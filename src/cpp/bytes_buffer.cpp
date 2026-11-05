#include "radex/detail/bytes_buffer.hpp"

#include <cstdint>
#include <memory>
#include <utility>

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

auto BytesBuffer::release() noexcept -> std::unique_ptr<std::uint8_t[]> {
    length = 0;
    return std::move(data);
}

} // namespace detail
} // namespace radex
