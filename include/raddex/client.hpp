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

/// Supported scalar element types for RaDeX values.
enum DType {
    /// 32-bit signed integer element type.
    INT32,
    /// 64-bit signed integer element type.
    INT64,
    /// 64-bit floating point element type.
    FLOAT64,
};

/// Runtime variant used to map DType values to C++ types.
using _DType = std::variant<std::int32_t, std::int64_t, double>;

/// Compile-time mapping from DType enum to C++ types.
template <DType dtype> struct FromDType {
    using type = std::remove_reference_t<decltype(std::get<dtype>(
        std::declval<_DType>()))>;
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

/// Integer type used to represent sizes of variaous metadata fields
using MetaInt = std::uint64_t;

  public:
    BytesBuffer() : data{std::unique_ptr<std::uint8_t[]>(nullptr)}, length{0} {}
    BytesBuffer(std::unique_ptr<std::uint8_t[]> data, detail::MetaInt length)
        : data{std::move(data)}, length{length} {}

    BytesBuffer(const BytesBuffer &other) = delete;
    BytesBuffer(BytesBuffer &&other) noexcept
        : data{std::move(other.data)}, length{other.length} {
        other.length = 0;
    };
    BytesBuffer &operator=(const BytesBuffer &other) = delete;
    BytesBuffer &operator=(BytesBuffer &&other) noexcept {
        if (this != &other) {
            data = std::move(other.data);
            length = other.length;
            other.length = 0;
        }
        return *this;
    }
    ~BytesBuffer() = default;

    std::unique_ptr<std::uint8_t[]> release() {
        length = 0;
        return std::move(data);
    }

    const void *get_ptr() const { return data.get(); }
    detail::MetaInt get_length() const { return length; }
};

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
        return make_buffer(raddex::data::encode_type<T>(), dims, n_dims);
    }

    template <typename T> static MetaData make_scalar() {
        return make_buffer(raddex::data::encode_type<T>(), nullptr, 0);
    }

    static MetaData from_buffer(BytesBuffer buf);

    MetaInt n_dims() const { return get_buffer()[Index::N_DIMS]; }
    const MetaInt *dims_ptr() const { return dims_begin(); }
    MetaInt n_elements() const {
        return std::accumulate(dims_begin(), dims_end(), 1,
                               std::multiplies<MetaInt>());
    }
    const MetaInt *get_buffer() const {
        return static_cast<const MetaInt *>(buffer.get_ptr());
    }

    MetaInt size() const { return buffer.get_length(); }
    raddex::data::DType type() const {
        return static_cast<raddex::data::DType>(val_at(Index::TYPE));
    }

  private:
    MetaData(BytesBuffer buffer) : buffer{std::move(buffer)} {}
    static MetaData make_buffer(const raddex::data::DType dtype,
                                const MetaInt *dims, MetaInt n_dims);
    MetaInt val_at(MetaInt idx) const { return get_buffer()[idx]; }
    const MetaInt *dims_begin() const {
        return get_buffer() + Index::END_OF_HEADER;
    }
    const MetaInt *dims_end() const { return dims_begin() + n_dims(); }
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
        : dims{dims, dims + n_dims}, data{data, data + n_elements} {}

    TensorInfo(const TensorInfo &other) = delete;
    TensorInfo(TensorInfo &&other) = default;
    TensorInfo &operator=(const TensorInfo &other) = delete;
    TensorInfo &operator=(TensorInfo &&other) = default;
    ~TensorInfo() = default;
};

/// Abstract byte-addressable key-value client.
///
/// Concrete backends provide basic byte put/get primitives, while this class
/// offers typed scalar/tensor convenience helpers layered on top.
class IClient {
  public:
    // >>> Start Virtual Methods >>>

        /// Return true when the key exists in the backend store.
    virtual bool contains(const std::string &key) = 0;

        /// Store a byte buffer under the given key.
        ///
        /// @param key Key to store data at.
        /// @param bytes Pointer to buffer contents.
        /// @param length Number of bytes to write from bytes.
    virtual void put_bytes(const std::string &key, const void *bytes,
                           detail::MetaInt length) = 0;

        /// Retrieve the byte buffer associated with the given key.
        ///
        /// Ownership of the returned memory is transferred to the caller.
    virtual std::unique_ptr<uint8_t[]> get_bytes(const std::string &key) = 0;

        /// Virtual destructor for interface-safe polymorphic deletion.
    virtual ~IClient() {}

    // <<< End Virtual Methods <<<

    /// Store a typed scalar value by serializing its bytes.
    template <data::DType dtype>
    void put_scalar(const std::string &key,
                    const typename data::FromDType<dtype>::type &value) {
        put_bytes(key, &value, sizeof(typename data::FromDType<dtype>::type));
    }

    /// Load a typed scalar value by deserializing backend bytes.
    template <data::DType dtype>
    typename data::FromDType<dtype>::type get_scalar(const std::string &key) {
        using T = typename data::FromDType<dtype>::type;
        auto bytes = get_bytes(key);
        T converted;
        std::memcpy(&converted, info.data(), sizeof(T));
        return converted;
    }

    /// Store a typed tensor and its shape metadata.
    ///
    /// Metadata is stored at a key which contais rank and dimensions.
    template <data::DType dtype>
    void
    put_tensor(const std::string &key, const std::vector<detail::MetaInt> &dims,
               const std::vector<T> &data) {
        put_tensor<T>(key, dims.data(), dims.size(), data.data(), data.size());
    }

    /// Retrieve a typed tensor and reconstruct it using stored shape metadata.
    template <data::DType dtype>
    std::tuple<std::vector<detail::MetaInt>,
               std::vector<typename data::FromDType<dtype>::type>>
    get_tensor(const std::string &key) {
        using T = typename data::FromDType<dtype>::type;
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
        /// Build the metadata key used to store tensor shape information.
    std::string build_meta_key(const std::string &s) {
        return "__metadata::" + s;
    }

    detail::MetaData get_meta_data(const std::string &key) {
        auto meta_key = build_meta_key(key);
        return detail::MetaData::from_buffer(get_bytes(meta_key));
    }
};

} // namespace raddex

#endif
