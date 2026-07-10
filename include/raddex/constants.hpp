#ifndef __RADDEX_CONSTANTS_HPP__
#define __RADDEX_CONSTANTS_HPP__

#include <string>

/// Environment variable containing backend connection information.
inline const std::string RADEX_STORE_VAR = "RADEX_STORE";

/// Environment variable containing backend-specific option values.
inline const std::string RADEX_STORE_OPTS_VAR = "RADEX_STORE_OPTS";

/// Environment variable optionally overriding backend connection timeout.
inline const std::string RADEX_CONNECTION_TIMEOUT_VAR = "RADEX_CONNECTION_TIMEOUT";

/// Default connection timeout in seconds when no override is provided.
constexpr unsigned int RADEX_DEFAULT_CONNECTION_TIMEOUT_SECONDS = 5;

#endif