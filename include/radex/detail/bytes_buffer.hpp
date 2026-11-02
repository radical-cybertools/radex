#ifndef __RADEX_DETAIL_BYTES_BUFFER__
#define __RADEX_DETAIL_BYTES_BUFFER__

#include "radex/detail/types.hpp"

#include <cstdint>
#include <memory>
#include <utility>

namespace radex {
namespace detail {

class BytesBuffer {
    std::unique_ptr<std::uint8_t[]> data;
    detail::MetaInt length;

  public:
    BytesBuffer() : data{std::unique_ptr<std::uint8_t[]>(nullptr)}, length{0} {}
    BytesBuffer(std::unique_ptr<std::uint8_t[]> data, detail::MetaInt length)
        : data{std::move(data)}, length{length} {}

    BytesBuffer(const BytesBuffer &other) = delete;
    BytesBuffer(BytesBuffer &&other) noexcept;
    BytesBuffer &operator=(const BytesBuffer &other) = delete;
    BytesBuffer &operator=(BytesBuffer &&other) noexcept;
    ~BytesBuffer() = default;

    auto release() noexcept -> std::unique_ptr<std::uint8_t[]>;
    auto get_ptr() const -> const void * { return data.get(); }
    auto get_length() const -> detail::MetaInt { return length; }
};

} // namespace detail
} // namespace radex

#endif
