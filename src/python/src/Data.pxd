cimport numpy as np
import numpy as np

np.import_array()

ctypedef fused SupportedType:
    np.int32_t
    np.int64_t
    np.float64_t

cdef extern from "raddex/client.hpp" namespace "raddex::data":
    cdef enum class DType(np.uint64_t):
        INT32,
        INT64,
        FLOAT64

# TODO: Don't like this method name
cdef inline make_ndarray(DType dtype, const void* data, np.uint64_t size):
    if dtype == DType.INT32:
        return np.copy(<np.int32_t[:size]> data)
    if dtype == DType.INT64:
        return np.copy(<np.int64_t[:size]> data)
    if dtype == DType.FLOAT64:
        return np.copy(<np.float64_t[:size]> data)
    raise TypeError("Unknown type encountered")
