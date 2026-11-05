#include "radex/detail/metadata.hpp"
#include "radex/data.hpp"
#include "radex/detail/bytes_buffer.hpp"
#include "radex/detail/types.hpp"
#include "radex/exceptions.hpp"

#include <cstdint>
#include <cstring>
#include <functional>
#include <memory>
#include <numeric>
#include <utility>

namespace radex {
namespace detail {

auto MetaData::from_buffer(BytesBuffer buffer) -> MetaData {
    MetaData meta{std::move(buffer)};
    MetaInt expected_size =
        (meta.n_dims() + Index::END_OF_HEADER) * sizeof(MetaInt);
    if (meta.size() != expected_size) {
        throw radex::MetadataError("Malformed item metadata buffer received");
    }
    return meta;
}

auto MetaData::make_buffer(const radex::data::DType dtype, const MetaInt *dims,
                           MetaInt n_dims) -> MetaData {
    MetaInt n_bytes = (n_dims + Index::END_OF_HEADER) * sizeof(MetaInt);
    auto bytes = std::make_unique<std::uint8_t[]>(n_bytes);

    auto buf = static_cast<MetaInt *>(static_cast<void *>(bytes.get()));
    buf[Index::TYPE] = static_cast<MetaInt>(dtype);
    buf[Index::N_DIMS] = n_dims;
    std::memcpy(buf + Index::END_OF_HEADER, dims, n_dims * sizeof(*dims));

    return {BytesBuffer{std::move(bytes), n_bytes}};
}

auto MetaData::n_elements() const -> MetaInt {
    return std::accumulate(dims_begin(), dims_end(), 1,
                           std::multiplies<MetaInt>());
}

} // namespace detail

} // namespace radex
