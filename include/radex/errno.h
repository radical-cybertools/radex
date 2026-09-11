#ifndef RADEX_ERRNO_H
#define RADEX_ERRNO_H

#ifdef __cplusplus
extern "C" {
#endif

/// Error codes returned by C interface functions
enum radex_errno {
  RADEX_OK = 0,                        // Success
  RADEX_ERR_KEY_NOT_FOUND = 1,         // Key does not exist in store
  RADEX_ERR_TIMEOUT = 2,               // Operation timed out
  RADEX_ERR_TYPE_MISMATCH = 3,         // Type/dtype mismatch
  RADEX_ERR_RANK_MISMATCH = 4,         // Rank mismatch (scalar, tensor, or mismatched number of dimensions)
  RADEX_ERR_DTYPE_MISMATCH = 5,        // Element type mismatch
  RADEX_ERR_METADATA = 6,              // Metadata decode error
  RADEX_ERR_BACKEND_UNAVAILABLE = 7,   // Backend not available
  RADEX_ERR_BUFFER_TOO_SMALL = 8,      // Tensor is larger than the provided buffer
  RADEX_ERR_NULL_ARGS = 9,             // Some input arguments are null when they must exist
  RADEX_ERR_UNKNOWN = 99               // Unknown/unexpected error
};

#ifdef __cplusplus
}
#endif

#endif // RADEX_ERRNO_H
