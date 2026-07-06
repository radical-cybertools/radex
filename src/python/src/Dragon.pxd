from libcpp.string cimport string
from libcpp.vector cimport vector
from libc.time cimport timespec
from libcpp.memory cimport unique_ptr

cimport numpy as np

from Data cimport DType

np.import_array()

cdef extern from "raddex/client.hpp" namespace "raddex::detail":
    cdef cppclass MetaData:
        np.uint64_t n_dims() except +
        np.uint64_t *dims_ptr() except +
        np.uint64_t n_elements() except +
        DType type() except +

    cdef cppclass ItemInfo:
        const MetaData &metadata() except +
        const void *data() except +

cdef extern from "raddex/dragon.hpp" namespace "raddex::drg::ddict":
    cdef cppclass Client:
        Client(const char*, const timespec*) except +
        bint contains(const string&) except +
        void put_scalar[T](const string&, T) except +
        void put_tensor[T](const string&,
                           const np.uint64_t*, np.uint64_t,
                           const T*, np.uint64_t) except +
        unique_ptr[ItemInfo] get_item_info_ptr(const string& key) except +
