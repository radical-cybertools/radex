#ifndef __RADDEX_DRAGON_HPP__
#define __RADDEX_DRAGON_HPP__

#include "raddex/client.hpp"
#include "raddex/constants.hpp"

#include <dragon/dictionary.hpp>
#include <dragon/serializable.hpp>
#include <string>

namespace raddex::drg::ddict {

/// Dragon DDict-backed implementation of the RaDeX client interface.
class Client : public IClient {
  private:
    /// Dragon distributed dictionary handle.
    dragon::DDict<dragon::Serializable, dragon::Serializable> ddict;

    /// Construct from an existing Dragon DDict handle.
    Client(dragon::DDict<dragon::Serializable, dragon::Serializable> ddict);

  public:
    /// Construct using information in environment variables.
    Client();

    /// Construct from a serialized Dragon descriptor and timeout.
    ///
    /// @param descriptor Serialized DDict descriptor.
    /// @param timeout Dragon timeout used for connection operations.
    Client(const char *descriptor, const timespec_t *timeout);

    Client(const Client &other) = delete;
    Client(Client &&other) = default;
    Client &operator=(const Client &other) = delete;
    Client &operator=(Client &&other) = default;
    ~Client() = default;

    /// Return true when the provided key exists in the DDict store.
    bool contains(const std::string &key) override;

    /// Store raw bytes in the DDict store under the provided key.
    void put_bytes(const std::string &key, const void *bytes,
                   detail::MetaInt length) override;

    /// Retrieve raw bytes for the provided key from the DDict store.
    std::unique_ptr<std::uint8_t[]> get_bytes(const std::string &key) override;
};

} // namespace raddex::drg::ddict

#endif
