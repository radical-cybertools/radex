#ifndef __RADEX_SMARTREDIS_HPP__
#define __RADEX_SMARTREDIS_HPP__

#include "radex/client.hpp"

#ifndef RADEX_HAS_SMARTREDIS
#define RADEX_HAS_SMARTREDIS 0
#endif

#if RADEX_HAS_SMARTREDIS
#include <client.h>
#endif

#include <string_view>

namespace radex::redis::smartredis {

class Client : public IClient {
  private:
#if RADEX_HAS_SMARTREDIS
    SmartRedis::Client client;
    Client(std::unique_ptr<SmartRedis::ConfigOptions> options,
           std::string_view logger_name);
#endif

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
