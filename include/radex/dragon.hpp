#ifndef __RADEX_DRAGON_HPP__
#define __RADEX_DRAGON_HPP__

#include "radex/client.hpp"

#include <dragon/dictionary.hpp>
#include <dragon/serializable.hpp>
#include <string_view>

namespace radex::drg::ddict {

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

    bool contains(std::string_view key) override;
    void put_bytes(std::string_view key, const void *bytes,
                   detail::MetaInt length) override;
    radex::detail::BytesBuffer get_bytes(std::string_view key) override;
};

} // namespace radex::drg::ddict

#endif
