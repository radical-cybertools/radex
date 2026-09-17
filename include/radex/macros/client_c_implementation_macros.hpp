#ifndef RADEX_CLIENT_C_IMPLEMENTATION_MACROS_HPP
#define RADEX_CLIENT_C_IMPLEMENTATION_MACROS_HPP

#include "radex/client_base.hpp"
#include "radex/errno.h"
#include "radex/macros/radex_c_error_macros.h"
#include <cstring>
#include <string_view>
#include <cstdio>

/// Generate put_scalar C function for a given C type
#define RADEX_DEFINE_C_CLIENT_PUT_SCALAR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_put_##TYPE_TAG(radex_client_t client_ptr, radex_outgoing_handle_t* handle_ptr, CTYPE value) { \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = reinterpret_cast<radex::data::OutgoingHandle*>(handle_ptr); \
      try { \
        client->put_scalar<CTYPE>(*handle, value); \
        return RADEX_OK; \
      } RADEX_C_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

/// Generate get_scalar C function for a given C type
#define RADEX_DEFINE_C_CLIENT_GET_SCALAR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_get_##TYPE_TAG(radex_client_t client_ptr, radex_incoming_handle_t* handle_ptr, CTYPE* out_value) { \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = reinterpret_cast<radex::data::IncomingHandle*>(handle_ptr); \
      try { \
        *out_value = client->get_scalar<CTYPE>(*handle); \
        return RADEX_OK; \
      } RADEX_C_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

/// Generate put_tensor C function for a given C type
#define RADEX_DEFINE_C_CLIENT_PUT_TENSOR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_put_tensor_##TYPE_TAG(radex_client_t client_ptr, radex_outgoing_handle_t* handle_ptr, \
        const CTYPE* data, size_t rank, const size_t* dims) { \
      if (rank <= 0) return RADEX_C_LOG_AND_RETURN(RADEX_ERR_RANK_MISMATCH); \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = reinterpret_cast<radex::data::OutgoingHandle*>(handle_ptr); \
      try { \
        std::vector<radex::detail::MetaInt> dims_vec(dims, dims + rank); \
        radex::detail::MetaInt n_elements = 1; \
        for (size_t i = 0; i < rank; ++i) n_elements *= dims[i]; \
        client->put_tensor<CTYPE>(*handle, dims_vec.data(), rank, data, n_elements); \
        return RADEX_OK; \
      } RADEX_C_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

/// Generate get_tensor C function for a given C type
//TODO: Add a method to C++ to allow a buffer to be passed and then
//      filled instead of doing a memcopy. See also wait_for_tensor
#define RADEX_DEFINE_C_CLIENT_GET_TENSOR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_get_tensor_##TYPE_TAG(radex_client_t client_ptr, radex_incoming_handle_t* handle_ptr, \
        CTYPE* out_data, size_t max_elements, \
        size_t* out_rank, size_t* out_dims, size_t max_dims) { \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = reinterpret_cast<radex::data::IncomingHandle*>(handle_ptr); \
      try { \
        auto tensor = client->get_tensor<CTYPE>(*handle); \
        if (tensor.data.size() > max_elements) \
          return RADEX_C_LOG_AND_RETURN(RADEX_ERR_BUFFER_TOO_SMALL); \
        if (tensor.dims.size() > max_dims) \
          return RADEX_C_LOG_AND_RETURN(RADEX_ERR_RANK_MISMATCH); \
        if (out_data && tensor.data.size() > 0) { \
          std::memcpy(out_data, tensor.data.data(), \
                      tensor.data.size() * sizeof(CTYPE)); \
        } \
        if (out_dims && tensor.dims.size() > 0) { \
          std::memcpy(out_dims, tensor.dims.data(), \
                      tensor.data.size() * sizeof(size_t)); \
        } \
        *out_rank = tensor.dims.size(); \
        return RADEX_OK; \
      } RADEX_C_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

/// Generate wait_for_scalar C function for a given C type
#define RADEX_DEFINE_C_CLIENT_WAIT_FOR_SCALAR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_wait_for_##TYPE_TAG(radex_client_t client_ptr, radex_incoming_handle_t* handle_ptr, \
        CTYPE* out_value, size_t timeout_ms) { \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = reinterpret_cast<radex::data::IncomingHandle*>(handle_ptr); \
      try { \
        *out_value = client->wait_for_scalar<CTYPE>(*handle, \
            std::chrono::milliseconds(timeout_ms)); \
        return RADEX_OK; \
      } RADEX_C_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

/// Generate wait_for_tensor C function for a given C type
// TODO: Add a method to C++ to allow a buffer to be passed and then
//      filled instead of doing a memcopy. See also get_tensor
#define RADEX_DEFINE_C_CLIENT_WAIT_FOR_TENSOR(CTYPE, TYPE_TAG) \
  extern "C" { \
    int radex_client_wait_for_tensor_##TYPE_TAG(radex_client_t client_ptr, radex_incoming_handle_t* handle_ptr, \
        CTYPE* out_data, size_t max_elements, \
        size_t* out_rank, size_t* out_dims, size_t max_dims, size_t timeout_ms) { \
      auto* client = static_cast<radex::IClient*>(client_ptr); \
      auto* handle = reinterpret_cast<radex::data::IncomingHandle*>(handle_ptr); \
      try { \
        auto tensor = client->wait_for_tensor<CTYPE>(*handle, \
            std::chrono::milliseconds(timeout_ms)); \
        if (tensor.data.size() > max_elements) \
          return RADEX_C_LOG_AND_RETURN(RADEX_ERR_BUFFER_TOO_SMALL); \
        if (tensor.dims.size() > max_dims) \
          return RADEX_C_LOG_AND_RETURN(RADEX_ERR_RANK_MISMATCH); \
        if (out_data && tensor.data.size() > 0) { \
          std::memcpy(out_data, tensor.data.data(), \
                      tensor.data.size() * sizeof(CTYPE)); \
        } \
        if (out_dims && tensor.dims.size() > 0) { \
          std::memcpy(out_dims, tensor.dims.data(), \
                      tensor.data.size() * sizeof(size_t)); \
        } \
        *out_rank = static_cast<int>(tensor.dims.size()); \
        return RADEX_OK; \
      } RADEX_C_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN) \
    } \
  }

#endif // RADEX_CLIENT_C_IMPLEMENTATION_MACROS_HPP
