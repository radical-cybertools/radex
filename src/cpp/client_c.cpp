#include "radex/macros/client_c_implementation_macros.hpp"
#include "radex/client_base.hpp"
#include "radex/dragon.hpp"
#include "radex/smartredis.hpp"
#include "radex/errno.h"
#include "radex/client_c.h"
#include "radex/handles_c.h"
#include <cstring>
#include <cstdio>
#include <cstdlib>

extern "C" {

radex_client_t radex_client_dragon_create(void) {
  try {
    auto* client = new radex::drg::ddict::Client();
    return static_cast<void*>(client);
  } catch (const radex::BackendUnavailableError&) {
    fprintf(stderr, "RaDex Error: RADEX_ERR_BACKEND_UNAVAILABLE\n");
    abort();
  } catch (const std::exception&) {
    fprintf(stderr, "RaDex Error: RADEX_ERR_UNKNOWN\n");
    abort();
  }
}

radex_client_t radex_client_smartredis_create(void) {
  try {
    auto* client = new radex::redis::smartredis::Client();
    return static_cast<void*>(client);
  } catch (const radex::BackendUnavailableError&) {
    fprintf(stderr, "RaDex Error: RADEX_ERR_BACKEND_UNAVAILABLE\n");
    abort();
  } catch (const std::exception&) {
    fprintf(stderr, "RaDex Error: RADEX_ERR_UNKNOWN\n");
    abort();
  }
}

int radex_client_destroy(radex_client_t client) {
  if (!client) return RADEX_ERR_UNKNOWN;
  try {
    auto* c = static_cast<radex::IClient*>(client);
    delete c;
    return RADEX_OK;
  } catch (const std::exception&) {
    return RADEX_ERR_UNKNOWN;
  }
}

/// Utility functions

int radex_client_contains(radex_client_t client_ptr, radex_incoming_handle_t* handle_ptr) {
  if (!client_ptr || !handle_ptr) return RADEX_ERR_UNKNOWN;
  auto* client = static_cast<radex::IClient*>(client_ptr);
  auto* handle = reinterpret_cast<radex::data::IncomingHandle*>(handle_ptr);
  try {
    bool result = client->contains(handle->key());
    return result ? 1 : 0;
  }
  catch (const std::exception&) { return RADEX_ERR_UNKNOWN; }
}

} // extern "C"

// Macro instantiation for typed functions
// int32_t
RADEX_DEFINE_C_CLIENT_PUT_SCALAR(int32_t, int32)
RADEX_DEFINE_C_CLIENT_GET_SCALAR(int32_t, int32)
RADEX_DEFINE_C_CLIENT_WAIT_FOR_SCALAR(int32_t, int32)
RADEX_DEFINE_C_CLIENT_PUT_TENSOR(int32_t, int32)
RADEX_DEFINE_C_CLIENT_GET_TENSOR(int32_t, int32)
RADEX_DEFINE_C_CLIENT_WAIT_FOR_TENSOR(int32_t, int32)

// int64_t
RADEX_DEFINE_C_CLIENT_PUT_SCALAR(int64_t, int64)
RADEX_DEFINE_C_CLIENT_GET_SCALAR(int64_t, int64)
RADEX_DEFINE_C_CLIENT_WAIT_FOR_SCALAR(int64_t, int64)
RADEX_DEFINE_C_CLIENT_PUT_TENSOR(int64_t, int64)
RADEX_DEFINE_C_CLIENT_GET_TENSOR(int64_t, int64)
RADEX_DEFINE_C_CLIENT_WAIT_FOR_TENSOR(int64_t, int64)

// float (float32)
RADEX_DEFINE_C_CLIENT_PUT_SCALAR(float, float32)
RADEX_DEFINE_C_CLIENT_GET_SCALAR(float, float32)
RADEX_DEFINE_C_CLIENT_WAIT_FOR_SCALAR(float, float32)
RADEX_DEFINE_C_CLIENT_PUT_TENSOR(float, float32)
RADEX_DEFINE_C_CLIENT_GET_TENSOR(float, float32)
RADEX_DEFINE_C_CLIENT_WAIT_FOR_TENSOR(float, float32)

// double (float64)
RADEX_DEFINE_C_CLIENT_PUT_SCALAR(double, float64)
RADEX_DEFINE_C_CLIENT_GET_SCALAR(double, float64)
RADEX_DEFINE_C_CLIENT_WAIT_FOR_SCALAR(double, float64)
RADEX_DEFINE_C_CLIENT_PUT_TENSOR(double, float64)
RADEX_DEFINE_C_CLIENT_GET_TENSOR(double, float64)
RADEX_DEFINE_C_CLIENT_WAIT_FOR_TENSOR(double, float64)
