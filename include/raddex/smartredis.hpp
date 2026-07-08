#ifndef __RADDEX_SMARTREDIS_HPP__
#define __RADDEX_SMARTREDIS_HPP__

#include "raddex/client.hpp"
#include "raddex/constants.hpp"

#include <client.h>

#include <cstdint>
#include <memory>
#include <string>

namespace raddex::redis::smartredis {

class Client : public IClient {
  private:
    SmartRedis::Client client;

  public:
    Client();
    Client(const std::string& logger_name);

    Client(const Client &other) = delete;
    Client(Client &&other) = default;
    Client &operator=(const Client &other) = delete;
    Client &operator=(Client &&other) = default;
    ~Client() = default;

    bool contains(const std::string &key) override;
    void put_bytes(const std::string &key, const void *bytes,
                   detail::MetaInt length) override;
    std::unique_ptr<std::uint8_t[]> get_bytes(const std::string &key) override;
};

} // namespace raddex::redis::smartredis

#endif
