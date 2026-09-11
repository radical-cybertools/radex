#ifndef RADEX_CLIENT_C_MACROS_HPP
#define RADEX_CLIENT_C_MACROS_HPP

#include "radex/client_base.hpp"
#include "radex/errno.h"
#include <cstring>
#include <string_view>
#include <cstdio>

/// Helper macro to log error to stderr and return the error code
#define LOG_RADEX_ERROR(error_code) \
  (fprintf(stderr, "RaDex Error: %s\n", #error_code), error_code)

/// Exception mapping with stderr logging
#define RADEX_CATCH_EXCEPTIONS(fallback_error) \
  catch (const radex::KeyNotFoundError&) { \
    return LOG_RADEX_ERROR(RADEX_ERR_KEY_NOT_FOUND); \
  } \
  catch (const radex::TimeoutError&) { \
    return LOG_RADEX_ERROR(RADEX_ERR_TIMEOUT); \
  } \
  catch (const radex::RankMismatchError&) { \
    return LOG_RADEX_ERROR(RADEX_ERR_RANK_MISMATCH); \
  } \
  catch (const radex::DTypeMismatchError&) { \
    return LOG_RADEX_ERROR(RADEX_ERR_DTYPE_MISMATCH); \
  } \
  catch (const radex::MetadataError&) { \
    return LOG_RADEX_ERROR(RADEX_ERR_METADATA); \
  } \
  catch (const radex::BackendUnavailableError&) { \
    return LOG_RADEX_ERROR(RADEX_ERR_BACKEND_UNAVAILABLE); \
  } \
  catch (const radex::TypeMismatchError&) { \
    return LOG_RADEX_ERROR(RADEX_ERR_TYPE_MISMATCH); \
  } \
  catch (const std::exception&) { \
    return LOG_RADEX_ERROR(RADEX_ERR_UNKNOWN); \
  }

/// Generate put_scalar C function for a given C type
#define RADEX_DEFINE_C_CLIENT_PUT_SCALAR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_put_##TYPE_TAG(void* client_ptr, void* handle_ptr, CTYPE value) { \
      if (!client_ptr || !handle_ptr) return LOG_RADEX_ERROR(RADEX_ERR_NULL_ARGS); \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = static_cast<radex::data::OutgoingHandle*>(handle_ptr); \
      try { \
        client->put_scalar<CTYPE>(*handle, value); \
        return RADEX_OK; \
      } RADEX_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

/// Generate get_scalar C function for a given C type
#define RADEX_DEFINE_C_CLIENT_GET_SCALAR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_get_##TYPE_TAG(void* client_ptr, void* handle_ptr, CTYPE* out_value) { \
      if (!client_ptr || !handle_ptr || !out_value) return LOG_RADEX_ERROR(RADEX_ERR_NULL_ARGS); \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = static_cast<radex::data::IncomingHandle*>(handle_ptr); \
      try { \
        *out_value = client->get_scalar<CTYPE>(*handle); \
        return RADEX_OK; \
      } RADEX_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

/// Generate put_tensor C function for a given C type
#define RADEX_DEFINE_C_CLIENT_PUT_TENSOR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_put_tensor_##TYPE_TAG(void* client_ptr, void* handle_ptr, \
        const CTYPE* data, int rank, const int* dims) { \
      if (!client_ptr || !handle_ptr || !data || rank <= 0 || !dims) \
        return LOG_RADEX_ERROR(RADEX_ERR_NULL_ARGS); \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = static_cast<radex::data::OutgoingHandle*>(handle_ptr); \
      try { \
        std::vector<radex::detail::MetaInt> dims_vec(dims, dims + rank); \
        radex::detail::MetaInt n_elements = 1; \
        for (int i = 0; i < rank; ++i) n_elements *= dims[i]; \
        client->put_tensor<CTYPE>(*handle, dims_vec.data(), rank, data, n_elements); \
        return RADEX_OK; \
      } RADEX_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

/// Generate get_tensor C function for a given C type
//TODO: Add a method to C++ to allow a buffer to be passed and then
//      filled instead of doing a memcopy. See also wait_for_tensor
#define RADEX_DEFINE_C_CLIENT_GET_TENSOR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_get_tensor_##TYPE_TAG(void* client_ptr, void* handle_ptr, \
        CTYPE* out_data, int max_elements, \
        int* out_rank, int* out_dims, int max_dims) { \
      if (!client_ptr || !handle_ptr || !out_rank || !out_dims) \
        return LOG_RADEX_ERROR(RADEX_ERR_NULL_ARGS); \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = static_cast<radex::data::IncomingHandle*>(handle_ptr); \
      try { \
        auto tensor = client->get_tensor<CTYPE>(*handle); \
        if (static_cast<int>(tensor.data.size()) > max_elements) \
          return LOG_RADEX_ERROR(RADEX_ERR_BUFFER_TOO_SMALL); \
        if (static_cast<int>(tensor.dims.size()) > max_dims) \
          return LOG_RADEX_ERROR(RADEX_ERR_RANK_MISMATCH); \
        if (out_data && tensor.data.size() > 0) { \
          std::memcpy(out_data, tensor.data.data(), \
                      tensor.data.size() * sizeof(CTYPE)); \
        } \
        if (out_dims && tensor.dims.size() > 0) { \
          for (int i = 0; i < static_cast<int>(tensor.dims.size()); ++i) { \
            out_dims[i] = static_cast<int>(tensor.dims[i]); \
          } \
        } \
        *out_rank = static_cast<int>(tensor.dims.size()); \
        return RADEX_OK; \
      } RADEX_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

/// Generate wait_for_scalar C function for a given C type
#define RADEX_DEFINE_C_CLIENT_WAIT_FOR_SCALAR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_wait_for_##TYPE_TAG(void* client_ptr, void* handle_ptr, \
        CTYPE* out_value, int timeout_ms) { \
      if (!client_ptr || !handle_ptr || !out_value) return LOG_RADEX_ERROR(RADEX_ERR_NULL_ARGS); \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = static_cast<radex::data::IncomingHandle*>(handle_ptr); \
      try { \
        *out_value = client->wait_for_scalar<CTYPE>(*handle, \
            std::chrono::milliseconds(timeout_ms)); \
        return RADEX_OK; \
      } RADEX_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

/// Generate wait_for_tensor C function for a given C type
// TODO: Add a method to C++ to allow a buffer to be passed and then
//      filled instead of doing a memcopy. See also get_tensor
#define RADEX_DEFINE_C_CLIENT_WAIT_FOR_TENSOR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_wait_for_tensor_##TYPE_TAG(void* client_ptr, void* handle_ptr, \
        CTYPE* out_data, int max_elements, \
        int* out_rank, int* out_dims, int max_dims, int timeout_ms) { \
      if (!client_ptr || !handle_ptr || !out_rank || !out_dims) \
        return LOG_RADEX_ERROR(RADEX_ERR_NULL_ARGS); \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = static_cast<radex::data::IncomingHandle*>(handle_ptr); \
      try { \
        auto tensor = client->wait_for_tensor<CTYPE>(*handle, \
            std::chrono::milliseconds(timeout_ms)); \
        if (static_cast<int>(tensor.data.size()) > max_elements) \
          return LOG_RADEX_ERROR(RADEX_ERR_BUFFER_TOO_SMALL); \
        if (static_cast<int>(tensor.dims.size()) > max_dims) \
          return LOG_RADEX_ERROR(RADEX_ERR_RANK_MISMATCH); \
        if (out_data && tensor.data.size() > 0) { \
          std::memcpy(out_data, tensor.data.data(), \
                      tensor.data.size() * sizeof(CTYPE)); \
        } \
        if (out_dims && tensor.dims.size() > 0) { \
          for (int i = 0; i < static_cast<int>(tensor.dims.size()); ++i) { \
            out_dims[i] = static_cast<int>(tensor.dims[i]); \
          } \
        } \
        *out_rank = static_cast<int>(tensor.dims.size()); \
        return RADEX_OK; \
      } RADEX_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

#endif // RADEX_CLIENT_C_MACROS_HPP
