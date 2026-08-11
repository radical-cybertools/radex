from libcpp.memory cimport unique_ptr
from libcpp.string cimport string
from libcpp.string_view cimport string_view

cdef extern from "radex/handles.hpp" namespace "radex::data":
    cdef cppclass IHandle:
        string key() except +
        string metadata_key() except +

    cdef cppclass IncomingHandle(IHandle):
        IncomingHandle(string_view)

    cdef cppclass OutgoingHandle(IHandle):
        OutgoingHandle(string_view)


cdef class PyIncomingHandle:
    cdef unique_ptr[IncomingHandle] _handle
    cdef IncomingHandle* unwrap(self)


cdef class PyOutgoingHandle:
    cdef unique_ptr[OutgoingHandle] _handle
    cdef OutgoingHandle* unwrap(self)
