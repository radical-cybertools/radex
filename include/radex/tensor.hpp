#ifndef __RADEX_TENSOR_HPP___
#define __RADEX_TENSOR_HPP___

#include "radex/detail/types.hpp"

#include <vector>

namespace radex {

/// The result of reading a tensor: its shape and flattened element data.
template <typename T> struct TensorInfo {
    /// The tensor's dimensions, outermost first.
    std::vector<detail::MetaInt> dims;
    /// The tensor's elements in row-major (C) order.
    std::vector<T> data;

  public:
    TensorInfo(const T *data, detail::MetaInt n_elements,
               const detail::MetaInt *dims, detail::MetaInt n_dims)
        : dims{dims, dims + n_dims}, data{data, data + n_elements} {}

    TensorInfo(const TensorInfo &other) = delete;
    TensorInfo(TensorInfo &&other) = default;
    TensorInfo &operator=(const TensorInfo &other) = delete;
    TensorInfo &operator=(TensorInfo &&other) = default;
    ~TensorInfo() = default;
};

} // namespace radex

#endif
