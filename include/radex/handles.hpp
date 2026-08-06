#ifndef __RADEX_HANDLES_HPP__
#define __RADEX_HANDLES_HPP__

#include <string>
#include <string_view>

namespace radex::data {

class IHandle {
  public:
    virtual auto key() const -> std::string = 0;
    virtual auto metadata_key() const -> std::string = 0;
    virtual ~IHandle() {}
};

class IncomingHandle : public IHandle {
  private:
    const std::string name;

  public:
    IncomingHandle(std::string_view name) : name{name} {}
    auto key() const -> std::string override;
    auto metadata_key() const -> std::string override;
};

class OutgoingHandle : public IHandle {
  private:
    const std::string name;

  public:
    OutgoingHandle(std::string_view name) : name{name} {}
    auto key() const -> std::string override;
    auto metadata_key() const -> std::string override;
};

} // namespace radex::data

#endif
