#include "radex/dragon.hpp"

#include <cstdint>
#include <cstdlib>
#include <memory>
#include <stdexcept>

#include "dragon/serializable.hpp"

namespace {

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

namespace radex::drg::ddict {

Client::Client() : Client(_ddict_from_radex_env()) {}

Client::Client(dragon::DDict<dragon::Serializable, dragon::Serializable> ddict)
    : ddict{ddict} {}

Client::Client(const char *descriptor, const timespec_t *timeout)
    : ddict{descriptor, timeout} {}

bool Client::contains(const std::string &key) {
    dragon::SerializableString key_(key);
    return ddict.contains(key_);
}


void Client::put_bytes(const std::string &key, const void *bytes,
                       detail::MetaInt length) {
    // FIXME: Gross const cast needed -- check with Kent!!
    auto ptr = static_cast<std::uint8_t *>(const_cast<void *>(bytes));

    SerializableString key_{key};
    SerializableByteBuffer buf{length, ptr};

    ddict[key_] = buf;
}

radex::detail::BytesBuffer Client::get_bytes(const std::string &key) {
    SerializableString key_{key};
    SerializableByteBuffer buf = ddict[key_];

    std::uint8_t *ptr = buf.getPtr();
    auto uniq = std::unique_ptr<std::uint8_t[]>(ptr);
    auto len = buf.getSize();

    return {std::move(uniq), len};
}

} // namespace radex::drg::ddict
