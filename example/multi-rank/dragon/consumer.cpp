#include "radex/dragon.hpp"
#include "radex/handles.hpp"

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
    if (argc < 3) {
        throw std::runtime_error("Too few arguments provided");
    }
    const char *prg_name = "producer";
    const char *serialized_dd = argv[1];
    unsigned int world_size = std::atoi(argv[2]);

    timespec timeout{5, 0};
    radex::drg::ddict::Client client{serialized_dd, &timeout};
    radex::data::ForeignApplication producer{prg_name, world_size};

    auto tensors = client.gather_tensors<int>(producer.across_ranks("tensor"),
                                              std::chrono::seconds(10));
    std::cout << "Consumer gathered tensors:" << "\n";
    for (const auto &tensor : tensors) {
        std::cout << "  |-- Part:" << "\n"
                  << "  |   |-- Data: " << vec_to_str(tensor.data) << "\n"
                  << "  |   \\-- Dims: " << vec_to_str(tensor.dims) << "\n";
    }
    std::cout << std::endl;
}
