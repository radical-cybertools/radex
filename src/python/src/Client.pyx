import cython

from libcpp.string cimport string
from libcpp.memory cimport unique_ptr
from libc.time cimport timespec
from libc.stdint cimport uint64_t

from Client cimport IClient, ItemInfo, BytesBuffer
from Dragon cimport Client
from Data cimport (
    DType,
    SupportedType,
    coerce_py_objects_to_np_numbers,
    make_ndarray,
)

import pickle

cimport numpy as np
import numpy as np
np.import_array()


cdef class PyClient:
    cdef IClient *_client

    def __dealloc__(self):
        # TODO: The clients really should be using a unique_ptr instead
        if self._client != NULL:
            del self._client
            self._client = NULL

    def contains(self, str key):
        cdef string key_ = key.encode("utf-8")
        return self._client.contains(key_)

    def put_scalar(self, str key, object value not None):
        cdef np.number val = coerce_py_objects_to_np_numbers(value)
        return self._put_scalar(key, val)

    def _put_scalar(self, str key, np.number value not None):
        cdef string key_ = key.encode("utf-8")

        # FIXME: Get rid of this ugly swith statment. Ideally we could used the
        #        fused `SupportedType` type, but there seems to be a known
        #        issue with how it dispatches
        # https://github.com/cython/cython/issues/4932
        if isinstance(value, np.int32):
            return self._client.put_scalar[np.int32_t](key_, value)
        if isinstance(value, np.int64):
            return self._client.put_scalar[np.int64_t](key_, value)
        if isinstance(value, np.float32):
            return self._client.put_scalar[np.float32_t](key_, value)
        if isinstance(value, np.float64):
            return self._client.put_scalar[np.float64_t](key_, value)
        raise TypeError(f"Unsupported data type: {type(value)}")

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
        cdef np.ndarray[uint64_t, ndim=1] dims_arr = np.asarray((<object>tensor).shape,
                              dtype=np.uint64)
        self._put_tensor(key, dims_arr, tensor.ravel())

    def _put_tensor(
        self,
        str key,
        const uint64_t[:] dims not None,
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

        cdef uint64_t n_dims = info_.metadata().n_dims()
        if n_dims == 0:
            # TODO: Better error type/msg here
            raise ValueError("Attempted to retrieve vector at a key with a scalar")
        cdef const uint64_t[:] dims = (
            <const uint64_t[:n_dims]> info_.metadata().dims_ptr()
        )

        cdef uint64_t n_elements = info_.metadata().n_elements()
        cdef DType type_ = info_.metadata().type()

        data = make_ndarray(type_, info_.data(), n_elements)
        return data.reshape(dims)

    def put_picklable(self, str key, object picklable):
        cdef string key_ = key.encode("utf-8")
        cdef bytes bytes_ = pickle.dumps(picklable)
        cdef void* ptr = <void*><char*>bytes_
        cdef uint64_t len_ = len(bytes_)
        self._client.put_bytes(key_, ptr, len_)

    def get_picklable(self, str key):
        cdef string key_ = key.encode("utf-8")
        cdef BytesBuffer buf = self._client.get_bytes(key_)

        cdef uint64_t len_ = buf.get_length()
        cdef np.uint8_t *ptr = <np.uint8_t*>buf.get_ptr()

        cdef bytes bytes_ = <bytes>ptr[:len_]
        return pickle.loads(bytes_)


cdef class DragonClient(PyClient):
    def __cinit__(self, descriptor: str | None=None, int timeout=5):
        cdef string desc
        cdef timespec spec

        if descriptor is None:
            self._client = new Client()
            return

        if not isinstance(descriptor, str):
            raise TypeError("descriptor must be a str or None")

        desc = (<str>descriptor).encode("utf-8")
        spec = timespec(timeout, 0)
        self._client = new Client(desc.c_str(), &spec)
