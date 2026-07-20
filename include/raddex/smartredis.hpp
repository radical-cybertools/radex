#ifndef __RADDEX_SMARTREDIS_HPP__
#define __RADDEX_SMARTREDIS_HPP__

#include "raddex/client.hpp"
#include "raddex/constants.hpp"

#include <client.h>

#include <string>

namespace raddex::redis::smartredis {

/// SmartRedis-backed implementation of the RaDeX client interface.
class Client : public IClient {
  private:
    /// Underlying SmartRedis client instance.
    SmartRedis::Client client;

    /// Construct from explicit SmartRedis options and logger name.
    Client(std::unique_ptr<SmartRedis::ConfigOptions> options,
           const std::string &logger_name);

  public:
    /// Construct using SmartRedis options resolved from the environment.
    Client();

    /// Construct using a caller-supplied logger name.
    Client(const std::string& logger_name);

    Client(const Client &other) = delete;
    Client(Client &&other) = default;
    Client &operator=(const Client &other) = delete;
    Client &operator=(Client &&other) = default;
    ~Client() = default;

    /// Return true when the provided key exists in Redis.
    bool contains(const std::string &key) override;

    /// Store raw bytes in Redis under the provided key.
    void put_bytes(const std::string &key, const void *bytes,
                   detail::MetaInt length) override;

    /// Retrieve raw bytes for the provided key from Redis.
    raddex::detail::BytesBuffer get_bytes(const std::string &key) override;
};

} // namespace raddex::redis::smartredis

#endif
