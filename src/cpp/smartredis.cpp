#include "radex/smartredis.hpp"
#include "radex/constants.hpp"

#include <cstdlib>
#include <memory>
#include <stdexcept>
#include <string>

#if RADEX_HAS_SMARTREDIS
#include <configoptions.h>
#endif

#if RADEX_HAS_SMARTREDIS
namespace {

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
        throw std::invalid_argument(RADEX_STORE_OPTS_VAR +
                                    " has not been set.");
    }

    const char *radex_conn_timeout =
        getenv(RADEX_CONNECTION_TIMEOUT_VAR.c_str());
    if (radex_conn_timeout) {
        opts->override_integer_option("SR_CONN_TIMEOUT",
                                      std::stoll(radex_conn_timeout));
    }

    return opts;
}

std::string _logger_name_from_env() {
    const char *logger = getenv("SMARTREDIS_LOGGER_NAME");
    return logger ? logger : "radex-client";
}
} // namespace

namespace radex::redis::smartredis {

Client::Client()
    : Client(_configOptions_from_radex_env(), _logger_name_from_env()) {}

Client::Client(std::unique_ptr<SmartRedis::ConfigOptions> options,
               std::string_view logger_name)
    : client{options.get(), std::string{logger_name}} {}

Client::Client(std::string_view logger_name)
    : client{std::string{logger_name}} {}

bool Client::contains(std::string_view key) {
    return client.key_exists(std::string{key});
}

void Client::put_bytes(std::string_view key, const void *bytes,
                       detail::MetaInt length) {
    client.put_bytes(std::string{key}, bytes, length);
}

radex::detail::BytesBuffer Client::get_bytes(std::string_view key) {
    void *out_buf = nullptr;
    detail::MetaInt out_n_bytes = 0;
    client.get_bytes(std::string{key}, out_buf, out_n_bytes);
    auto ptr = static_cast<std::uint8_t *>(out_buf);
    auto uniq = std::unique_ptr<std::uint8_t[]>(ptr);
    return {std::move(uniq), out_n_bytes};
}

} // namespace radex::redis::smartredis
#else
namespace {

void _smartredis_disabled() {
    throw std::runtime_error(
        "radex was built without SmartRedis backend support. "
        "Rebuild with -DBUILD_SMARTREDIS=ON to enable "
        "radex::redis::smartredis::Client."
    );
}

} // namespace

namespace radex::redis::smartredis {

Client::Client() { _smartredis_disabled(); }

Client::Client(std::string_view logger_name) {
    (void)logger_name;
    _smartredis_disabled();
}

bool Client::contains(std::string_view key) {
    (void)key;
    _smartredis_disabled();
}

void Client::put_bytes(std::string_view key, const void *bytes,
                       detail::MetaInt length) {
    (void)key;
    (void)bytes;
    (void)length;
    _smartredis_disabled();
}

radex::detail::BytesBuffer Client::get_bytes(std::string_view key) {
    (void)key;
    _smartredis_disabled();
}

} // namespace radex::redis::smartredis
#endif
