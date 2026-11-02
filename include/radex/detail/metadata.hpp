#ifndef __RADEX_DETAIL_METADATA__
#define __RADEX_DETAIL_METADATA__

#include "radex/data.hpp"
#include "radex/detail/bytes_buffer.hpp"
#include "radex/detail/types.hpp"

#include <utility>

namespace radex {
namespace detail {

class MetaData {
    BytesBuffer buffer;

  private:
    struct Index {
        enum {
            TYPE = 0,
            N_DIMS,
            END_OF_HEADER,
        };
    };

  public:
    template <typename T>
    static MetaData make_tensor(const MetaInt *dims, MetaInt n_dims) {
        return make_buffer(radex::data::encode_type<T>(), dims, n_dims);
    }

    template <typename T> static MetaData make_scalar() {
        return make_buffer(radex::data::encode_type<T>(), nullptr, 0);
    }

    static MetaData from_buffer(BytesBuffer buf);

    auto n_dims() const -> MetaInt { return get_buffer()[Index::N_DIMS]; }
    auto dims_ptr() const -> const MetaInt * { return dims_begin(); }
    auto n_elements() const -> MetaInt;
    auto get_buffer() const -> const MetaInt * {
        return static_cast<const MetaInt *>(buffer.get_ptr());
    }

    auto size() const -> MetaInt { return buffer.get_length(); }
    auto type() const -> radex::data::DType {
        return static_cast<radex::data::DType>(val_at(Index::TYPE));
    }

  private:
    MetaData(BytesBuffer buffer) : buffer{std::move(buffer)} {}
    static auto make_buffer(const radex::data::DType dtype, const MetaInt *dims,
                            MetaInt n_dims) -> MetaData;
    MetaInt val_at(MetaInt idx) const { return get_buffer()[idx]; }
    auto dims_begin() const -> const MetaInt * {
        return get_buffer() + Index::END_OF_HEADER;
    }
    auto dims_end() const -> const MetaInt * { return dims_begin() + n_dims(); }
};

} // namespace detail
} // namespace radex

#endif
