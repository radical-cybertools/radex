#include "radex/dragon.hpp"
#include "radex/constants.hpp"

#include <cstdint>
#include <cstdlib>
#include <memory>
#include <stdexcept>
#include <utility>

#if RADEX_HAS_DRAGON
#include "dragon/serializable.hpp"
#endif

#if RADEX_HAS_DRAGON
namespace {

using DDict = dragon::DDict<dragon::Serializable, dragon::Serializable>;

void _validate_ddict(DDict &ddict_ref) {

    if (!ddict_ref.wait_for_keys()) {
        throw std::runtime_error(
            "The DDict was not created with `wait_for_keys` enabled. "
            "Check that the correct serialized DDict was passed to this "
            "application."
        );
    }
}

DDict _ddict_from_radex_env() {

    const char *serialized_ddict = getenv(RADEX_STORE_VAR.c_str());
    if (!serialized_ddict) {
        throw std::invalid_argument(RADEX_STORE_VAR + " was not set.");
    }

    unsigned int timeout_seconds = RADEX_DEFAULT_CONNECTION_TIMEOUT_SECONDS;
    const char *timeout_str = getenv(RADEX_CONNECTION_TIMEOUT_VAR.c_str());
    if (timeout_str) {
        timeout_seconds = (unsigned int)std::stoul(timeout_str);
    }
    timespec_t timeout{timeout_seconds, 0};

    return DDict{serialized_ddict, &timeout};
}


} // namespace

namespace radex::drg::ddict {

// For now, the validation happens after teh ddict because of a weird problem
// which seems to originate from copy/move semantics with Dragon DDict.
Client::Client() : ddict{_ddict_from_radex_env()} {
    _validate_ddict(ddict);
}

Client::Client(dragon::DDict<dragon::Serializable, dragon::Serializable> ddict)
    : ddict{ddict} {
    _validate_ddict(this->ddict);
}

Client::Client(const char *descriptor, const timespec_t *timeout)
    : ddict{descriptor, timeout} {
    _validate_ddict(ddict);
}

bool Client::contains(std::string_view key) {
    dragon::SerializableString key_(std::string{key});
    return ddict.contains(key_);
}

void Client::put_bytes(std::string_view key, const void *bytes,
                       detail::MetaInt length) {
    // FIXME: Gross const cast needed -- check with Kent!!
    auto ptr = static_cast<std::uint8_t *>(const_cast<void *>(bytes));

    SerializableString key_{std::string{key}};
    SerializableByteBuffer buf{length, ptr};

    ddict[key_] = buf;
}

detail::BytesBuffer Client::wait_for_bytes(std::string_view key,
                                           std::chrono::milliseconds timeout) {
    // TODO: Implement this when Dragon supports command-level timeout
    if(!dormant_timeout_warning_triggered) {
        std::cerr
            << "The timeout for individual get commands has not been implemented. "
            "Using the stored value from initialization"
            << std::endl;

        dormant_timeout_warning_triggered = true;
    }
    SerializableString key_{std::string{key}};
    SerializableByteBuffer buf = ddict[key_];

    std::uint8_t *ptr = buf.getPtr();
    auto uniq = std::unique_ptr<std::uint8_t[]>(ptr);
    auto len = buf.getSize();

    return {std::move(uniq), len};
}

radex::detail::BytesBuffer Client::get_bytes(std::string_view key) {
    const std::chrono::milliseconds fast_timeout{1};
    // TODO: Check if/when Dragon can support bypassing wait for keys
    if (!contains(key)) {
        std::runtime_error("Key does not exist in the DDict: " + std::string(key));
    }
    return wait_for_bytes(key, fast_timeout);
}
} // namespace radex::drg::ddict
#else
namespace {

 void _dragon_disabled() {
    throw std::runtime_error(
        "radex was built without Dragon backend support. "
        "Rebuild with -DBUILD_DRAGON=ON to enable radex::drg::ddict::Client."
    );
}

} // namespace

namespace radex::drg::ddict {

Client::Client() { _dragon_disabled(); }

Client::Client(const char *descriptor, const timespec_t *timeout) {
    (void)descriptor;
    (void)timeout;
    _dragon_disabled();
}

bool Client::contains(std::string_view key) {
    (void)key;
    _dragon_disabled();
}

void Client::put_bytes(std::string_view key, const void *bytes,
                       detail::MetaInt length) {
    (void)key;
    (void)bytes;
    (void)length;
    _dragon_disabled();
}

detail::BytesBuffer Client::wait_for_bytes(std::string_view key,
                                           std::chrono::milliseconds timeout) {
    (void)key;
    (void)timeout;
    _dragon_disabled();
}

radex::detail::BytesBuffer Client::get_bytes(std::string_view key) {
    (void)key;
    _dragon_disabled();
}

} // namespace radex::drg::ddict
#endif
