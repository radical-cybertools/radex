#ifndef __RADEX_DRAGON_HPP__
#define __RADEX_DRAGON_HPP__

#include "radex/build_config.hpp"
#include "radex/client_base.hpp"
#include "radex/detail/bytes_buffer.hpp"
#include "radex/detail/types.hpp"

#ifdef RADEX_HAS_DRAGON
#include <dragon/ddict.h>
#endif

#include <chrono>
#include <ctime>
#include <memory>
#include <mutex>
#include <string_view>

namespace radex::drg::ddict {

#ifdef RADEX_HAS_DRAGON
/// RaDex client backed by a Dragon Distributed Dictionary (DDict).
///
/// Thread contract. A client attaches to the dictionary once and owns that
/// attachment. Dragon keeps per-attachment state (request tags, manager
/// connections, response channels) that two calls must not use at once, so
/// a client runs one call at a time, whichever threads make the calls: calls
/// on one client from several threads are serialized by the client's mutex.
/// Calls on different clients run concurrently, so a thread that should not
/// wait for other threads' calls needs a client of its own. Attaching is
/// serialized process-wide.
///
/// Every call makes its own Dragon requests, gives each one a key that no
/// other request in the process uses, and finalizes a request that failed
/// before raising. Dragon 0.15.0 keys its process-wide request map by a
/// descriptor that its own C++ API leaves uninitialized, so a request that
/// failed stayed in the map and failed every later request that happened to
/// reuse its key.
class Client : public IClient {
  private:
    dragonDDictDescr_t ddict{};
    timespec timeout_value{};
    bool has_timeout = false;
    std::unique_ptr<std::mutex> mutex = std::make_unique<std::mutex>();

    /// Dragon's timeout for each operation; null means none.
    const timespec *timeout() const {
        return has_timeout ? &timeout_value : nullptr;
    }

    void attach(const char *descriptor, const timespec *timeout);
    bool contains_unlocked(std::string_view key);
    detail::BytesBuffer get_unlocked(std::string_view key);

    void delete_key(std::string_view key) override;

    bool dormant_timeout_warning_triggered = false;

  public:
    /// Attach using a descriptor/timeout read from the environment.
    Client();
    /// @param descriptor A serialized DDict descriptor to attach to.
    /// @param timeout Timeout for attaching to the DDict, and for each of
    ///     Dragon's operations within a call.
    Client(const char *descriptor, const timespec *timeout);

    Client(const Client &other) = delete;
    Client(Client &&other) = default;
    Client &operator=(const Client &other) = delete;
    Client &operator=(Client &&other) = default;
    ~Client() = default;

    bool contains(std::string_view key) override;
    detail::BytesBuffer
    wait_for_bytes(std::string_view key,
                   std::chrono::milliseconds timeout) override;
    void put_bytes(std::string_view key, const void *bytes,
                   detail::MetaInt length) override;
    radex::detail::BytesBuffer get_bytes(std::string_view key) override;
};
#else
/// Placeholder used when RaDex was built without Dragon support
/// (`BUILD_DRAGON=OFF`).
class Client : public radex::unsupported_backend::Client {
  public:
    Client();
    Client(const char *descriptor, const timespec *timeout);
};
#endif

} // namespace radex::drg::ddict

#endif
