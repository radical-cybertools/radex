#include "radex/client.hpp"

#include <catch2/catch_template_test_macros.hpp>

#include <cstdint>
#include <memory>
#include <string>
#include <type_traits>
#include <unordered_map>
#include <vector>

namespace test_utils {

class UnorderedMapClient : public radex::IClient {
  public:
    std::unordered_map<std::string, std::vector<uint8_t>> _map{};

    bool contains(const std::string &key) override {
        try {
            _map.at(key);
        } catch (std::out_of_range &e) {
            return false;
        }
        return true;
    }

    void put_bytes(const std::string &key, const void *bytes,
                   radex::detail::MetaInt length) override {
        auto ptr = static_cast<const std::uint8_t *>(bytes);
        _map.insert({key, std::vector<uint8_t>{ptr, ptr + length}});
    }

    radex::detail::BytesBuffer get_bytes(const std::string &key) override {
        auto buf = _map.at(key);
        auto ptr = std::make_unique<uint8_t[]>(buf.size());
        std::copy(buf.begin(), buf.end(), ptr.get());
        return {std::move(ptr), buf.size()};
    }
};

} // namespace test_utils

TEMPLATE_TEST_CASE("In memory client test cases", "[in-mem]", std::uint32_t,
                   std::uint64_t, double) {

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
        y = client.get_scalar<TestType>("my-sclaar");

        if constexpr (std::is_integral<TestType>::value) {
            REQUIRE(x == y);
        } else {
            REQUIRE_THAT(y, WithinRel(x));
        }
    }

    SECTION("Client can put and get a 1D tensor value") {
        const int size = 12;
        std::vector<TestType> x_data(size);
        std::iota(x.begin(), x.end(), 0);
        std::vector<radex::detail::MetaInt> x_dims{size};

        client.put_tensor("my-tensor", x_dims, x);
        auto [y_dims, y_data] = client.get_tensor<TestType>("my-tensor");

        REQUIRE(y_dims.size() == x_dims.size());
        REQUIRE(y_data.size() == x_data.size());

        for (int i = 0; i < y_dims.size(); i++) {
            REQUIRE(y_dims[i] == x_dims[i]);
        }

        for (int i = 0; i < y_data.size(); i++) {
            TestType x = x_data[i];
            TestType y = y_data[i];

            if constexpr (std::is_integral<TestType>::value) {
                REQUIRE(y == x);
            } else {
                REQUIRE_THAT(y, WithinRel(x));
            }
        }
    }
}
