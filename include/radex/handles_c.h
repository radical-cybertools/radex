#ifndef __RADEX_HANDLES_C_H__
#define __RADEX_HANDLES_C_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque handles for C API */
typedef struct radex_incoming_handle radex_incoming_handle_t;
typedef struct radex_outgoing_handle radex_outgoing_handle_t;

/**
 * Create an incoming handle for reading from the store.
 * @param name The key name to read from (null-terminated string).
 * @return A new incoming handle, or NULL on error.
 */
radex_incoming_handle_t* radex_incoming_handle_create(const char* name);

/**
 * Destroy an incoming handle and free its resources.
 * @param handle The handle to destroy.
 */
void radex_incoming_handle_destroy(radex_incoming_handle_t* handle);

/**
 * Create an outgoing handle for writing to the store.
 * @param name The key name to write to (null-terminated string).
 * @return A new outgoing handle, or NULL on error.
 */
radex_outgoing_handle_t* radex_outgoing_handle_create(const char* name);

/**
 * Destroy an outgoing handle and free its resources.
 * @param handle The handle to destroy.
 */
void radex_outgoing_handle_destroy(radex_outgoing_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif /* __RADEX_HANDLES_C_H__ */
