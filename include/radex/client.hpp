#ifndef __RADEX_CLIENT_HPP__
#define __RADEX_CLIENT_HPP__

#if defined(__has_include)
#if __has_include("radex/build_config.hpp")
#include "radex/build_config.hpp"
#endif
#else
#error "RaDex requires __has_include support. This typically means that a newer compiler is needed"
#endif

#if !defined(RADEX_HAS_DRAGON) || !defined(RADEX_HAS_SMARTREDIS)
#error "RaDex backend configuration missing. Include radex/build_config.hpp or define RADEX_HAS_DRAGON and RADEX_HAS_SMARTREDIS before including radex/client.hpp."
#endif

#include "radex/client_base.hpp"
#include "radex/handles.hpp"
#include "radex/dragon.hpp"
#include "radex/smartredis.hpp"

#endif
