from libcpp.memory cimport unique_ptr
from libcpp.string cimport string
from libcpp.string_view cimport string_view

from radex.utils.libcpp_chrono cimport milliseconds
from radex.utils.data cimport (
    BytesBuffer,
    DType,
    ItemInfo,
    MetaInt as size_t,
)
from radex.handles.handles cimport (
    CXXIncomingHandle as IncomingHandle,
    CXXOutgoingHandle as OutgoingHandle,
)

cimport numpy as np
np.import_array()

cdef extern from "radex/client.hpp" namespace "radex":
    cdef cppclass IClient:
        # >>> Start Virtual Methods >>>
        bint contains(string_view) except +
        void put_bytes(string_view, const void*, size_t) except +
        BytesBuffer get_bytes(string_view) except +
        BytesBuffer wait_for_bytes(string_view, milliseconds) except +
        # <<< End Virtual Methods <<<

        void put_scalar[T](const OutgoingHandle&, T) except +
        void put_tensor[T](const OutgoingHandle&,
                           const size_t*, size_t,
                           const T*, size_t) except +

        unique_ptr[ItemInfo] get_item_info_ptr(const IncomingHandle&) except +
        unique_ptr[ItemInfo] wait_for_item_info_ptr(
                const IncomingHandle&, milliseconds) except +
