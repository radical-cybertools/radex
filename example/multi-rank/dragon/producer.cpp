#include "radex/dragon.hpp"
#include "radex/handles.hpp"

#include <cstdlib>
#include <ctime>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

int main(int argc, char *argv[]) {
    if (argc < 4) {
        throw std::runtime_error("Too few arguments provided");
    }
    const char *serialized_dd = argv[1];
    unsigned int rank = std::atoi(argv[2]);
    unsigned int world_size = std::atoi(argv[3]);

    timespec timeout{5, 0};
    radex::drg::ddict::Client client{serialized_dd, &timeout};

    std::vector<int> data(4);
    std::iota(data.begin(), data.end(), rank * world_size);

    std::string scalar_key{"scalar-part-"};
    std::string tensor_key{"tensor-part-"};
    std::string suffix{std::to_string(rank) + "-of-" +
                       std::to_string(world_size)};

    client.put_scalar<long>(radex::data::OutgoingHandle{scalar_key + suffix},
                            (rank + 1) * world_size);
    client.put_tensor(radex::data::OutgoingHandle{tensor_key + suffix},
                      {data.size()}, data);
    std::cout << "Producer rank set a scalar and tensor in the ddict" << std::endl;

    return 0;
}
