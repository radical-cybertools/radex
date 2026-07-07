#ifndef __RADDEX_DRAGON_HPP__
#define __RADDEX_DRAGON_HPP__

#include "raddex/client.hpp"
#include "raddex/constants.hpp"

#include <dragon/dictionary.hpp>
#include <dragon/serializable.hpp>
#include <string>

namespace raddex::drg::ddict {

class Client : public IClient {
  private:
    dragon::DDict<dragon::Serializable, dragon::Serializable> ddict;

    Client(dragon::DDict<dragon::Serializable, dragon::Serializable> ddict);

  public:
    Client();
    Client(const char *descriptor, const timespec_t *timeout);

    Client(const Client &other) = delete;
    Client(Client &&other) = default;
    Client &operator=(const Client &other) = delete;
    Client &operator=(Client &&other) = default;
    ~Client() = default;

    bool contains(const std::string &key) override;
    void put_bytes(const std::string &key, const void *bytes,
                   detail::MetaInt length) override;
    raddex::detail::BytesBuffer get_bytes(const std::string &key) override;
};

} // namespace raddex::drg::ddict

#endif
