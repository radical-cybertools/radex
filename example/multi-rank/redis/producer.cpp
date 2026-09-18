#include "radex/handles.hpp"
#include "radex/smartredis.hpp"

#include <cstdlib>
#include <ctime>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <vector>

int main(int argc, char *argv[]) {
    if (argc < 3) {
        throw std::runtime_error("Too few arguments provided");
    }
    const char *prg_name = "producer";
    unsigned int rank = std::atoi(argv[1]);
    unsigned int world_size = std::atoi(argv[2]);

    timespec timeout{5, 0};
    radex::redis::smartredis::Client client{"example-multi-rank-producer"};

    std::vector<int> data(4);
    std::iota(data.begin(), data.end(), rank * world_size);

    std::string scalar_key{"scalar-part-"};
    std::string tensor_key{"tensor-part-"};
    std::string suffix{std::to_string(rank) + "-of-" +
                       std::to_string(world_size)};

    client.put_scalar<long>(radex::data::OutgoingHandle{scalar_key + suffix},
                            (rank + 1) * world_size);
    std::cout << "Producer rank set a scalar in the orchestrator" << std::endl;
    client.put_tensor(radex::data::OutgoingHandle{tensor_key + suffix},
                      {data.size()}, data);
    std::cout << "Producer rank set a tensor in the orchestrator" << std::endl;

    return 0;
}
