#ifndef __RADEX_DETAIL_ITEM_INFO__
#define __RADEX_DETAIL_ITEM_INFO__

#include "radex/detail/metadata.hpp"
#include "radex/detail/types.hpp"

#include <memory>
#include <utility>

namespace radex {
namespace detail {

class ItemInfo {
    MetaData _metadata;
    std::unique_ptr<std::uint8_t[]> _data;

  public:
    ItemInfo(MetaData metadata, std::unique_ptr<std::uint8_t[]> data)
        : _metadata{std::move(metadata)}, _data{std::move(data)} {};
    const MetaData &metadata() const { return _metadata; }
    const void *data() const { return _data.get(); }
};

} // namespace detail
} // namespace radex

#endif
