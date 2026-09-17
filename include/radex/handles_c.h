#ifndef __RADEX_HANDLES_C_H__
#define __RADEX_HANDLES_C_H__

#include "radex/errno.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque handles for C API */
typedef struct radex_incoming_handle radex_incoming_handle_t;
typedef struct radex_outgoing_handle radex_outgoing_handle_t;

/**
 * Create an incoming handle for reading from the store.
 * @param name The key name to read from (null-terminated string).
 * @param out_handle Receives the new handle on success.
 * @return RADEX_OK on success, an error code otherwise.
 */
int radex_incoming_handle_create(const char* name,
								 radex_incoming_handle_t** out_handle);

/**
 * Destroy an incoming handle and free its resources.
 * @param handle The handle to destroy.
 */
int radex_incoming_handle_destroy(radex_incoming_handle_t* handle);

/**
 * Create an outgoing handle for writing to the store.
 * @param name The key name to write to (null-terminated string).
 * @param out_handle Receives the new handle on success.
 * @return RADEX_OK on success, an error code otherwise.
 */
int radex_outgoing_handle_create(const char* name,
								 radex_outgoing_handle_t** out_handle);

/**
 * Destroy an outgoing handle and free its resources.
 * @param handle The handle to destroy.
 */
int radex_outgoing_handle_destroy(radex_outgoing_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif /* __RADEX_HANDLES_C_H__ */
