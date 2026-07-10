#include "raddex/dragon.hpp"

#include <cstdint>
#include <cstdlib>
#include <memory>
#include <stdexcept>

#include "dragon/serializable.hpp"

namespace {

/// Build a Dragon distributed dictionary client from RaDeX environment variables.
///
/// Expects `RADEX_STORE_VAR` to contain a serialized DDict descriptor and
/// optionally `RADEX_CONNECTION_TIMEOUT_VAR` to override the connection timeout.
/// These variables are expected to be set from a RHAPSODY-backed workflow.
dragon::DDict<dragon::Serializable, dragon::Serializable> _ddict_from_radex_env() {

    const char *serialized_ddict = getenv(RADEX_STORE_VAR.c_str());
    if (!serialized_ddict) {
        throw std::invalid_argument(RADEX_STORE_VAR + " was not set.");
    }

    unsigned int timeout_seconds = RADEX_DEFAULT_CONNECTION_TIMEOUT_SECONDS;
    const char *timeout_str = getenv(RADEX_CONNECTION_TIMEOUT_VAR.c_str());
    if (timeout_str) {
        timeout_seconds = (unsigned int) std::stoul(timeout_str);
    }
    timespec_t timeout{timeout_seconds, 0};

    return dragon::DDict<dragon::Serializable, dragon::Serializable>{serialized_ddict, &timeout};

}

} // namespace

namespace raddex::drg::ddict {

/// Construct a client using Dragon connection information stored in environment variables.
Client::Client() : Client(_ddict_from_radex_env()) {}

/// Construct a client from an existing Dragon DDict.
Client::Client(dragon::DDict<dragon::Serializable, dragon::Serializable> ddict)
    : ddict{ddict} {}

/// Construct a client from a serialized descriptor and timeout.
Client::Client(const char *descriptor, const timespec_t *timeout)
    : ddict{descriptor, timeout} {}

/// Check whether a key exists in the backing Dragon dictionary.
bool Client::contains(const std::string &key) {
    dragon::SerializableString key_(key);
    return ddict.contains(key_);
}


/// Store a raw byte buffer under the provided key.
///
/// The buffer is written with the provided byte length.
void Client::put_bytes(const std::string &key, const void *bytes,
                       detail::MetaInt length) {
    // FIXME: Gross const cast needed -- check with Kent!!
    auto ptr = static_cast<std::uint8_t *>(const_cast<void *>(bytes));

    SerializableString key_{key};
    SerializableByteBuffer buf{length, ptr};

    ddict[key_] = buf;
}

/// Retrieve the raw byte buffer associated with the given key.
///
/// Ownership of the returned buffer is transferred to the caller.
std::unique_ptr<std::uint8_t[]> Client::get_bytes(const std::string &key) {
    SerializableString key_{key};
    SerializableByteBuffer buf = ddict[key_];

    std::uint8_t *ptr = buf.getPtr();
    auto uniq = std::unique_ptr<std::uint8_t[]>(ptr);
    auto len = buf.getSize();

    return {std::move(uniq), len};
}

} // namespace raddex::drg::ddict
