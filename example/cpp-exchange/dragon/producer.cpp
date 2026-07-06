#include <ctime>
#include <iostream>
#include <stdexcept>

#include "raddex/client.hpp"
#include "raddex/dragon.hpp"

int main() {
    char *serialized_dd = getenv("SERIALIZED_DDICT");
    if (serialized_dd == nullptr) {
        throw std::runtime_error("DDict descriptor not found!");
    }

    std::cout << "===========================\n"
              << "Hello World from Producer!!\n"
              << "---------------------------\n";

    timespec timeout{5, 0};
    raddex::drg::ddict::Client client{serialized_dd, &timeout};

    using DType = raddex::data::DType;

    client.put_scalar<DType::INT64>("some-int", 123);
    client.put_scalar<DType::FLOAT64>("some-float", 1.23);

    client.put_tensor<DType::FLOAT64>("some-float-tensor", {4},
                                      {0.12, 3.45, 6.78, 9.123});
    client.put_tensor<DType::INT64>("some-int-tensor", {2, 4},
                                    {1, 2, 3, 4, 5, 6, 7, 8});

    std::cout << "---------------------------\n"
              << "Goodbye from Producer\n"
              << "===========================\n";

    return 0;
}
