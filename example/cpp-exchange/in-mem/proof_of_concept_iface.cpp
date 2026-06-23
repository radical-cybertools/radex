#include <algorithm>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include "raddex/client.hpp"

namespace pkg {

namespace localkv {

class UnorderedMapClient : public raddex::IClient {
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
                   raddex::detail::MetaInt length) override {
        auto ptr = static_cast<const std::uint8_t*>(bytes);
        _map.insert({key, std::vector<uint8_t>{ptr, ptr + length}});
    }

    std::unique_ptr<uint8_t[]> get_bytes(const std::string &key) override {
        auto buf = _map.at(key);
        auto ptr = std::make_unique<uint8_t[]>(buf.size());
        std::copy(buf.begin(), buf.end(), ptr.get());
        return ptr;
    }
};

} // namespace localkv

} // namespace pkg

template <typename T> std::string vec_to_str(const std::vector<T> &vec) {
    std::string s{"[ "};
    for (const auto &v : vec) {
        s += std::to_string(v) + ", ";
    }
    s += "]";
    return s;
}

int main() {
    int i = 123;
    double d = 1.23;

    using DType = raddex::data::DType;

    pkg::localkv::UnorderedMapClient client{};
    client.put_scalar<DType::INT64>("some-int", i);
    client.put_scalar<DType::FLOAT64>("some-double", d);

    std::cout << "=============\n"
              << "Hello World!!\n"
              << "=============\n";

    auto some_int = client.get_scalar<DType::INT64>("some-int");
    auto some_double = client.get_scalar<DType::FLOAT64>("some-double");

    std::vector<int> itensor{0, 1, 2, 3};
    std::vector<double> dtensor{0.1, 2.3, 4.5, 6.7};

    client.put_tensor<DType::INT32>("int-tensor", {2, 2}, itensor);
    client.put_tensor<DType::FLOAT64>("double-tensor", {4}, dtensor);

    auto [some_itensor_dims, some_itensor] =
        client.get_tensor<DType::INT32>("int-tensor");
    auto [some_dtensor_dims, some_dtensor] =
        client.get_tensor<DType::FLOAT64>("double-tensor");

    std::cout << "Some Int Tensor:    " << vec_to_str(some_itensor) << "\n"
              << "        \\- Dims:    " << vec_to_str(some_itensor_dims)
              << "\n"
              << "Some Double Tensor: " << vec_to_str(some_dtensor) << "\n"
              << "           \\- Dims: " << vec_to_str(some_dtensor_dims)
              << "\n"
              << "=============\n";
}
