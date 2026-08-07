#ifndef __RADEX_DRAGON_HPP__
#define __RADEX_DRAGON_HPP__

#include "radex/client.hpp"

#ifndef RADEX_HAS_DRAGON
#define RADEX_HAS_DRAGON 0
#endif

#if RADEX_HAS_DRAGON
#include <dragon/dictionary.hpp>
#include <dragon/serializable.hpp>
#else
#include <ctime>
using timespec_t = struct timespec;
#endif
#include <string_view>

namespace radex::drg::ddict {

#if RADEX_HAS_DRAGON
class Client : public IClient {
  private:
    dragon::DDict<dragon::Serializable, dragon::Serializable> ddict;

    Client(dragon::DDict<dragon::Serializable, dragon::Serializable> ddict);

    bool dormant_timeout_warning_triggered = false;

  public:
    Client();
    Client(const char *descriptor, const timespec_t *timeout);

    Client(const Client &other) = delete;
    Client(Client &&other) = default;
    Client &operator=(const Client &other) = delete;
    Client &operator=(Client &&other) = default;
    ~Client() = default;

    bool contains(std::string_view key) override;
    detail::BytesBuffer wait_for_bytes(std::string_view key,
                                       std::chrono::milliseconds timeout) override;
    void put_bytes(std::string_view key, const void *bytes,
                   detail::MetaInt length) override;
    radex::detail::BytesBuffer get_bytes(std::string_view key) override;
};
#else
class Client : public detail::UnsupportedBackendClient {
  public:
    Client();
    Client(const char *descriptor, const timespec_t *timeout);
};
#endif

} // namespace radex::drg::ddict

#endif
