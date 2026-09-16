#ifndef RADEX_CLIENT_C_DECLARATION_MACROS_H
#define RADEX_CLIENT_C_DECLARATION_MACROS_H

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
                                       CTYPE* out_value, size_t timeout_ms);

// Tensor methods declarations

/// Declare a put_tensor function for a given C type
#define RADEX_DECLARE_C_CLIENT_PUT_TENSOR(CTYPE, TYPE_TAG) \
  int radex_client_put_tensor_##TYPE_TAG(radex_client_t client, \
                                         radex_outgoing_handle_t* handle, \
                                         const CTYPE* data, size_t rank, const size_t* dims);

/// Declare a get_tensor function for a given C type
#define RADEX_DECLARE_C_CLIENT_GET_TENSOR(CTYPE, TYPE_TAG) \
  int radex_client_get_tensor_##TYPE_TAG(radex_client_t client, \
                                         radex_incoming_handle_t* handle, \
                                         CTYPE* out_data, size_t max_elements, \
                                         size_t* out_rank, size_t* out_dims, size_t max_dims);

/// Declare a wait_for_tensor function for a given C type
#define RADEX_DECLARE_C_CLIENT_WAIT_FOR_TENSOR(CTYPE, TYPE_TAG) \
  int radex_client_wait_for_tensor_##TYPE_TAG(radex_client_t client, \
                                              radex_incoming_handle_t* handle, \
                                              CTYPE* out_data, size_t max_elements, \
                                              size_t* out_rank, size_t* out_dims, size_t max_dims, \
                                              size_t timeout_ms);

#endif // RADEX_CLIENT_C_DECLARATION_MACROS_H
