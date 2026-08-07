#ifndef __RADEX_SMARTREDIS_HPP__
#define __RADEX_SMARTREDIS_HPP__

#include "radex/client.hpp"

#if RADEX_HAS_SMARTREDIS
#include <client.h>
#endif

#include <string_view>

namespace radex::redis::smartredis {

#if RADEX_HAS_SMARTREDIS
class Client : public IClient {
  private:
    SmartRedis::Client client;
    Client(std::unique_ptr<SmartRedis::ConfigOptions> options,
           std::string_view logger_name);

  public:
    Client();
    Client(std::string_view logger_name);

    Client(const Client &other) = delete;
    Client(Client &&other) = default;
    Client &operator=(const Client &other) = delete;
    Client &operator=(Client &&other) = default;
    ~Client() = default;

    bool contains(std::string_view key) override;
    void put_bytes(std::string_view key, const void *bytes,
                   detail::MetaInt length) override;
    radex::detail::BytesBuffer get_bytes(std::string_view key) override;
};
#else
class Client : public detail::UnsupportedBackendClient {
  public:
    Client();
    Client(std::string_view logger_name);
};
#endif

} // namespace radex::redis::smartredis

#endif
