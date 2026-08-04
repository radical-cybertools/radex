#include "radex/dragon.hpp"
#include "radex/constants.hpp"

#include <cstdint>
#include <cstdlib>
#include <memory>
#include <stdexcept>
#include <utility>

#include "dragon/serializable.hpp"

namespace {

using DDict = dragon::DDict<dragon::Serializable, dragon::Serializable>;

DDict _validate_ddict(DDict ddict) {

    if (!ddict.wait_for_keys()) {
        throw std::runtime_error(
            "The DDict was not created with `wait_for_keys` enabled. "
            "Check that the correct serialized DDict was passed to this "
            "application."
        );
    }
    return ddict;
}

DDict _ddict_from_radex_env() {

    const char *serialized_ddict = getenv(RADEX_STORE_VAR.c_str());
    if (!serialized_ddict) {
        throw std::invalid_argument(RADEX_STORE_VAR + " was not set.");
    }

    unsigned int timeout_seconds = RADEX_DEFAULT_CONNECTION_TIMEOUT_SECONDS;
    const char *timeout_str = getenv(RADEX_CONNECTION_TIMEOUT_VAR.c_str());
    if (timeout_str) {
        timeout_seconds = (unsigned int)std::stoul(timeout_str);
    }
    timespec_t timeout{timeout_seconds, 0};

    return DDict{serialized_ddict, &timeout};
}

DDict _ddict_from_descriptor(const char *descriptor, const timespec_t *timeout) {
    if (!descriptor) {
        throw std::invalid_argument("DDict descriptor must be specified.");
    }

    return DDict{descriptor, timeout};
}

} // namespace

namespace radex::drg::ddict {

Client::Client() : Client(_ddict_from_radex_env()) {}

Client::Client(dragon::DDict<dragon::Serializable, dragon::Serializable> ddict)
    : ddict{_validate_ddict(std::move(ddict))} {}

Client::Client(const char *descriptor, const timespec_t *timeout)
    : Client(_ddict_from_descriptor(descriptor, timeout)) {}

bool Client::contains(std::string_view key) {
    dragon::SerializableString key_(std::string{key});
    return ddict.contains(key_);
}

void Client::put_bytes(std::string_view key, const void *bytes,
                       detail::MetaInt length) {
    // FIXME: Gross const cast needed -- check with Kent!!
    auto ptr = static_cast<std::uint8_t *>(const_cast<void *>(bytes));

    SerializableString key_{std::string{key}};
    SerializableByteBuffer buf{length, ptr};

    ddict[key_] = buf;
}

detail::BytesBuffer Client::wait_for_bytes(std::string_view key,
                                           std::chrono::milliseconds timeout) {
    // TODO: Implement this when Dragon supports command-level timeout
    if(!dormant_timeout_warning_triggered) {
        std::cerr
            << "The timeout for individual get commands has not been implemented. "
            "Using the stored value from initialization"
            << std::endl;

        dormant_timeout_warning_triggered = true;
    }
    return get_bytes(key);
}

radex::detail::BytesBuffer Client::get_bytes(std::string_view key) {
    SerializableString key_{std::string{key}};
    SerializableByteBuffer buf = ddict[key_];

    std::uint8_t *ptr = buf.getPtr();
    auto uniq = std::unique_ptr<std::uint8_t[]>(ptr);
    auto len = buf.getSize();

    return {std::move(uniq), len};
}

} // namespace radex::drg::ddict
