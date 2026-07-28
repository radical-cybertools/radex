#ifndef __RADEX_CONSTANTS_HPP__
#define __RADEX_CONSTANTS_HPP__

#include <string>

inline const std::string RADEX_STORE_VAR = "RADEX_STORE";
inline const std::string RADEX_STORE_OPTS_VAR = "RADEX_STORE_OPTS";
inline const std::string RADEX_CONNECTION_TIMEOUT_VAR = "RADEX_CONNECTION_TIMEOUT";
constexpr unsigned int RADEX_DEFAULT_CONNECTION_TIMEOUT_SECONDS = 5;

inline const std::string RADEX_POLL_INTERVAL_VAR = "RADEX_POLL_INTERVAL";
constexpr unsigned int RADEX_DEFAULT_POLL_INTERVAL_SECONDS = 1;

#endif
