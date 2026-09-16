#ifndef RADEX_CLIENT_C_H
#define RADEX_CLIENT_C_H

#include "radex/errno.h"
#include "radex/handles_c.h"
#include "radex/macros/client_c_declaration_macros.h"
#include <stdint.h>
#include <cstddef>

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
RADEX_DECLARE_C_CLIENT_PUT_SCALAR(int32_t, int32)

/// Retrieve an int32_t scalar.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
RADEX_DECLARE_C_CLIENT_GET_SCALAR(int32_t, int32)

/// Block until an int32_t scalar is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
/// @param timeout_ms Maximum time to wait in milliseconds.
RADEX_DECLARE_C_CLIENT_WAIT_FOR_SCALAR(int32_t, int32)

/// Store an int64_t scalar.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param value Value to store.
RADEX_DECLARE_C_CLIENT_PUT_SCALAR(int64_t, int64)

/// Retrieve an int64_t scalar.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
RADEX_DECLARE_C_CLIENT_GET_SCALAR(int64_t, int64)

/// Block until an int64_t scalar is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
/// @param timeout_ms Maximum time to wait in milliseconds.
RADEX_DECLARE_C_CLIENT_WAIT_FOR_SCALAR(int64_t, int64)

/// Store a float scalar.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param value Value to store.
RADEX_DECLARE_C_CLIENT_PUT_SCALAR(float, float32)

/// Retrieve a float scalar.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
RADEX_DECLARE_C_CLIENT_GET_SCALAR(float, float32)

/// Block until a float scalar is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
/// @param timeout_ms Maximum time to wait in milliseconds.
RADEX_DECLARE_C_CLIENT_WAIT_FOR_SCALAR(float, float32)

/// Store a double scalar.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param value Value to store.
RADEX_DECLARE_C_CLIENT_PUT_SCALAR(double, float64)

/// Retrieve a double scalar.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
RADEX_DECLARE_C_CLIENT_GET_SCALAR(double, float64)

/// Block until a double scalar is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_value Pointer to store the retrieved value.
/// @param timeout_ms Maximum time to wait in milliseconds.
RADEX_DECLARE_C_CLIENT_WAIT_FOR_SCALAR(double, float64)

// ============================================================================
// Tensor Operations
// ============================================================================

/// Store an int32_t tensor.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param data Pointer to flattened element data in row-major (C) order.
/// @param rank Number of dimensions.
/// @param dims Pointer to rank dimension sizes.
RADEX_DECLARE_C_CLIENT_PUT_TENSOR(int32_t, int32)

/// Retrieve an int32_t tensor.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
RADEX_DECLARE_C_CLIENT_GET_TENSOR(int32_t, int32)

/// Block until an int32_t tensor is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
/// @param timeout_ms Maximum time to wait in milliseconds.
RADEX_DECLARE_C_CLIENT_WAIT_FOR_TENSOR(int32_t, int32)

/// Store an int64_t tensor.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param data Pointer to flattened element data in row-major (C) order.
/// @param rank Number of dimensions.
/// @param dims Pointer to rank dimension sizes.
RADEX_DECLARE_C_CLIENT_PUT_TENSOR(int64_t, int64)

/// Retrieve an int64_t tensor.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
RADEX_DECLARE_C_CLIENT_GET_TENSOR(int64_t, int64)

/// Block until an int64_t tensor is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
/// @param timeout_ms Maximum time to wait in milliseconds.
RADEX_DECLARE_C_CLIENT_WAIT_FOR_TENSOR(int64_t, int64)

/// Store a float tensor.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param data Pointer to flattened element data in row-major (C) order.
/// @param rank Number of dimensions.
/// @param dims Pointer to rank dimension sizes.
RADEX_DECLARE_C_CLIENT_PUT_TENSOR(float, float32)

/// Retrieve a float tensor.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
RADEX_DECLARE_C_CLIENT_GET_TENSOR(float, float32)

/// Block until a float tensor is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
/// @param timeout_ms Maximum time to wait in milliseconds.
RADEX_DECLARE_C_CLIENT_WAIT_FOR_TENSOR(float, float32)

/// Store a double tensor.
/// @param client Initialized radex client.
/// @param handle Outgoing handle for the key.
/// @param data Pointer to flattened element data in row-major (C) order.
/// @param rank Number of dimensions.
/// @param dims Pointer to rank dimension sizes.
RADEX_DECLARE_C_CLIENT_PUT_TENSOR(double, float64)

/// Retrieve a double tensor.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
RADEX_DECLARE_C_CLIENT_GET_TENSOR(double, float64)

/// Block until a double tensor is available, then retrieve it.
/// @param client Initialized radex client.
/// @param handle Incoming handle for the key.
/// @param out_data Buffer to hold flattened element data (caller-allocated).
/// @param max_elements Maximum capacity of out_data buffer.
/// @param out_rank Output: number of dimensions.
/// @param out_dims Buffer for dimension sizes (caller-allocated).
/// @param max_dims Maximum capacity of out_dims buffer.
/// @param timeout_ms Maximum time to wait in milliseconds.
RADEX_DECLARE_C_CLIENT_WAIT_FOR_TENSOR(double, float64)

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
