#ifndef __RADEX_DRAGON_HPP__
#define __RADEX_DRAGON_HPP__

#include "radex/client_base.hpp"
#include "radex/build_config.hpp"

#ifdef RADEX_HAS_DRAGON
#include <dragon/dictionary.hpp>
#include <dragon/serializable.hpp>
#endif
#include <ctime>
#include <string_view>

namespace radex::drg::ddict {

#ifdef RADEX_HAS_DRAGON
class Client : public IClient {
  private:
    dragon::DDict<dragon::Serializable, dragon::Serializable> ddict;

    Client(dragon::DDict<dragon::Serializable, dragon::Serializable> ddict);

    bool dormant_timeout_warning_triggered = false;

  public:
    Client();
    Client(const char *descriptor, const timespec *timeout);

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
class Client : public radex::unsupported_backend::Client {
  public:
    Client();
    Client(const char *descriptor, const timespec *timeout);
};
#endif

} // namespace radex::drg::ddict

#endif
