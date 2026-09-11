#include "radex/handles.hpp"
#include "radex/detail.hpp"

#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace radex::data {

auto IncomingHandle::key() const -> std::string {
    std::ostringstream key;
    key << name;
    return key.str();
}

auto IncomingHandle::metadata_key() const -> std::string {
    std::ostringstream meta;
    meta << "metadata::" << key();
    return meta.str();
}

auto OutgoingHandle::key() const -> std::string {
    std::ostringstream key;
    key << name;
    return key.str();
}

auto OutgoingHandle::metadata_key() const -> std::string {
    std::ostringstream meta;
    meta << "metadata::" << key();
    return meta.str();
}

auto ForeignApplication::add_rank_data_to_key(
    std::string_view key, radex::detail::MetaInt rank_id) const -> std::string {
    std::ostringstream key_;
    key_ << app_name << "::" << rank_id << "::" << key;
    return key_.str();
}

auto ForeignApplication::across_ranks(std::string_view name) const -> std::vector<IncomingHandle> {
    std::vector<IncomingHandle> handles;
    for (radex::detail::MetaInt rank = 0; rank < n_ranks; rank++) {
        handles.push_back(from_rank(name, rank));
    }
    return handles;
}

auto ForeignApplication::from_rank(std::string_view name,
                                   radex::detail::MetaInt rank_id) const
    -> IncomingHandle {
    if (rank_id >= n_ranks) {
        throw std::invalid_argument("Invlaid rank ID");
    }
    return IncomingHandle{add_rank_data_to_key(name, rank_id)};
}

auto ThisApplication::with_rank_info(std::string_view name) const
    -> OutgoingHandle {
    return OutgoingHandle{add_rank_data_to_key(name, rank)};
}

} // namespace radex::data
