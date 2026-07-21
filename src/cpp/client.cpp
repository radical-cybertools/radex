#include "radex/client.hpp"

namespace radex {
namespace detail {

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

} // namespace radex
