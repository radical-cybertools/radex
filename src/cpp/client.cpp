#include "radex/client.hpp"

#include <cstring>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>

namespace radex {
namespace detail {

BytesBuffer::BytesBuffer(BytesBuffer &&other) noexcept
    : data{std::move(other.data)}, length{other.length} {
    other.length = 0;
};

BytesBuffer &BytesBuffer::operator=(BytesBuffer &&other) noexcept {
    if (this != &other) {
        length = other.length;
        data = other.release();
    }
    return *this;
}

std::unique_ptr<std::uint8_t[]> BytesBuffer::release() noexcept {
    length = 0;
    return std::move(data);
}

MetaData MetaData::from_buffer(BytesBuffer buffer) {
    MetaData meta{std::move(buffer)};
    MetaInt expected_size =
        (meta.n_dims() + Index::END_OF_HEADER) * sizeof(MetaInt);
    if (meta.size() != expected_size) {
        throw std::runtime_error("Malformed item metadata buffer received");
    }
    return meta;
}

MetaData MetaData::make_buffer(const radex::data::DType dtype,
                               const MetaInt *dims, MetaInt n_dims) {
    MetaInt n_bytes = (n_dims + Index::END_OF_HEADER) * sizeof(MetaInt);
    auto bytes = std::make_unique<std::uint8_t[]>(n_bytes);

    auto buf = static_cast<MetaInt *>(static_cast<void *>(bytes.get()));
    buf[Index::TYPE] = static_cast<MetaInt>(dtype);
    buf[Index::N_DIMS] = n_dims;
    std::memcpy(buf + Index::END_OF_HEADER, dims, n_dims * sizeof(*dims));

    return {BytesBuffer{std::move(bytes), n_bytes}};
}

} // namespace detail

detail::ItemInfo IClient::get_item_info(std::string_view key) {
    auto buf = get_bytes(key);
    return {get_meta_data(key), buf.release()};
}

std::unique_ptr<detail::ItemInfo>
IClient::get_item_info_ptr(std::string_view key) {
    return std::make_unique<detail::ItemInfo>(get_meta_data(key),
                                              get_bytes(key).release());
}

std::string IClient::build_meta_key(std::string_view s) const {
    std::ostringstream meta;
    meta <<  "__metadata::" << s;
    return meta.str();
}

detail::MetaData IClient::get_meta_data(std::string_view key) {
    auto meta_key = build_meta_key(key);
    return detail::MetaData::from_buffer(get_bytes(meta_key));
}

} // namespace radex
