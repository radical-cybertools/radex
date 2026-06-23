#ifndef __RADDEX_CLIENT_HPP__
#define __RADDEX_CLIENT_HPP__

#include <cstdint>
#include <cstring>
#include <memory>
#include <numeric>
#include <string>
#include <type_traits>
#include <variant>
#include <vector>

namespace raddex {

namespace data {

enum DType {
    INT32,
    INT64,
    FLOAT64,
};

using _DType = std::variant<std::int32_t, std::int64_t, double>;

template <DType dtype> struct FromDType {
    using type = std::remove_reference_t<decltype(std::get<dtype>(
        std::declval<_DType>()))>;
};

} // namespace data

namespace detail {

using MetaInt = std::uint64_t;

}

class IClient {
  public:
    // >>> Start Virtual Methods >>>

    virtual bool contains(const std::string &key) = 0;
    virtual void put_bytes(const std::string &key, const void *bytes,
                           detail::MetaInt length) = 0;
    virtual std::unique_ptr<uint8_t[]> get_bytes(const std::string &key) = 0;
    virtual ~IClient() {}

    // <<< End Virtual Methods <<<

    template <data::DType dtype>
    void put_scalar(const std::string &key,
                    const typename data::FromDType<dtype>::type &value) {
        put_bytes(key, &value, sizeof(typename data::FromDType<dtype>::type));
    }

    template <data::DType dtype>
    typename data::FromDType<dtype>::type get_scalar(const std::string &key) {
        using T = typename data::FromDType<dtype>::type;
        auto bytes = get_bytes(key);
        T converted;
        std::memcpy(&converted, bytes.get(), sizeof(T));
        return converted;
    }

    template <data::DType dtype>
    void
    put_tensor(const std::string &key, const std::vector<detail::MetaInt> &dims,
               const std::vector<typename data::FromDType<dtype>::type> &data) {
        using T = typename data::FromDType<dtype>::type;
        std::string metakey = build_meta_key(key);
        detail::MetaInt ndims = dims.size();

        std::vector<detail::MetaInt> metadata;
        metadata.push_back(dims.size());
        for (auto &d : dims) {
            metadata.push_back(d);
        }

        put_bytes(metakey, metadata.data(),
                  metadata.size() * sizeof(detail::MetaInt));
        put_bytes(key, data.data(), data.size() * sizeof(T));
    }

    template <data::DType dtype>
    std::tuple<std::vector<detail::MetaInt>,
               std::vector<typename data::FromDType<dtype>::type>>
    get_tensor(const std::string &key) {
        using T = typename data::FromDType<dtype>::type;
        std::string metakey = build_meta_key(key);
        auto meta_buf = get_bytes(metakey);
        const detail::MetaInt *meta_ptr =
            static_cast<detail::MetaInt *>(static_cast<void *>(meta_buf.get()));

        detail::MetaInt ndims = *meta_ptr;
        std::vector<detail::MetaInt> dims{(meta_ptr + 1),
                                          (meta_ptr + 1) + ndims};
        detail::MetaInt n_elements = std::reduce(
            dims.begin(), dims.end(), 1, std::multiplies<detail::MetaInt>());

        auto data_buf = get_bytes(key);
        const T *data_ptr =
            static_cast<T *>(static_cast<void *>(data_buf.get()));
        std::vector<T> data{data_ptr, data_ptr + n_elements};

        return {dims, data};
    }

  private:
    std::string build_meta_key(const std::string &s) {
        return "__metadata::" + s;
    }
};

} // namespace raddex

#endif
