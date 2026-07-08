#include "raddex/dragon.hpp"

#include <cstdint>
#include <cstdlib>
#include <memory>

#include "dragon/serializable.hpp"

namespace raddex::drg::ddict {

namespace {

time_t get_env_timeout_seconds() {
    const char *timeout_str = getenv(RADEX_CONNECTION_TIMEOUT_VAR.c_str());
    if (timeout_str) {
        return std::stol(timeout_str);
    }

    return RADEX_DEFAULT_CONNECTION_TIMEOUT_SECONDS;
}

} // namespace

Client::Client()
    : Client(getenv(RADEX_STORE_VAR.c_str()),
             timespec_t{get_env_timeout_seconds(), 0}) {}

Client::Client(dragon::DDict<dragon::Serializable, dragon::Serializable> ddict)
    : ddict{ddict} {}

Client::Client(const char *descriptor, timespec_t timeout)
    : ddict{descriptor, &timeout} {}

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

std::unique_ptr<std::uint8_t[]> Client::get_bytes(const std::string &key) {
    SerializableString key_{key};
    SerializableByteBuffer buf = ddict[key_];

    std::uint8_t *ptr = buf.getPtr();
    auto uniq = std::unique_ptr<std::uint8_t[]>(ptr);

    return uniq;
}

} // namespace raddex::drg::ddict
