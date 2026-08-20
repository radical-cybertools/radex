#ifndef __RADEX_HANDLES_HPP__
#define __RADEX_HANDLES_HPP__

#include "radex/detail.hpp"

#include <string>
#include <string_view>
#include <vector>

namespace radex::data {

/// Base interface for a named reference to a value in a RaDex backend.
class IHandle {
  public:
    /// The key under which the value's raw bytes are stored.
    virtual auto key() const -> std::string = 0;
    /// The key under which the value's metadata (type, dimensions) is stored.
    virtual auto metadata_key() const -> std::string = 0;
    virtual ~IHandle() {}
};

/// A handle for reading a value from the store.
class IncomingHandle : public IHandle {
  private:
    const std::string name;

  public:
    /// @param name The key name to read from.
    IncomingHandle(std::string_view name) : name{name} {}
    auto key() const -> std::string override;
    auto metadata_key() const -> std::string override;
};

/// A handle for writing a value to the store.
class OutgoingHandle : public IHandle {
  private:
    const std::string name;

  public:
    /// @param name The key name to write to.
    OutgoingHandle(std::string_view name) : name{name} {}
    auto key() const -> std::string override;
    auto metadata_key() const -> std::string override;
};

class ForeignApplication {
  private:
    const std::string app_name;
    const radex::detail::MetaInt n_ranks;

  public:
    ForeignApplication(std::string_view app_name,
                       radex::detail::MetaInt world_size)
        : app_name{app_name}, n_ranks{world_size} {}
    auto from_rank(std::string_view name, radex::detail::MetaInt) const
        -> IncomingHandle;
    auto across_ranks(std::string_view name) const
        -> std::vector<IncomingHandle>;

  protected:
    auto add_rank_data_to_key(std::string_view key,
                              radex::detail::MetaInt rank_id) const
        -> std::string;
};

class ThisApplication : public ForeignApplication {
  private:
    const radex::detail::MetaInt rank;

  public:
    ThisApplication(std::string_view app_name, radex::detail::MetaInt my_rank,
                    radex::detail::MetaInt world_size)
        : ForeignApplication{app_name, world_size}, rank{my_rank} {}
    auto with_rank_info(std::string_view name) const -> OutgoingHandle;
};

} // namespace radex::data

#endif
