#ifndef __RADDEX_CLIENT_HPP__
#define __RADDEX_CLIENT_HPP__

#include <cstdint>
#include <cstring>
#include <memory>
#include <numeric>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>

namespace raddex {

namespace detail {
using MetaInt = std::uint64_t;
}

namespace data {

template <typename... Ts> struct TypeSet {};

using ValidTypes = TypeSet<std::int32_t, std::int64_t, double>;

template <typename T, typename Set, raddex::detail::MetaInt i = 0>
struct get_index {};

template <typename T, typename U, typename... Rest, raddex::detail::MetaInt i>
struct get_index<T, TypeSet<U, Rest...>, i>
    : std::conditional<std::is_same<T, U>::value,
                       std::integral_constant<raddex::detail::MetaInt, i>,
                       get_index<T, TypeSet<Rest...>, i + 1>>::type {};

template <typename T> struct enumerate_type : get_index<T, ValidTypes> {};

template <typename, typename = void>
struct has_value_member : std::false_type {};

template <typename T>
struct has_value_member<T, std::void_t<decltype(&T::value)>> : std::true_type {
};

template <typename T>
struct is_supported_type
    : std::integral_constant<bool, has_value_member<enumerate_type<T>>::value> {
};

// FIXME: I would really prefer to see this created dynamically when adding to
//        the `ValidTypes` set, or vice-versa.
enum class DType : raddex::detail::MetaInt {
    INT32 = enumerate_type<std::int32_t>::value,
    INT64 = enumerate_type<std::int64_t>::value,
    FLOAT64 = enumerate_type<double>::value
};

template <typename T>
typename std::enable_if<is_supported_type<T>::value, DType>::type
encode_type() {
    return static_cast<DType>(enumerate_type<T>::value);
}

} // namespace data

namespace detail {

class MetaData {
    std::unique_ptr<MetaInt[]> buffer;

  public:
    template <typename T>
    static MetaData make_tensor(const MetaInt *dims, MetaInt n_dims) {
        return make_buffer(raddex::data::encode_type<T>(), dims, n_dims);
    }

    template <typename T> static MetaData make_scalar() {
        return make_buffer(raddex::data::encode_type<T>(), nullptr, 0);
    }

    MetaData(std::unique_ptr<MetaInt[]> ptr) : buffer{std::move(ptr)} {}

    MetaInt n_dims() const { return buffer[Index::N_DIMS]; }
    MetaInt *dims_ptr() const { return dims_begin(); }
    MetaInt n_elements() const {
        return std::accumulate(dims_begin(), dims_end(), 1,
                               std::multiplies<detail::MetaInt>());
    }
    const MetaInt *get_buffer() const { return buffer.get(); }
    MetaInt size() const {
        return (n_dims() + Index::END_OF_HEADER) * sizeof(buffer[0]);
    }
    raddex::data::DType type() const {
        return static_cast<raddex::data::DType>(buffer[Index::TYPE]);
    }

  private:
    static MetaData make_buffer(const raddex::data::DType dtype,
                                const MetaInt *dims, MetaInt n_dims) {
        auto buf = std::make_unique<MetaInt[]>(n_dims + Index::END_OF_HEADER);
        buf[Index::TYPE] = static_cast<MetaInt>(dtype);
        buf[Index::N_DIMS] = n_dims;
        std::memcpy(buf.get() + Index::END_OF_HEADER, dims,
                    n_dims * sizeof(*dims));
        return {std::move(buf)};
    }
    MetaInt *dims_begin() const { return buffer.get() + Index::END_OF_HEADER; }
    MetaInt *dims_end() const { return dims_begin() + n_dims(); }

    struct Index {
        enum {
            TYPE = 0,
            N_DIMS,
            END_OF_HEADER,
        };
    };
};

class BytesBuffer {
    std::unique_ptr<std::uint8_t[]> data;
    detail::MetaInt length;

  public:
    BytesBuffer() : data{std::unique_ptr<std::uint8_t[]>(nullptr)}, length{0} {}
    BytesBuffer(std::unique_ptr<std::uint8_t[]> data, detail::MetaInt length)
        : data{std::move(data)}, length{length} {}

    BytesBuffer(const BytesBuffer &other) = delete;

    // FIXME: Need to zero out the length member on move
    //        but this was leading to some problems with Python compatibility.
    //        This is an internal(ish) class, so this is OK for now, but should
    //        be fixed later.
    BytesBuffer(BytesBuffer &&other) = default;
    BytesBuffer &operator=(const BytesBuffer &other) = delete;
    BytesBuffer &operator=(BytesBuffer &&other) = default;
    ~BytesBuffer() = default;

    std::unique_ptr<std::uint8_t[]> release() {
        length = 0;
        return std::move(data);
    }

    const void *get_ptr() const { return data.get(); }
    detail::MetaInt get_length() const { return length; }
};

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

template <typename T> struct TensorInfo {
    std::vector<detail::MetaInt> dims;
    std::vector<T> data;

  public:
    TensorInfo(const T *data, detail::MetaInt n_elements,
               const detail::MetaInt *dims, detail::MetaInt n_dims)
        : data{data, data + n_elements}, dims{dims, dims + n_dims} {}

    TensorInfo(const TensorInfo &other) = delete;
    TensorInfo(TensorInfo &&other) = default;
    TensorInfo &operator=(const TensorInfo &other) = delete;
    TensorInfo &operator=(TensorInfo &&other) = default;
    ~TensorInfo() = default;
};

class IClient {
  public:
    // >>> Start Virtual Methods >>>

    virtual bool contains(const std::string &key) = 0;
    virtual void put_bytes(const std::string &key, const void *bytes,
                           detail::MetaInt length) = 0;
    virtual detail::BytesBuffer get_bytes(const std::string &key) = 0;
    virtual ~IClient() {}

    // <<< End Virtual Methods <<<

    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value, void>::type
    put_scalar(const std::string &key, const T &value) {
        std::string metakey = build_meta_key(key);
        auto meta = detail::MetaData::make_scalar<T>();
        put_bytes(metakey, meta.get_buffer(), meta.size());
        put_bytes(key, &value, sizeof(T));
    }

    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value, T>::type
    get_scalar(const std::string &key) {
        const auto info = get_item_info(key);
        if (info.metadata().n_dims() != 0) {
            // TODO: Better error type/message here
            throw std::runtime_error(
                "Attempted to retrieve scalar at a key with a vector");
        }
        if (info.metadata().type() != data::encode_type<T>()) {
            // TODO: Better error type/message here
            throw std::runtime_error(
                "Attempted to retrieve scalar of mismatched type");
        }
        T converted;
        std::memcpy(&converted, info.data(), sizeof(T));
        return converted;
    }

    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value, void>::type
    put_tensor(const std::string &key, const std::vector<detail::MetaInt> &dims,
               const std::vector<T> &data) {
        put_tensor<T>(key, dims.data(), dims.size(), data.data(), data.size());
    }

    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value, void>::type
    put_tensor(const std::string &key, const detail::MetaInt *dims,
               detail::MetaInt n_dims, const T *elements,
               detail::MetaInt n_elements) {
        std::string metakey = build_meta_key(key);
        auto meta = detail::MetaData::make_tensor<T>(dims, n_dims);
        put_bytes(metakey, meta.get_buffer(), meta.size());
        put_bytes(key, elements, n_elements * sizeof(T));
    }

    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value,
                            TensorInfo<T>>::type
    get_tensor(const std::string &key) {
        const auto info = get_item_info(key);
        if (info.metadata().n_dims() == 0) {
            // TODO: Better error type/message here
            throw std::runtime_error(
                "Attempted to retrieve vector at a key with a scalar");
        }
        if (info.metadata().type() != data::encode_type<T>()) {
            // TODO: Better error type/message here
            throw std::runtime_error(
                "Attempted to retrieve vector of mismatched type");
        }

        const T *data_ptr = static_cast<const T *>(info.data());
        return {data_ptr, info.metadata().n_elements(),
                info.metadata().dims_ptr(), info.metadata().n_dims()};
    }

    detail::ItemInfo get_item_info(const std::string &key) {
        auto buf = get_bytes(key);
        return {get_meta_data(key), buf.release()};
    }

    std::unique_ptr<detail::ItemInfo>
    get_item_info_ptr(const std::string &key) {
        return std::make_unique<detail::ItemInfo>(get_meta_data(key),
                                                  get_bytes(key).release());
    }

  private:
    std::string build_meta_key(const std::string &s) {
        return "__metadata::" + s;
    }

    detail::MetaData get_meta_data(const std::string &key) {
        auto meta_key = build_meta_key(key);
        auto buf = get_bytes(meta_key);
        auto original_size = buf.get_length();

        // FIXME: Need use the deleter from the original unique ptr
        auto p = static_cast<detail::MetaInt *>(
            static_cast<void *>(buf.release().release()));
        std::unique_ptr<detail::MetaInt[]> arr{p};

        detail::MetaData meta{std::move(arr)};
        if (original_size != meta.size()) {
            // TODO: Better error msg/type here
            throw std::runtime_error("Malformed item metadata buffer recieved");
        }
        return meta;
    }
};

} // namespace raddex

#endif
