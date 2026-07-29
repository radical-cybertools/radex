from libcpp.memory cimport unique_ptr
from libcpp.string cimport string
from libcpp.string_view cimport string_view
from libcpp_chrono cimport milliseconds

from Data cimport (
    BytesBuffer,
    DType,
    ItemInfo,
    MetaInt as size_t,
)

cimport numpy as np
np.import_array()

cdef extern from "radex/client.hpp" namespace "radex":
    cdef cppclass IClient:
        bint contains(string_view) except +
        void put_bytes(string_view, const void*, size_t) except +
        BytesBuffer get_bytes(string_view) except +
        BytesBuffer wait_for_bytes(string_view, milliseconds) except +
        void put_scalar[T](string_view, T) except +
        void put_tensor[T](string_view,
                           const size_t*, size_t,
                           const T*, size_t) except +
        unique_ptr[ItemInfo] get_item_info_ptr(string_view) except +
        unique_ptr[ItemInfo] wait_for_item_info_ptr(
                string_view, milliseconds) except +
