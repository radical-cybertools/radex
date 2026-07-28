from libcpp.memory cimport unique_ptr
from libcpp.string cimport string
from libcpp.string_view cimport string_view

from Data cimport DType, MetaInt as size_t

cimport numpy as np
np.import_array()

cdef extern from "radex/client.hpp" namespace "radex::detail":
    cdef cppclass BytesBuffer:
        const void* get_ptr() except +
        size_t get_length() except +
        unique_ptr[np.uint8_t[]] release() except +

    cdef cppclass MetaData:
        size_t n_dims() except +
        const size_t *dims_ptr() except +
        size_t n_elements() except +
        DType type() except +

    cdef cppclass ItemInfo:
        const MetaData &metadata() except +
        const void *data() except +


cdef extern from "radex/client.hpp" namespace "radex":
    cdef cppclass IClient:
        bint contains(string_view) except +
        void put_bytes(string_view, const void*, size_t) except +
        BytesBuffer get_bytes(string_view) except +
        void put_scalar[T](string_view, T) except +
        void put_tensor[T](string_view,
                           const size_t*, size_t,
                           const T*, size_t) except +
        unique_ptr[ItemInfo] get_item_info_ptr(string_view) except +
