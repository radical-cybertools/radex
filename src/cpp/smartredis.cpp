#include "raddex/smartredis.hpp"
#include "raddex/constants.hpp"

#include <cstdlib>
#include <configoptions.h>
#include <memory>
#include <stdexcept>
#include <string>

namespace {

/// Build SmartRedis configuration options from RaDeX environment variables.
///
/// Requires store endpoint and DB type variables; timeout is optional.
std::unique_ptr<SmartRedis::ConfigOptions> _configOptions_from_radex_env() {

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

    return opts;
}

std::string _logger_name_from_env() {
    const char *logger = getenv("SMARTREDIS_LOGGER_NAME");
    return logger ? logger : "radex-client";
}
}


namespace raddex::redis::smartredis {

/// Construct a SmartRedis-backed client information stored in environment variables.
Client::Client()
    : Client(_configOptions_from_radex_env(), _logger_name_from_env()) {}

/// Construct a client from explicit SmartRedis options and logger name.
Client::Client(std::unique_ptr<SmartRedis::ConfigOptions> options,
               const std::string &logger_name)
    : client{options.get(), logger_name} {}

/// Construct a client with the given logger and default SmartRedis settings.
Client::Client(const std::string &logger_name) : client{logger_name} {}

/// Check whether a key exists in the configured Redis backend.
bool Client::contains(const std::string &key) { return client.key_exists(key); }

/// Store a raw byte buffer in Redis under the supplied key.
void Client::put_bytes(const std::string &key, const void *bytes,
                       detail::MetaInt length) {
    client.put_bytes(key, bytes, length);
}

/// Fetch a raw byte buffer from Redis for the supplied key.
///
/// Ownership of the returned buffer is transferred to the caller.
std::unique_ptr<std::uint8_t[]> Client::get_bytes(const std::string &key) {
    void *out_buf = nullptr;
    detail::MetaInt out_n_bytes = 0;
    client.get_bytes(key, out_buf, out_n_bytes);
    auto ptr = static_cast<std::uint8_t *>(out_buf);
    auto uniq = std::unique_ptr<std::uint8_t[]>(ptr);
    return {std::move(uniq), out_n_bytes};
}

} // namespace raddex::redis::smartredis
