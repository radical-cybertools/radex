#include "raddex/smartredis.hpp"

#include <memory>
#include <string>

namespace raddex::redis::smartredis {

Client::Client(const std::string &logger_name) : client{logger_name} {}

bool Client::contains(const std::string &key) { return client.key_exists(key); }

void Client::put_bytes(const std::string &key, const void *bytes,
                       detail::MetaInt length) {
    client.put_bytes(key, bytes, length);
}

std::unique_ptr<std::uint8_t[]> Client::get_bytes(const std::string &key) {
    void *out_buf = nullptr;
    detail::MetaInt out_n_bytes = 0;
    client.get_bytes(key, out_buf, out_n_bytes);
    auto ptr = static_cast<std::uint8_t *>(out_buf);
    return std::unique_ptr<std::uint8_t[]>(ptr);
}

} // namespace raddex::redis::smartredis
