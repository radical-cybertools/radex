#include "radex/dragon.hpp"
#include "radex/handles.hpp"

#include <chrono>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <vector>

int main(int argc, char *argv[]) {
    if (argc < 4) {
        throw std::runtime_error("Too few arguments provided");
    }
    const char *prg_name = "producer";
    const char *serialized_dd = argv[1];
    unsigned int rank = std::atoi(argv[2]);
    unsigned int world_size = std::atoi(argv[3]);

    timespec timeout{5, 0};
    radex::drg::ddict::Client client{serialized_dd, &timeout};
    radex::data::ThisApplication app{prg_name, rank, world_size};

    std::vector<int> data(4);
    std::iota(data.begin(), data.end(), rank * world_size);
    client.put_tensor(app.with_rank_info("tensor"), {data.size()}, data);
    std::cout << "Producer rank set one part of the tensor in the ddict"
              << std::endl;
}
