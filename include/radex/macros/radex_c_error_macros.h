#ifndef RADEX_C_ERROR_MACROS_H
#define RADEX_C_ERROR_MACROS_H

#include "radex/errno.h"
#include <stdio.h>

#ifdef __cplusplus
#include "radex/exceptions.hpp"
#include <new>
#endif

/// Log error to stderr and return the error code
#define RADEX_C_LOG_AND_RETURN(error_code) \
    (fprintf(stderr, "RaDex Error: %s\n", #error_code), error_code)

#ifdef __cplusplus

/// Map common C++ exceptions to C API error codes.
#define RADEX_C_CATCH_EXCEPTIONS(fallback_error) \
    catch (const radex::KeyNotFoundError&) { \
        return RADEX_C_LOG_AND_RETURN(RADEX_ERR_KEY_NOT_FOUND); \
    } \
    catch (const radex::TimeoutError&) { \
        return RADEX_C_LOG_AND_RETURN(RADEX_ERR_TIMEOUT); \
    } \
    catch (const radex::RankMismatchError&) { \
        return RADEX_C_LOG_AND_RETURN(RADEX_ERR_RANK_MISMATCH); \
    } \
    catch (const radex::DTypeMismatchError&) { \
        return RADEX_C_LOG_AND_RETURN(RADEX_ERR_DTYPE_MISMATCH); \
    } \
    catch (const radex::MetadataError&) { \
        return RADEX_C_LOG_AND_RETURN(RADEX_ERR_METADATA); \
    } \
    catch (const radex::BackendUnavailableError&) { \
        return RADEX_C_LOG_AND_RETURN(RADEX_ERR_BACKEND_UNAVAILABLE); \
    } \
    catch (const radex::TypeMismatchError&) { \
        return RADEX_C_LOG_AND_RETURN(RADEX_ERR_TYPE_MISMATCH); \
    } \
    catch (const std::bad_alloc&) { \
        return RADEX_C_LOG_AND_RETURN(RADEX_ERR_ALLOCATION); \
    } \
    catch (const std::exception&) { \
        return RADEX_C_LOG_AND_RETURN(fallback_error); \
    }

#endif

#endif // RADEX_C_ERROR_MACROS_H
