import cython

from libc.stdint cimport uint64_t, int32_t, int64_t
from libc.time cimport timespec
from libcpp.memory cimport unique_ptr
from libcpp.string cimport string
from libcpp_chrono cimport milliseconds

from Client cimport IClient
from Dragon cimport Client
from Data cimport (
    BytesBuffer,
    DType,
    ItemInfo,
    MetaInt as size_t,
    SupportedType,
    coerce_py_objects_to_np_numbers,
    construct_scalar,
    construct_tensor,
)

import cloudpickle

cimport numpy as np
import numpy as np
np.import_array()


ctypedef string EncodedStr


cdef inline EncodedStr _encode_str(str s):
    return s.encode("utf-8")


cdef class PyClient:
    cdef IClient *_client

    def __dealloc__(self):
        # TODO: The clients really should be using a unique_ptr instead
        if self._client != NULL:
            del self._client
            self._client = NULL

    def contains(self, str key):
        return self._client.contains(_encode_str(key).c_str())

    def put_scalar(self, str key, object value not None):
        cdef np.number val = coerce_py_objects_to_np_numbers(value)
        return self._put_scalar(key, val)

    def _put_scalar(self, str key, np.number value not None):
        cdef EncodedStr key_ = _encode_str(key)

        # FIXME: Get rid of this ugly swith statment. Ideally we could used the
        #        fused `SupportedType` type, but there seems to be a known
        #        issue with how it dispatches
        # https://github.com/cython/cython/issues/4932
        if isinstance(value, np.int32):
            return self._client.put_scalar[int32_t](key_.c_str(), value)
        if isinstance(value, np.int64):
            return self._client.put_scalar[int64_t](key_.c_str(), value)
        if isinstance(value, np.float32):
            return self._client.put_scalar[np.float32_t](key_.c_str(), value)
        if isinstance(value, np.float64):
            return self._client.put_scalar[np.float64_t](key_.c_str(), value)
        raise TypeError(f"Unsupported data type: {type(value)}")

    def get_scalar(self, str key):
        cdef EncodedStr key_ = _encode_str(key)
        cdef unique_ptr[ItemInfo] info = self._client.get_item_info_ptr(key_.c_str())
        return construct_scalar(info.get()[0])

    def wait_for_scalar(self, str key, float timeout):
        cdef EncodedStr key_ = _encode_str(key)
        cdef milliseconds timeout_ = milliseconds(<int64_t>(timeout * 1000))
        cdef unique_ptr[ItemInfo] info = self._client.wait_for_item_info_ptr(
                key_.c_str(), timeout_)
        return construct_scalar(info.get()[0])

    def put_tensor(self, str key, np.ndarray tensor not None):
        cdef np.ndarray[np.uintp_t, ndim=1] dims_arr = np.asarray(
                (<object>tensor).shape, dtype=np.uintp)
        self._put_tensor(key, dims_arr, tensor.ravel())

    def _put_tensor(
        self,
        str key,
        const size_t[:] dims not None,
        const SupportedType[:] data not None,
    ):
        cdef EncodedStr key_ = _encode_str(key)
        return self._client.put_tensor(key_.c_str(),
                                       &dims[0], dims.size,
                                       &data[0], data.size)

    def get_tensor(self, str key):
        cdef string key_ = _encode_str(key)
        cdef unique_ptr[ItemInfo] info = self._client.get_item_info_ptr(key_.c_str())
        return construct_tensor(info.get()[0])

    def wait_for_tensor(self, str key, float timeout):
        cdef EncodedStr key_ = _encode_str(key)
        cdef milliseconds timeout_ = milliseconds(<int64_t>(timeout * 1000))
        cdef unique_ptr[ItemInfo] info = self._client.wait_for_item_info_ptr(
                key_.c_str(), timeout_)
        return construct_tensor(info.get()[0])

    def put_picklable(self, str key, object picklable):
        cdef string key_ = _encode_str(key)
        cdef bytes bytes_ = cloudpickle.dumps(picklable)
        cdef void* ptr = <void*><char*>bytes_
        cdef size_t len_ = len(bytes_)
        self._client.put_bytes(key_.c_str(), ptr, len_)

    def get_picklable(self, str key):
        cdef string key_ = _encode_str(key)
        cdef BytesBuffer buf = self._client.get_bytes(key_.c_str())

        cdef size_t len_ = buf.get_length()
        cdef np.uint8_t *ptr = <np.uint8_t*>buf.get_ptr()

        cdef bytes bytes_ = <bytes>ptr[:len_]
        return cloudpickle.loads(bytes_)

    def wait_for_picklable(self, str key, float timeout):
        cdef string key_ = _encode_str(key)
        cdef milliseconds timeout_ = milliseconds(<int64_t>(timeout * 1000))
        cdef BytesBuffer buf = self._client.wait_for_bytes(key_.c_str(), timeout_)

        cdef size_t len_ = buf.get_length()
        cdef np.uint8_t *ptr = <np.uint8_t*>buf.get_ptr()

        cdef bytes bytes_ = <bytes>ptr[:len_]
        return cloudpickle.loads(bytes_)


cdef class DragonClient(PyClient):
    def __cinit__(
        self, descriptor: str | None = None, timeout: int | None = None
    ):
        if (descriptor is None) and (timeout is None):
            self._init_from_env()
        elif (descriptor is not None) and (timeout is not None):
            self._init_from_args(descriptor, timeout)
        else:
            raise ValueError(
                "Both descriptor and timeout must be set or both be None"
            )

    cdef void _init_from_env(self):
        self._client = new Client()

    cdef void _init_from_args(self, str descriptor, int timeout):
        if len(descriptor) == 0:
            raise ValueError("DDict descriptor cannot be an empty string")
        if timeout < 0:
            raise ValueError("timeout must be positive")
        cdef EncodedStr desc = _encode_str(descriptor)
        cdef timespec spec = timespec(timeout, 0)
        self._client = new Client(desc.c_str(), &spec)
