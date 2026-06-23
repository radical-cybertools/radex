#include "raddex/dragon.hpp"

#include <cstdint>
#include <memory>

#include "dragon/serializable.hpp"

namespace raddex::drg::ddict {

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

std::unique_ptr<std::uint8_t[]> Client::get_bytes(const std::string &key) {
    SerializableString key_{key};
    SerializableByteBuffer buf = ddict[key_];

    std::uint8_t *ptr = buf.getPtr();
    auto uniq = std::unique_ptr<std::uint8_t[]>(ptr);

    return uniq;
}

} // namespace raddex::drg::ddict
