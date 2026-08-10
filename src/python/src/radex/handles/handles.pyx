import cython

from libcpp.memory cimport unique_ptr, make_unique

from radex.utils.utils cimport encode_str, EncodedStr
from radex.handles.handles cimport IncomingHandle, OutgoingHandle


cdef class PyIncomingHandle:
    def __cinit__(self, str handle_id):
        cdef EncodedStr id_ = encode_str(handle_id)
        self._handle = make_unique[IncomingHandle](id_.c_str())

    cdef IncomingHandle* unwrap(self):
        return self._handle.get()


cdef class PyOutgoingHandle:
    def __cinit__(self, str handle_id):
        cdef EncodedStr id_ = encode_str(handle_id)
        self._handle = make_unique[OutgoingHandle](id_.c_str())

    cdef OutgoingHandle* unwrap(self):
        return self._handle.get()
