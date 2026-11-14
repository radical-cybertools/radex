#include "radex/dragon.hpp"
#include "radex/constants.hpp"
#include "radex/detail/bytes_buffer.hpp"
#include "radex/detail/types.hpp"
#include "radex/exceptions.hpp"

#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

#ifdef RADEX_HAS_DRAGON
#include <dragon/dictionary.hpp>
#include <dragon/exceptions.hpp>
#include <dragon/serializable.hpp>

namespace {

/// Serializes attaching, process-wide: Dragon creates its process-wide maps
/// of dictionaries and requests on first use, without a lock.
std::mutex attach_mutex;
bool requests_ready = false; // guarded by attach_mutex

/// Keys for Dragon's process-wide request map. Dragon 0.15.0 uses the key in
/// the descriptor it is given and never sets one; Dragon's own C++ API passes
/// an uninitialized descriptor, so the key was whatever its stack held.
std::atomic<std::uint64_t> next_request_key{0x5241444558000001ULL};

/// Raise a Dragon failure as a RaDex error, with Dragon's own traceback.
[[noreturn]] void raise_dragon(dragonError_t rc, std::string_view what,
                               std::string_view key) {
    std::string msg = "Dragon could not ";
    msg += what;
    if (!key.empty()) {
        msg += " (key `";
        msg += key;
        msg += "`)";
    }
    msg += ": ";
    msg += dragon_get_rc_string(rc);
    char *traceback = dragon_getlasterrstr();
    if (traceback != nullptr) {
        if (*traceback != '\0') {
            msg += "\n";
            msg += traceback;
        }
        std::free(traceback);
    }
    if (rc == DRAGON_TIMEOUT) {
        throw radex::TimeoutError(msg);
    }
    if (rc == DRAGON_KEY_NOT_FOUND) {
        throw radex::KeyNotFoundError(msg);
    }
    throw radex::Error(msg);
}

void check(dragonError_t rc, std::string_view what, std::string_view key) {
    if (rc != DRAGON_SUCCESS) {
        raise_dragon(rc, what, key);
    }
}

/// One Dragon request, with a key of its own, finalized when it goes out of
/// scope if `finalize` was not reached: a request that failed must not stay
/// in Dragon's request map.
class Request {
  public:
    Request(dragonDDictDescr_t *ddict, std::string_view key) : key(key) {
        req._idx = next_request_key.fetch_add(1, std::memory_order_relaxed);
        check(dragon_ddict_create_request(ddict, &req), "create a request",
              key);
        open = true;
    }
    Request(const Request &) = delete;
    Request &operator=(const Request &) = delete;
    ~Request() {
        if (open) {
            // After an error: release what Dragon can release. Its error is
            // not the one being raised, so it is dropped.
            (void)dragon_ddict_finalize_request(&req);
        }
    }

    dragonDDictRequestDescr_t *get() { return &req; }

    /// Write the key, as Dragon's C++ DDict does: a Serializable string.
    void send_key(const timespec *timeout) {
        dragonFLISendHandleDescr_t sendh;
        check(dragon_ddict_request_key_sendh(&req, &sendh),
              "get the request's key handle", key);
        dragon::Serializable(dragon::SerializableString(std::string{key}))
            .serialize(&sendh, KEY_HINT, true, timeout);
    }

    void finalize() {
        open = false;
        check(dragon_ddict_finalize_request(&req), "finalize the request", key);
    }

  private:
    dragonDDictRequestDescr_t req{};
    std::string_view key;
    bool open = false;
};

/// Run `body`, raising Dragon's C++ errors (from serializing and
/// deserializing) as RaDex errors.
template <typename F>
auto translating(std::string_view what, std::string_view key, F &&body) {
    try {
        return body();
    } catch (const dragon::DragonError &e) {
        raise_dragon(e.rc(), what, key);
    }
}

void validate(dragonDDictDescr_t *ddict) {
    bool waits = false;
    check(dragon_ddict_wait_for_keys(ddict, &waits),
          "read the dictionary's wait_for_keys setting", "");
    if (!waits) {
        throw std::runtime_error(
            "The DDict was not created with `wait_for_keys` enabled. "
            "Check that the correct serialized DDict was passed to this "
            "application.");
    }
}

} // namespace

namespace radex::drg::ddict {

void Client::attach(const char *descriptor, const timespec *timeout) {
    if (timeout != nullptr) {
        timeout_value = *timeout;
        has_timeout = true;
    }
    std::lock_guard<std::mutex> lock{attach_mutex};
    check(dragon_ddict_attach(descriptor, &ddict,
                              const_cast<timespec *>(this->timeout())),
          "attach to the dictionary", "");
    validate(&ddict);
    if (!requests_ready) {
        // Make Dragon create its request map now, while no other thread can
        // make a request: every client is attached under this lock first.
        contains_unlocked("radex::first-request");
        requests_ready = true;
    }
}

Client::Client() {
    const char *serialized_ddict = getenv(RADEX_STORE_VAR.c_str());
    if (!serialized_ddict) {
        throw std::invalid_argument(RADEX_STORE_VAR + " was not set.");
    }
    unsigned int timeout_seconds = RADEX_DEFAULT_CONNECTION_TIMEOUT_SECONDS;
    const char *timeout_str = getenv(RADEX_CONNECTION_TIMEOUT_VAR.c_str());
    if (timeout_str) {
        timeout_seconds = (unsigned int)std::stoul(timeout_str);
    }
    timespec timeout{timeout_seconds, 0};
    attach(serialized_ddict, &timeout);
}

Client::Client(const char *descriptor, const timespec *timeout) {
    attach(descriptor, timeout);
}

bool Client::contains_unlocked(std::string_view key) {
    Request req{&ddict, key};
    translating("send a contains", key, [&] { req.send_key(timeout()); });
    dragonError_t rc = dragon_ddict_contains(req.get());
    if (rc != DRAGON_SUCCESS && rc != DRAGON_KEY_NOT_FOUND) {
        raise_dragon(rc, "check whether the key exists", key);
    }
    req.finalize();
    return rc == DRAGON_SUCCESS;
}

detail::BytesBuffer Client::get_unlocked(std::string_view key) {
    Request req{&ddict, key};
    translating("send a get", key, [&] { req.send_key(timeout()); });
    check(dragon_ddict_get(req.get()), "get the value", key);
    dragonFLIRecvHandleDescr_t recvh;
    check(dragon_ddict_request_recvh(req.get(), &recvh),
          "get the request's receive handle", key);
    uint64_t hint = 0;
    dragon::SerializableByteBuffer buf =
        translating("read the value", key, [&] {
            return dragon::Serializable::deserialize(&recvh, &hint, timeout())
                .asSerializableByteBuffer();
        });
    // Ours to free from here, whatever happens next.
    auto uniq = std::unique_ptr<std::uint8_t[]>(buf.getPtr());
    if (hint != VALUE_HINT) {
        raise_dragon(DRAGON_INVALID_OPERATION, "read a value (wrong hint)",
                     key);
    }
    req.finalize();
    return {std::move(uniq), buf.getSize()};
}

bool Client::contains(std::string_view key) {
    std::lock_guard<std::mutex> lock{*mutex};
    return contains_unlocked(key);
}

void Client::delete_key(std::string_view key) {
    std::lock_guard<std::mutex> lock{*mutex};
    Request req{&ddict, key};
    translating("send a delete", key, [&] { req.send_key(timeout()); });
    check(dragon_ddict_pop(req.get()), "delete", key);
    dragonFLIRecvHandleDescr_t recvh;
    check(dragon_ddict_request_recvh(req.get(), &recvh),
          "get the request's receive handle", key);
    uint64_t hint = 0;
    // A delete is a pop: it returns the deleted value in a buffer that Dragon
    // allocates with `malloc` and leaves to the caller to free.
    dragon::SerializableByteBuffer buf =
        translating("read the deleted value", key, [&] {
            return dragon::Serializable::deserialize(&recvh, &hint, timeout())
                .asSerializableByteBuffer();
        });
    std::free(buf.getPtr());
    req.finalize();
}

void Client::put_bytes(std::string_view key, const void *bytes,
                       detail::MetaInt length) {
    std::lock_guard<std::mutex> lock{*mutex};
    // Dragon's byte buffer takes a non-const pointer; it only reads it.
    auto ptr = static_cast<std::uint8_t *>(const_cast<void *>(bytes));
    Request req{&ddict, key};
    translating("send a put", key, [&] { req.send_key(timeout()); });
    check(dragon_ddict_put(req.get()), "put the value", key);
    dragonFLISendHandleDescr_t sendh;
    check(dragon_ddict_request_value_sendh(req.get(), &sendh),
          "get the request's value handle", key);
    translating("send the value", key, [&] {
        dragon::Serializable(dragon::SerializableByteBuffer(length, ptr))
            .serialize(&sendh, VALUE_HINT, false, this->timeout());
    });
    req.finalize();
}

detail::BytesBuffer Client::wait_for_bytes(std::string_view key,
                                           std::chrono::milliseconds timeout) {
    std::lock_guard<std::mutex> lock{*mutex};
    // TODO: Implement this when Dragon supports command-level timeout
    if (!dormant_timeout_warning_triggered) {
        std::cerr << "The timeout for individual get commands has not been "
                     "implemented. "
                     "Using the stored value from initialization"
                  << std::endl;

        dormant_timeout_warning_triggered = true;
    }
    return get_unlocked(key);
}

radex::detail::BytesBuffer Client::get_bytes(std::string_view key) {
    std::lock_guard<std::mutex> lock{*mutex};
    // TODO: Check if/when Dragon can support bypassing wait for keys
    if (!contains_unlocked(key)) {
        throw radex::KeyNotFoundError("Key does not exist in the DDict: " +
                                      std::string(key));
    }
    return get_unlocked(key);
}

} // namespace radex::drg::ddict
#else
namespace radex::drg::ddict {

Client::Client()
    : radex::unsupported_backend::Client("Dragon", "BUILD_DRAGON") {}

Client::Client(const char *descriptor, const timespec *timeout)
    : radex::unsupported_backend::Client("Dragon", "BUILD_DRAGON") {}

} // namespace radex::drg::ddict
#endif
