#include "radex/handles.hpp"
#include "radex/handles_c.h"
#include "radex/macros/radex_c_error_macros.h"

#include <cstring>
#include <new>
#include <sstream>
#include <string>

namespace radex::data {

auto IncomingHandle::key() const -> std::string {
    std::ostringstream key;
    key << name;
    return key.str();
}

auto IncomingHandle::metadata_key() const -> std::string {
    std::ostringstream meta;
    meta << "metadata::" << key();
    return meta.str();
}

auto OutgoingHandle::key() const -> std::string {
    std::ostringstream key;
    key << name;
    return key.str();
}

auto OutgoingHandle::metadata_key() const -> std::string {
    std::ostringstream meta;
    meta << "metadata::" << key();
    return meta.str();
}

} // namespace radex::data

/* C API implementations */
extern "C" {

int radex_incoming_handle_create(const char* name,
                                 radex_incoming_handle_t** out_handle) {
    *out_handle = nullptr;
    try {
        *out_handle = reinterpret_cast<radex_incoming_handle_t*>(
            new radex::data::IncomingHandle(name));
        return RADEX_OK;
    } RADEX_C_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN)
}

int radex_incoming_handle_destroy(radex_incoming_handle_t* handle) {
    delete reinterpret_cast<radex::data::IncomingHandle*>(handle);
    return RADEX_OK;
}

int radex_outgoing_handle_create(const char* name,
                                 radex_outgoing_handle_t** out_handle) {
    *out_handle = nullptr;
    try {
        *out_handle = reinterpret_cast<radex_outgoing_handle_t*>(
            new radex::data::OutgoingHandle(name));
        return RADEX_OK;
    } RADEX_C_CATCH_EXCEPTIONS(RADEX_ERR_UNKNOWN)
}

int radex_outgoing_handle_destroy(radex_outgoing_handle_t* handle) {
    delete reinterpret_cast<radex::data::OutgoingHandle*>(handle);
    return RADEX_OK;
}

} // extern "C"
