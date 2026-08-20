#include "radex/handles.hpp"
#include "radex/smartredis.hpp"

#include <chrono>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <stdexcept>
#include <vector>

template <typename T> std::string vec_to_str(const std::vector<T> &vec) {
    std::string s{"[ "};
    for (const auto &v : vec) {
        s += std::to_string(v) + ", ";
    }
    s += "]";
    return s;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        throw std::runtime_error("Too few arguments provided");
    }
    unsigned int world_size = std::atoi(argv[1]);

    timespec timeout{5, 0};
    radex::redis::smartredis::Client client{"example-multi-rank-consumer"};

    std::vector<radex::data::IncomingHandle> scalar_handles;
    scalar_handles.reserve(world_size);
    std::vector<radex::data::IncomingHandle> tensor_handles;
    tensor_handles.reserve(world_size);
    for (int i = 0; i < world_size; i++) {
        std::string scalar_key{"scalar-part-"};
        std::string tensor_key{"tensor-part-"};
        std::string suffix{std::to_string(i) + "-of-" +
                           std::to_string(world_size)};

        scalar_handles.push_back(
            radex::data::IncomingHandle{scalar_key + suffix});
        tensor_handles.push_back(
            radex::data::IncomingHandle{tensor_key + suffix});
    }

    auto scalars =
        client.gather_scalars<long>(scalar_handles, std::chrono::seconds(10));
    std::cout << "Consumer gathered scalars: " << vec_to_str(scalars) << "\n";
    auto tensors =
        client.gather_tensors<int>(tensor_handles, std::chrono::seconds(10));
    std::cout << "Consumer gathered tensors:" << "\n";
    for (const auto &tensor : tensors) {
        std::cout << "  |-- Part:" << "\n"
                  << "  |   |-- Data: " << vec_to_str(tensor.data) << "\n"
                  << "  |   \\-- Dims: " << vec_to_str(tensor.dims) << "\n";
    }
    std::cout << std::endl;

    return 0;
}
