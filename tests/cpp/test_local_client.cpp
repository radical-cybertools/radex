#include "radex/client.hpp"

#include <catch2/catch_template_test_macros.hpp>
#include <catch2/matchers/catch_matchers_floating_point.hpp>

#include <cstdint>
#include <memory>
#include <string>
#include <string_view>
#include <type_traits>
#include <unordered_map>
#include <vector>

namespace test_utils {

class UnorderedMapClient : public radex::IClient {
  public:
    std::unordered_map<std::string, std::vector<uint8_t>> _map{};

    bool contains(std::string_view key) override {
        try {
            _map.at(key);
        } catch (std::out_of_range &e) {
            return false;
        }
        return true;
    }

    void put_bytes(std::string_view key, const void *bytes,
                   radex::detail::MetaInt length) override {
        auto ptr = static_cast<const std::uint8_t *>(bytes);
        _map.insert({key, std::vector<uint8_t>{ptr, ptr + length}});
    }

    radex::detail::BytesBuffer get_bytes(std::string_view key) override {
        auto buf = _map.at(key);
        auto ptr = std::make_unique<uint8_t[]>(buf.size());
        std::copy(buf.begin(), buf.end(), ptr.get());
        return {std::move(ptr), buf.size()};
    }
};

} // namespace test_utils

TEMPLATE_TEST_CASE("In memory client test cases", "[in-mem]", std::int32_t,
                   std::int64_t, double) {

    test_utils::UnorderedMapClient client{};

    SECTION("Client can put and get a scalar value") {
        TestType x;
        if constexpr (std::is_integral<TestType>::value) {
            x = 123;
        } else {
            x = 1.23;
        }

        TestType y = 0;
        client.put_scalar("my-scalar", x);
        y = client.get_scalar<TestType>("my-scalar");

//FIXME: @MattToast        if constexpr (std::is_integral<TestType>::value) {
//FIXME: @MattToast            REQUIRE(x == y);
//FIXME: @MattToast        } else {
//FIXME: @MattToast            REQUIRE_THAT(y, Catch::Matchers::WithinRel(x));
//FIXME: @MattToast        }
    }

    SECTION("Client can put and get a 1D tensor value") {
        const int size = 12;
        std::vector<TestType> x_data(size);
        std::iota(x_data.begin(), x_data.end(), 0);
        std::vector<radex::detail::MetaInt> x_dims{size};

        client.put_tensor("my-tensor", x_dims, x_data);
        auto [y_dims, y_data] = client.get_tensor<TestType>("my-tensor");

//FIXME: @MattToast        REQUIRE(y_dims.size() == x_dims.size());
//FIXME: @MattToast        REQUIRE(y_data.size() == x_data.size());
//FIXME: @MattToast
//FIXME: @MattToast        for (int i = 0; i < y_dims.size(); i++) {
//FIXME: @MattToast            REQUIRE(y_dims[i] == x_dims[i]);
//FIXME: @MattToast        }

        for (int i = 0; i < y_data.size(); i++) {
            TestType x = x_data[i];
            TestType y = y_data[i];

//FIXME: @MattToast            if constexpr (std::is_integral<TestType>::value) {
//FIXME: @MattToast                REQUIRE(y == x);
//FIXME: @MattToast            } else {
//FIXME: @MattToast                REQUIRE_THAT(y, Catch::Matchers::WithinRel(x, 0.001));
//FIXME: @MattToast            }
        }
    }
}
