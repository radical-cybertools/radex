#include "radex/client.hpp"
#include "radex/handles.hpp"

#include <algorithm>
#include <catch2/catch_template_test_macros.hpp>
#include <catch2/matchers/catch_matchers_floating_point.hpp>

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>
#include <string_view>
#include <type_traits>
#include <unordered_map>
#include <utility>
#include <vector>

namespace test_utils {

class UnorderedMapClient : public radex::IClient {
  public:
    std::unordered_map<std::string, std::vector<uint8_t>> _map{};

    bool contains(std::string_view key) override {
        try {
            _map.at(std::string{key});
        } catch (std::out_of_range &e) {
            return false;
        }
        return true;
    }

  private:
    void delete_key(std::string_view key) override {
        _map.erase(std::string{key});
    }

  public:
    void put_bytes(std::string_view key, const void *bytes,
                   radex::detail::MetaInt length) override {
        auto ptr = static_cast<const std::uint8_t *>(bytes);
        _map.insert(
            {std::string{key}, std::vector<uint8_t>{ptr, ptr + length}});
    }

    radex::detail::BytesBuffer get_bytes(std::string_view key) override {
        auto buf = _map.at(std::string{key});
        auto ptr = std::make_unique<uint8_t[]>(buf.size());
        std::copy(buf.begin(), buf.end(), ptr.get());
        return {std::move(ptr), buf.size()};
    }

    radex::detail::BytesBuffer
    wait_for_bytes(std::string_view key,
                   std::chrono::milliseconds timeout) override {
        return IClient::wait_for_bytes(key, timeout);
    }
};

} // namespace test_utils

TEMPLATE_TEST_CASE("In memory client test cases", "[in-mem]", std::int32_t,
                   std::int64_t, float, double) {

    test_utils::UnorderedMapClient client{};

    SECTION("Client can put and get a scalar value") {
        TestType x;
        if constexpr (std::is_integral<TestType>::value) {
            x = 123;
        } else {
            x = 1.23;
        }

        TestType y = 0;
        client.put_scalar(radex::data::OutgoingHandle{"my-scalar"}, x);
        y = client.get_scalar<TestType>(
            radex::data::IncomingHandle{"my-scalar"});

        if constexpr (std::is_integral<TestType>::value) {
            REQUIRE(x == y);
        } else {
            REQUIRE_THAT(y, Catch::Matchers::WithinRel(x));
        }
    }

    SECTION("Client can delete a scalar value and its metadata") {
        const radex::data::OutgoingHandle outgoing{"my-scalar"};
        const radex::data::OutgoingHandle deletion_handle{"my-scalar"};
        client.put_scalar(outgoing, TestType{});
        REQUIRE(client.contains(outgoing.key()));
        REQUIRE(client.contains(outgoing.metadata_key()));

        client.delete_item(deletion_handle);

        REQUIRE_FALSE(client.contains(outgoing.key()));
        REQUIRE_FALSE(client.contains(outgoing.metadata_key()));
    }

    SECTION("Client can delete a tensor value and its metadata") {
        const radex::data::OutgoingHandle outgoing{"my-tensor-to-delete"};
        const radex::data::OutgoingHandle deletion_handle{
            "my-tensor-to-delete"};
        const std::vector<radex::detail::MetaInt> dims{2};
        const std::vector<TestType> data{TestType{1}, TestType{2}};
        client.put_tensor(outgoing, dims, data);
        REQUIRE(client.contains(outgoing.key()));
        REQUIRE(client.contains(outgoing.metadata_key()));

        client.delete_item(deletion_handle);

        REQUIRE_FALSE(client.contains(outgoing.key()));
        REQUIRE_FALSE(client.contains(outgoing.metadata_key()));
    }

    SECTION("Client can put and get a 1D tensor value") {
        const int size = 12;
        std::vector<TestType> x_data(size);
        std::iota(x_data.begin(), x_data.end(), 0);
        std::vector<radex::detail::MetaInt> x_dims{size};

        client.put_tensor(radex::data::OutgoingHandle{"my-tensor"}, x_dims,
                          x_data);
        auto [y_dims, y_data] = client.get_tensor<TestType>(
            radex::data::IncomingHandle{"my-tensor"});

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
                REQUIRE_THAT(y, Catch::Matchers::WithinRel(
                                    x, static_cast<TestType>(0.001)));
            }
        }
    }

    SECTION("Client can gather several scalar items") {

        std::vector<TestType> expected_elements{0, 123, 36};
        std::size_t idx = 0;
        std::vector<radex::data::IncomingHandle> in_handles{};

        for (const auto &e : expected_elements) {
            std::string key = std::string{"scalar-"} + std::to_string(idx++);
            client.put_scalar<TestType>(radex::data::OutgoingHandle{key}, e);
            in_handles.push_back(radex::data::IncomingHandle{key});
        }

        const auto scalars = client.gather_scalars<TestType>(
            in_handles, std::chrono::seconds(3));

        REQUIRE(in_handles.size() == scalars.size());
        REQUIRE(expected_elements.size() == scalars.size());

        for (int i = 0; i < scalars.size(); i++) {
            auto got = scalars[i];
            auto x = expected_elements[i];

            if constexpr (std::is_integral<TestType>::value) {
                REQUIRE(got == x);
            } else {
                REQUIRE_THAT(got, Catch::Matchers::WithinRel(
                                      x, static_cast<TestType>(0.001)));
            }
        }
    }

    SECTION("Client can gather several tensor items") {
        // Tensor 0
        const int t0_size = 12;
        std::vector<TestType> t0_data(t0_size);
        std::iota(t0_data.begin(), t0_data.end(), 0);
        std::vector<radex::detail::MetaInt> t0_dims{t0_size};

        // Tensor 1
        const int t1_size = 12;
        std::vector<TestType> t1_data(t1_size);
        std::iota(t1_data.begin(), t1_data.end(), 0);
        std::reverse(t1_data.begin(), t1_data.end());
        std::vector<radex::detail::MetaInt> t1_dims{3, 4};

        // Tensor 2
        const int t2_size = 400;
        std::vector<TestType> t2_data(t2_size, 0);
        std::vector<radex::detail::MetaInt> t2_dims{10, 5, 8};

        // Place tensors
        std::vector<std::pair<std::vector<radex::detail::MetaInt>,
                              std::vector<TestType>>>
            expected_vectors{std::make_pair(t0_dims, t0_data),
                             std::make_pair(t1_dims, t1_data),
                             std::make_pair(t2_dims, t2_data)};
        std::size_t idx = 0;
        std::vector<radex::data::IncomingHandle> in_handles{};

        for (const auto &[dims, data] : expected_vectors) {
            std::string key = std::string("my-tensor-") + std::to_string(idx++);
            client.put_tensor(radex::data::OutgoingHandle{key}, dims, data);
            in_handles.push_back(radex::data::IncomingHandle{key});
        }

        // Gather tensors
        const auto got_tensors = client.gather_tensors<TestType>(
            in_handles, std::chrono::seconds(3));

        // Assert equal
        REQUIRE(in_handles.size() == got_tensors.size());
        REQUIRE(expected_vectors.size() == got_tensors.size());

        for (int i = 0; i < in_handles.size(); i++) {
            const auto &[got_dims, got_data] = got_tensors[i];
            const auto &[x_dims, x_data] = expected_vectors[i];

            REQUIRE(got_dims.size() == x_dims.size());
            REQUIRE(got_data.size() == x_data.size());

            for (int i = 0; i < got_dims.size(); i++) {
                REQUIRE(got_dims[i] == x_dims[i]);
            }

            for (int i = 0; i < got_data.size(); i++) {
                TestType got_element = got_data[i];
                TestType x_element = x_data[i];

                if constexpr (std::is_integral<TestType>::value) {
                    REQUIRE(got_element == x_element);
                } else {
                    REQUIRE_THAT(got_element,
                                 Catch::Matchers::WithinRel(
                                     x_element, static_cast<TestType>(0.001)));
                }
            }
        }
    }
}
