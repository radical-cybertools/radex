#ifndef __RADEX_SMARTREDIS_HPP__
#define __RADEX_SMARTREDIS_HPP__

#include "radex/client.hpp"

#include <client.h>

#include <string_view>

namespace radex::redis::smartredis {

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

} // namespace radex::redis::smartredis

#endif
