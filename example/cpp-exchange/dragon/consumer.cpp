#include <ctime>
#include <stdexcept>
#include <vector>
#include <string>
#include <iostream>

#include "raddex/client.hpp"
#include "raddex/dragon.hpp"

template <typename T> std::string vec_to_str(const std::vector<T> &vec) {
    std::string s{"[ "};
    for (const auto &v : vec) {
        s += std::to_string(v) + ", ";
    }
    s += "]";
    return s;
}

int main() {
    char *serialized_dd = getenv("SERIALIZED_DDICT");
    if (serialized_dd == nullptr) {
        throw std::runtime_error("DDict descriptor not found!");
    }

    std::cout << "===========================\n"
              << "Hello World from Consumer!!\n"
              << "---------------------------\n";

    timespec timeout{5, 0};
    raddex::drg::ddict::Client client{serialized_dd, &timeout};

    using DType = raddex::data::DType;

    auto some_int = client.get_scalar<DType::INT64>("some-int");
    auto [some_int_tensor_dims, some_int_tensor] =
        client.get_tensor<DType::INT64>("some-int-tensor");

    auto some_float = client.get_scalar<DType::FLOAT64>("some-float");
    auto [some_float_tensor_dims, some_float_tensor] =
        client.get_tensor<DType::FLOAT64>("some-float-tensor");

    std::cout << ""
              << "Some Int:          " << some_int << "\n"
              << "Some Float:        " << some_float << "\n"
              << "Some Int Tensor:   " << vec_to_str(some_int_tensor) << "\n"
              << "      \\ -> Dims:   " << vec_to_str(some_int_tensor_dims) << "\n"
              << "Some Float Tensor: " << vec_to_str(some_float_tensor) << "\n"
              << "        \\ -> Dims: " << vec_to_str(some_float_tensor_dims) << "\n"
              << "---------------------------\n"
              << "Goodbye from Consumer!!\n"
              << "===========================\n";

    return 0;
}
