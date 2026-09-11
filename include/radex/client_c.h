#ifndef RADEX_CLIENT_C_H
#define RADEX_CLIENT_C_H

#include "radex/errno.h"
#include "radex/handles_c.h"
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/// Opaque pointer to a client (internally an IClient*)
typedef void* radex_client_t;

/// Create a Dragon/DDict client from environment.
/// @return Opaque pointer to a client, or NULL on error.
radex_client_t radex_client_dragon_create(void);

/// Create a SmartRedis client from environment.
/// @return Opaque pointer to a client, or NULL on error.
radex_client_t radex_client_smartredis_create(void);

/// Destroy a client and free its resources.
/// @param pointer to a client returned by radex_client_create_*().
/// @return RADEX_OK on success, error code otherwise.
int radex_client_destroy(radex_client_t client);

// ============================================================================
// Scalar Operations
// ============================================================================

/// Store an int32_t scalar.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param value Value to store.
int radex_client_put_int32(radex_client_t client,
                          radex_outgoing_handle_t* handle,
                          int32_t value);

/// Retrieve an int32_t scalar.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
int radex_client_get_int32(radex_client_t client,
                          radex_incoming_handle_t* handle,
                          int32_t* out_value);

/// Store an int64_t scalar.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param value Value to store.
int radex_client_put_int64(radex_client_t client,
                          radex_outgoing_handle_t* handle,
                          int64_t value);

/// Retrieve an int64_t scalar.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
int radex_client_get_int64(radex_client_t client,
                          radex_incoming_handle_t* handle,
                          int64_t* out_value);

/// Store a float scalar.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param value Value to store.
int radex_client_put_float32(radex_client_t client,
                            radex_outgoing_handle_t* handle,
                            float value);

/// Retrieve a float scalar.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
int radex_client_get_float32(radex_client_t client,
                            radex_incoming_handle_t* handle,
                            float* out_value);

/// Store a double scalar.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param value Value to store.
int radex_client_put_float64(radex_client_t client,
                            radex_outgoing_handle_t* handle,
                            double value);

/// Retrieve a double scalar.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
int radex_client_get_float64(radex_client_t client,
                            radex_incoming_handle_t* handle,
                            double* out_value);

// ============================================================================
// Tensor Operations
// ============================================================================

/// Store an int32_t tensor.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param data Pointer to flattened element data in row-major (C) order.
/// @param rank Number of dimensions.
/// @param dims Pointer to rank dimension sizes.
int radex_client_put_tensor_int32(radex_client_t client,
                                 radex_outgoing_handle_t* handle,
                                 const int32_t* data, int rank, const int* dims);

/// Retrieve an int32_t tensor.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
int radex_client_get_tensor_int32(radex_client_t client,
                                 radex_incoming_handle_t* handle,
                                 int32_t* out_data, int max_elements,
                                 int* out_rank, int* out_dims, int max_dims);

/// Store an int64_t tensor.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param data Pointer to flattened element data in row-major (C) order.
/// @param rank Number of dimensions.
/// @param dims Pointer to rank dimension sizes.
int radex_client_put_tensor_int64(radex_client_t client,
                                 radex_outgoing_handle_t* handle,
                                 const int64_t* data, int rank, const int* dims);

/// Retrieve an int64_t tensor.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
int radex_client_get_tensor_int64(radex_client_t client,
                                 radex_incoming_handle_t* handle,
                                 int64_t* out_data, int max_elements,
                                 int* out_rank, int* out_dims, int max_dims);

/// Store a float tensor.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param data Pointer to flattened element data in row-major (C) order.
/// @param rank Number of dimensions.
/// @param dims Pointer to rank dimension sizes.
int radex_client_put_tensor_float32(radex_client_t client,
                                   radex_outgoing_handle_t* handle,
                                   const float* data, int rank, const int* dims);

/// Retrieve a float tensor.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
int radex_client_get_tensor_float32(radex_client_t client,
                                   radex_incoming_handle_t* handle,
                                   float* out_data, int max_elements,
                                   int* out_rank, int* out_dims, int max_dims);

/// Store a double tensor.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param data Pointer to flattened element data in row-major (C) order.
/// @param rank Number of dimensions.
/// @param dims Pointer to rank dimension sizes.
int radex_client_put_tensor_float64(radex_client_t client,
                                   radex_outgoing_handle_t* handle,
                                   const double* data, int rank, const int* dims);

/// Retrieve a double tensor.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
int radex_client_get_tensor_float64(radex_client_t client,
                                   radex_incoming_handle_t* handle,
                                   double* out_data, int max_elements,
                                   int* out_rank, int* out_dims, int max_dims);

/// Block until an int32_t scalar is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
/// @param timeout_ms Maximum time to wait in milliseconds.
int radex_client_wait_for_int32(radex_client_t client,
                                radex_incoming_handle_t* handle,
                                int32_t* out_value, int timeout_ms);

/// Block until an int64_t scalar is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
/// @param timeout_ms Maximum time to wait in milliseconds.
int radex_client_wait_for_int64(radex_client_t client,
                                radex_incoming_handle_t* handle,
                                int64_t* out_value, int timeout_ms);

/// Block until a float scalar is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
/// @param timeout_ms Maximum time to wait in milliseconds.
int radex_client_wait_for_float32(radex_client_t client,
                                  radex_incoming_handle_t* handle,
                                  float* out_value, int timeout_ms);

/// Block until a double scalar is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
/// @param timeout_ms Maximum time to wait in milliseconds.
int radex_client_wait_for_float64(radex_client_t client,
                                  radex_incoming_handle_t* handle,
                                  double* out_value, int timeout_ms);

/// Block until an int32_t tensor is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
/// @param timeout_ms Maximum time to wait in milliseconds.
int radex_client_wait_for_tensor_int32(radex_client_t client,
                                       radex_incoming_handle_t* handle,
                                       int32_t* out_data, int max_elements,
                                       int* out_rank, int* out_dims, int max_dims,
                                       int timeout_ms);

/// Block until an int64_t tensor is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
/// @param timeout_ms Maximum time to wait in milliseconds.
int radex_client_wait_for_tensor_int64(radex_client_t client,
                                       radex_incoming_handle_t* handle,
                                       int64_t* out_data, int max_elements,
                                       int* out_rank, int* out_dims, int max_dims,
                                       int timeout_ms);

/// Block until a float tensor is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
/// @param timeout_ms Maximum time to wait in milliseconds.
int radex_client_wait_for_tensor_float32(radex_client_t client,
                                         radex_incoming_handle_t* handle,
                                         float* out_data, int max_elements,
                                         int* out_rank, int* out_dims, int max_dims,
                                         int timeout_ms);

/// Block until a double tensor is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
/// @param timeout_ms Maximum time to wait in milliseconds.
int radex_client_wait_for_tensor_float64(radex_client_t client,
                                         radex_incoming_handle_t* handle,
                                         double* out_data, int max_elements,
                                         int* out_rank, int* out_dims, int max_dims,
                                         int timeout_ms);

// ============================================================================
// Utility Operations
// ============================================================================

/// Check if a key exists in the store.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @return 1 if key exists, 0 if not, error code (<0) on error.
int radex_client_contains(radex_client_t client,
                         radex_incoming_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif // RADEX_CLIENT_C_H
