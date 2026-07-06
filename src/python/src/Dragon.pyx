import cython

from libcpp.string cimport string
from libcpp.memory cimport unique_ptr
from libc.time cimport timespec

from Dragon cimport Client, ItemInfo
from Data cimport SupportedType, make_ndarray, DType

cimport numpy as np
import numpy as np

np.import_array()


cdef class DragonClient:
    cdef Client *_client

    def __cinit__(self, str descriptor, int timeout):
        cdef string desc = descriptor.encode("utf-8");
        cdef timespec spec = timespec(timeout, 0)
        self._client = new Client(desc.c_str(), &spec)

    def __dealloc__(self):
        del self._client

    def contains(self, str key):
        cdef string key_ = key.encode("utf-8")
        return self._client.contains(key_)

    def put_scalar(self, str key, SupportedType value):
        cdef string key_ = key.encode("utf-8")
        self._client.put_scalar[cython.typeof(value)](key_, value)

    def get_scalar(self, str key):
        cdef string key_ = key.encode("utf-8")
        cdef unique_ptr[ItemInfo] info = self._client.get_item_info_ptr(key_)
        cdef ItemInfo* info_ = info.get()

        if info_.metadata().n_dims() != 0:
            # TODO: Better error type/msg here
            raise ValueError("Attempted to retrieve scalar at a key with a vector")

        cdef DType type_ = info_.metadata().type()
        return make_ndarray(type_, info_.data(), 1)[0]

    def put_tensor(self, str key, np.ndarray tensor not None):
        cdef np.ndarray[np.uint64_t, ndim=1] dims = np.asarray(
                (<object>tensor).shape, dtype=np.uint64)
        self._put_tensor(key, dims, tensor.ravel())

    def _put_tensor(
        self,
        str key,
        const np.uint64_t[:] dims not None,
        const SupportedType[:] data not None,
    ):
        cdef string key_ = key.encode("utf-8")
        return self._client.put_tensor(key_,
                                       &dims[0], dims.size,
                                       &data[0], data.size)

    def get_tensor(self, str key):
        cdef string key_ = key.encode("utf-8")
        cdef unique_ptr[ItemInfo] info = self._client.get_item_info_ptr(key_)
        cdef ItemInfo* info_ = info.get()

        cdef np.uint64_t n_dims = info_.metadata().n_dims()
        if n_dims == 0:
            # TODO: Better error type/msg here
            raise ValueError("Attempted to retrieve vector at a key with a scalar")
        cdef np.uint64_t[:] dims = <np.uint64_t[:n_dims]> info_.metadata().dims_ptr()

        cdef np.uint64_t n_elements = info_.metadata().n_elements()
        cdef DType type_ = info_.metadata().type()

        data = make_ndarray(type_, info_.data(), n_elements)
        return data.reshape(dims)
