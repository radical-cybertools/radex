#include "radex/handles.hpp"
#include "radex/handles_c.h"

#include <cstring>
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

radex_incoming_handle* radex_incoming_handle_create(const char* name) {
    try {
        return reinterpret_cast<radex_incoming_handle*>(
            new radex::data::IncomingHandle(name));
    } catch (...) {
        return nullptr;
    }
}

void radex_incoming_handle_destroy(radex_incoming_handle* handle) {
    if (handle != nullptr) {
        delete reinterpret_cast<radex::data::IncomingHandle*>(handle);
    }
}

radex_outgoing_handle* radex_outgoing_handle_create(const char* name) {
    try {
        return reinterpret_cast<radex_outgoing_handle*>(
            new radex::data::OutgoingHandle(name));
    } catch (...) {
        return nullptr;
    }
}

void radex_outgoing_handle_destroy(radex_outgoing_handle* handle) {
    if (handle != nullptr) {
        delete reinterpret_cast<radex::data::OutgoingHandle*>(handle);
    }
}

} // extern "C"
