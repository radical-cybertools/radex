from libcpp.string_view cimport string_view

from radex.clients.core cimport IClient


cdef extern from "radex/smartredis.hpp" namespace "radex::redis::smartredis":
    cdef cppclass Client(IClient):
        Client() except +
        Client(string_view) except +
