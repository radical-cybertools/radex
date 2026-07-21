from libc.time cimport timespec

from Client cimport IClient


cdef extern from "radex/dragon.hpp" namespace "radex::drg::ddict":
    cdef cppclass Client(IClient):
        Client(const char*, const timespec*) except +
