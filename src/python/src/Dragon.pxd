from libc.time cimport timespec

from Client cimport IClient


cdef extern from "raddex/dragon.hpp" namespace "raddex::drg::ddict":
    cdef cppclass Client(IClient):
        Client(const char*, const timespec*) except +
