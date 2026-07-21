cimport numpy as np
import numpy as np
from libc.stdint cimport int32_t, int64_t, uint64_t

np.import_array()

ctypedef fused SupportedType:
    int32_t
    int64_t
    float
    double

cdef extern from "raddex/client.hpp" namespace "raddex::data":
    cdef enum class DType(uint64_t):
        INT32,
        INT64,
        FLOAT32,
        FLOAT64


# TODO: Don't like this method name
cdef inline make_ndarray(DType dtype, const void* data, uint64_t size):
    if dtype == DType.INT32:
        return np.copy(<np.int32_t[:size]> data)
    if dtype == DType.INT64:
        return np.copy(<np.int64_t[:size]> data)
    if dtype == DType.FLOAT32:
        return np.copy(<np.float32_t[:size]> data)
    if dtype == DType.FLOAT64:
        return np.copy(<np.float64_t[:size]> data)
    raise TypeError("Unknown type encountered")


cdef inline np.number coerce_py_objects_to_np_numbers(object value):
    _DEFAULT_FIXED_WIDTH_INT = np.int32
    _DEFAULT_FIXED_WIDTH_FLOAT = np.float64

    if isinstance(value, int):
        value = _DEFAULT_FIXED_WIDTH_INT(value)
    if isinstance(value, float):
        value = _DEFAULT_FIXED_WIDTH_FLOAT(value)
    if not isinstance(value, np.number):
        raise TypeError(
            f"Could not figure out how to coerce {type(value)} to a numpy.number"
        )
    return value
