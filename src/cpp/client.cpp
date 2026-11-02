#include "radex/client_base.hpp"
#include "radex/constants.hpp"
#include "radex/detail/bytes_buffer.hpp"
#include "radex/detail/item_info.hpp"
#include "radex/detail/metadata.hpp"
#include "radex/exceptions.hpp"
#include "radex/handles.hpp"

#include <chrono>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <memory>
#include <sstream>
#include <string>
#include <string_view>
#include <thread>

namespace radex {

detail::BytesBuffer IClient::wait_for_bytes(std::string_view key,
                                            std::chrono::milliseconds timeout) {
    const char *poll_interval_s = nullptr;
    const auto end_time = std::chrono::steady_clock::now() + timeout;
    const auto poll_interval = std::chrono::milliseconds(
        (poll_interval_s = std::getenv(RADEX_POLL_INTERVAL_VAR.c_str()))
            ? std::stoul(poll_interval_s)
            : RADEX_DEFAULT_POLL_INTERVAL_MILLISECONDS);

    while (!contains(key)) {
        const auto curr_time = std::chrono::steady_clock::now();
        const auto timeout_expired = curr_time > end_time;

        if (timeout_expired) {
            std::ostringstream msg;
            msg << "Failed to find key `" << key << "` before timeout";

            throw radex::TimeoutError(msg.str());
        }
        std::this_thread::sleep_for(poll_interval);
    }
    return get_bytes(key);
}

detail::ItemInfo IClient::get_item_info(
    std::function<detail::BytesBuffer(std::string_view)> fetch_bytes,
    const data::IncomingHandle &handle) {
    auto buf = fetch_bytes(handle.key());
    return {get_meta_data(handle), buf.release()};
}

std::unique_ptr<detail::ItemInfo>
IClient::get_item_info_ptr(const data::IncomingHandle &handle) {
    const auto fetch_bytes =
        std::bind(&IClient::get_bytes, this, std::placeholders::_1);
    return std::make_unique<detail::ItemInfo>(
        get_item_info(fetch_bytes, handle));
}

std::unique_ptr<detail::ItemInfo>
IClient::wait_for_item_info_ptr(const data::IncomingHandle &handle,
                                std::chrono::milliseconds timeout) {
    const auto fetch_bytes = std::bind(&IClient::wait_for_bytes, this,
                                       std::placeholders::_1, timeout);
    return std::make_unique<detail::ItemInfo>(
        get_item_info(fetch_bytes, handle));
}

void IClient::delete_item(const data::OutgoingHandle &handle) {
    delete_key(handle.key());
    if (contains(handle.metadata_key())) {
        delete_key(handle.metadata_key());
    }
}

detail::MetaData IClient::get_meta_data(const data::IncomingHandle &handle) {
    return detail::MetaData::from_buffer(get_bytes(handle.metadata_key()));
}

} // namespace radex
