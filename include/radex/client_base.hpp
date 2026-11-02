#ifndef __RADEX_CLIENT_BASE_HPP__
#define __RADEX_CLIENT_BASE_HPP__

#include "radex/data.hpp"
#include "radex/detail/bytes_buffer.hpp"
#include "radex/detail/item_info.hpp"
#include "radex/detail/metadata.hpp"
#include "radex/detail/types.hpp"
#include "radex/exceptions.hpp"
#include "radex/handles.hpp"
#include "radex/tensor.hpp"

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <memory>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

namespace radex {

/// Abstract base class for all RaDex backend clients (Dragon, SmartRedis, ...).
///
/// Provides typed `put_scalar`/`get_scalar`/`put_tensor`/`get_tensor` (and
/// their `wait_for_*` blocking variants) on top of the raw byte-oriented
/// `put_bytes`/`get_bytes`/`wait_for_bytes` methods that concrete backends
/// implement.
class IClient {
  public:
    // >>> Start Virtual Methods >>>

    /// @return True if `key` exists in the backing store.
    virtual bool contains(std::string_view key) = 0;
    /// Store raw bytes under `key`, overwriting any existing value.
    virtual void put_bytes(std::string_view key, const void *bytes,
                           detail::MetaInt length) = 0;
    /// @return The raw bytes previously stored under `key`.
    virtual detail::BytesBuffer get_bytes(std::string_view key) = 0;
    /// Block until `key` becomes available, then return its raw bytes.
    /// @param timeout Maximum time to wait for the key to appear.
    virtual detail::BytesBuffer
    wait_for_bytes(std::string_view key, std::chrono::milliseconds timeout) = 0;
    virtual ~IClient() {}

    // <<< End Virtual Methods <<<

  private:
    /// Delete the entry stored under `key` in the backing store.
    virtual void delete_key(std::string_view key) = 0;

    detail::ItemInfo get_item_info(
        std::function<detail::BytesBuffer(std::string_view)> fetch_bytes,
        const data::IncomingHandle &handle);
    detail::MetaData get_meta_data(const data::IncomingHandle &handle);

  public:
    std::unique_ptr<detail::ItemInfo>
    get_item_info_ptr(const data::IncomingHandle &handle);
    std::unique_ptr<detail::ItemInfo>
    wait_for_item_info_ptr(const data::IncomingHandle &handle,
                           std::chrono::milliseconds timeout);

    /// Delete a typed value and its associated metadata.
    void delete_item(const data::OutgoingHandle &handle);

  public:
    /// Store a scalar value under `handle`.
    /// @tparam T One of `int32_t`, `int64_t`, `float`, `double`.
    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value, void>::type
    put_scalar(const data::OutgoingHandle &handle, const T &value) {
        auto meta = detail::MetaData::make_scalar<T>();
        put_bytes(handle.metadata_key(), meta.get_buffer(), meta.size());
        put_bytes(handle.key(), &value, sizeof(T));
    }

    /// @return The scalar value previously written under `handle`.
    /// @throws std::runtime_error If the stored value is a tensor, or its
    ///     type does not match `T`.
    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value, T>::type
    get_scalar(const data::IncomingHandle handle) {
        const auto fetch =
            std::bind(&IClient::get_bytes, this, std::placeholders::_1);
        const auto info = get_item_info(fetch, handle);
        return assemble_scalar<T>(info);
    }

    /// Block until a scalar value is available under `handle`, then return it.
    /// @param timeout Maximum time to wait for the value to appear.
    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value, T>::type
    wait_for_scalar(const data::IncomingHandle handle,
                    std::chrono::milliseconds timeout) {
        const auto fetch = std::bind(&IClient::wait_for_bytes, this,
                                     std::placeholders::_1, timeout);
        const auto info = get_item_info(fetch, handle);
        return assemble_scalar<T>(info);
    }

    /// Store a tensor under `handle`.
    /// @param dims The tensor's dimensions, outermost first.
    /// @param data The tensor's elements in row-major (C) order.
    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value, void>::type
    put_tensor(const data::OutgoingHandle &handle,
               const std::vector<detail::MetaInt> &dims,
               const std::vector<T> &data) {
        put_tensor<T>(handle, dims.data(), dims.size(), data.data(),
                      data.size());
    }

    /// Store a tensor under `handle`, given raw dimension/element pointers.
    /// @param dims Pointer to `n_dims` dimension sizes, outermost first.
    /// @param elements Pointer to `n_elements` elements in row-major order.
    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value, void>::type
    put_tensor(const data::OutgoingHandle &handle, const detail::MetaInt *dims,
               detail::MetaInt n_dims, const T *elements,
               detail::MetaInt n_elements) {
        auto meta = detail::MetaData::make_tensor<T>(dims, n_dims);
        put_bytes(handle.metadata_key(), meta.get_buffer(), meta.size());
        put_bytes(handle.key(), elements, n_elements * sizeof(T));
    }

    /// @return The tensor previously written under `handle`.
    /// @throws std::runtime_error If the stored value is a scalar, or its
    ///     type does not match `T`.
    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value,
                            TensorInfo<T>>::type
    get_tensor(const data::IncomingHandle &handle) {
        const auto fetch =
            std::bind(&IClient::get_bytes, this, std::placeholders::_1);
        const auto info = get_item_info(fetch, handle);
        return assemble_tensor<T>(info);
    }

    /// Block until a tensor is available under `handle`, then return it.
    /// @param timeout Maximum time to wait for the value to appear.
    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value,
                            TensorInfo<T>>::type
    wait_for_tensor(const data::IncomingHandle &handle,
                    std::chrono::milliseconds timeout) {
        const auto fetch = std::bind(&IClient::wait_for_bytes, this,
                                     std::placeholders::_1, timeout);
        const auto info = get_item_info(fetch, handle);
        return assemble_tensor<T>(info);
    }

  private:
    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value, T>::type
    assemble_scalar(const detail::ItemInfo &info) {
        if (info.metadata().n_dims() != 0) {
            throw RankMismatchError(
                "Attempted to retrieve scalar at a key with a vector");
        }
        if (info.metadata().type() != data::encode_type<T>()) {
            throw DTypeMismatchError(
                "Attempted to retrieve scalar of mismatched type");
        }
        T converted;
        std::memcpy(&converted, info.data(), sizeof(T));
        return converted;
    }

    template <typename T>
    typename std::enable_if<data::is_supported_type<T>::value,
                            TensorInfo<T>>::type
    assemble_tensor(const detail::ItemInfo &info) {
        if (info.metadata().n_dims() == 0) {
            throw RankMismatchError(
                "Attempted to retrieve vector at a key with a scalar");
        }
        if (info.metadata().type() != data::encode_type<T>()) {
            throw DTypeMismatchError(
                "Attempted to retrieve vector of mismatched type");
        }

        const T *data_ptr = static_cast<const T *>(info.data());
        return {data_ptr, info.metadata().n_elements(),
                info.metadata().dims_ptr(), info.metadata().n_dims()};
    }
};

namespace unsupported_backend {

/// Placeholder `IClient` used when a backend was disabled at build time; every
/// method throws `radex::BackendUnavailableError` explaining how to rebuild
/// with it enabled.
class Client : public IClient {
  private:
    std::string backend_name;
    std::string enable_option;

  protected:
    [[noreturn]] void throw_backend_unavailable() const {
        throw BackendUnavailableError(
            "RaDex was built without " + backend_name +
            " backend support. "
            "Rebuild with -D" +
            enable_option + "=ON to enable this client.");
    }

  public:
    Client(std::string backend_name, std::string enable_option)
        : backend_name{std::move(backend_name)},
          enable_option{std::move(enable_option)} {
        throw_backend_unavailable();
    }

    bool contains(std::string_view key) override {
        throw_backend_unavailable();
    }

  private:
    void delete_key(std::string_view key) override {
        throw_backend_unavailable();
    }

    void put_bytes(std::string_view key, const void *bytes,
                   detail::MetaInt length) override {
        throw_backend_unavailable();
    }

    detail::BytesBuffer get_bytes(std::string_view key) override {
        throw_backend_unavailable();
    }

    detail::BytesBuffer
    wait_for_bytes(std::string_view key,
                   std::chrono::milliseconds timeout) override {
        throw_backend_unavailable();
    }
};

} // namespace unsupported_backend

} // namespace radex

#endif
