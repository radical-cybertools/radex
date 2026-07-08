#include "raddex/smartredis.hpp"
#include "raddex/constants.hpp"

#include <cstdlib>
#include <configoptions.h>
#include <memory>
#include <stdexcept>
#include <string>

namespace raddex::redis::smartredis {

Client::Client() {
    auto opts = SmartRedis::ConfigOptions::create_from_environment("");

    const char *radex_ssdb = getenv(RADEX_STORE_VAR.c_str());
    if (radex_ssdb) {
        opts->override_string_option("SSDB", radex_ssdb);
    } else {
        throw std::invalid_argument(RADEX_STORE_VAR + " has not been set.");
    }

    const char *radex_db_type = getenv(RADEX_STORE_OPTS_VAR.c_str());
    if (radex_db_type) {
        opts->override_string_option("SR_DB_TYPE", radex_db_type);
    } else {
        throw std::invalid_argument(RADEX_STORE_OPTS_VAR + " has not been set.");
    }

    const char *radex_conn_timeout = getenv(RADEX_CONNECTION_TIMEOUT_VAR.c_str());
    if (radex_conn_timeout) {
        opts->override_integer_option("SR_CONN_TIMEOUT", std::stoll(radex_conn_timeout));
    }

    const char *logger = getenv("SMARTREDIS_LOGGER_NAME");

    // Initialize client with ConfigOptions
    client = SmartRedis::Client(opts.get(), logger ? logger : "radex-client");
}

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
