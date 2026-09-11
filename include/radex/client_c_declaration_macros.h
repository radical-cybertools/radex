#ifndef RADEX_CLIENT_C_DECLARATION_MACROS_H
#define RADEX_CLIENT_C_DECLARATION_MACROS_H

/// @file client_c_decls_macros.h
/// Macros for declaring C interface functions (put/get/wait_for scalar and tensor operations)

// Scalar method declaration

/// Declare a put_scalar function for a given C type
#define RADEX_DECLARE_C_CLIENT_PUT_SCALAR(CTYPE, TYPE_TAG) \
  int radex_client_put_##TYPE_TAG(radex_client_t client, \
                                  radex_outgoing_handle_t* handle, \
                                  CTYPE value);

/// Declare a get_scalar function for a given C type
#define RADEX_DECLARE_C_CLIENT_GET_SCALAR(CTYPE, TYPE_TAG) \
  int radex_client_get_##TYPE_TAG(radex_client_t client, \
                                  radex_incoming_handle_t* handle, \
                                  CTYPE* out_value);

/// Declare a wait_for_scalar function for a given C type
#define RADEX_DECLARE_C_CLIENT_WAIT_FOR_SCALAR(CTYPE, TYPE_TAG) \
  int radex_client_wait_for_##TYPE_TAG(radex_client_t client, \
                                       radex_incoming_handle_t* handle, \
                                       CTYPE* out_value, int timeout_ms);

// Tensor methods declarations

/// Declare a put_tensor function for a given C type
#define RADEX_DECLARE_C_CLIENT_PUT_TENSOR(CTYPE, TYPE_TAG) \
  int radex_client_put_tensor_##TYPE_TAG(radex_client_t client, \
                                         radex_outgoing_handle_t* handle, \
                                         const CTYPE* data, int rank, const int* dims);

/// Declare a get_tensor function for a given C type
#define RADEX_DECLARE_C_CLIENT_GET_TENSOR(CTYPE, TYPE_TAG) \
  int radex_client_get_tensor_##TYPE_TAG(radex_client_t client, \
                                         radex_incoming_handle_t* handle, \
                                         CTYPE* out_data, int max_elements, \
                                         int* out_rank, int* out_dims, int max_dims);

/// Declare a wait_for_tensor function for a given C type
#define RADEX_DECLARE_C_CLIENT_WAIT_FOR_TENSOR(CTYPE, TYPE_TAG) \
  int radex_client_wait_for_tensor_##TYPE_TAG(radex_client_t client, \
                                              radex_incoming_handle_t* handle, \
                                              CTYPE* out_data, int max_elements, \
                                              int* out_rank, int* out_dims, int max_dims, \
                                              int timeout_ms);

#endif // RADEX_CLIENT_C_DECLS_MACROS_H
