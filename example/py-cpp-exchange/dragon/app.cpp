#include <ctime>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <thread>
#include <vector>

#include "raddex/client.hpp"
#include "raddex/dragon.hpp"

const std::string IDENT{"               "};

template <typename T> std::string vec_to_str(const std::vector<T> &vec) {
    std::string s{"[ "};
    for (const auto &v : vec) {
        s += std::to_string(v) + ", ";
    }
    s += "]";
    return s;
}

void poll_for_key(raddex::IClient &client, const std::string &key,
                  int max_attempts = 10) {
    while (!client.contains(key)) {
        if (max_attempts-- == 0) {
            throw std::runtime_error("Too many attempts");
        }
        std::cout << IDENT << "App: Waiting for key `" << key << "`"
                  << std::endl;
        std::this_thread::sleep_for(1'000ms);
    }
}

template <typename T>
void poll_for_scalar_key(raddex::IClient &client, const std::string &key) {
    poll_for_key(client, key);
    auto val = client.get_scalar<T>(key);
    std::cout << IDENT << "App: Got key `" << key << "` has value " << val
              << "\n"
              << std::endl;
}

template <typename T>
void poll_for_vector_key(raddex::IClient &client, const std::string &key) {
    poll_for_key(client, key);
    auto [dims, data] = client.get_tensor<T>(key);
    std::cout << IDENT << "App: Got key `" << key << "`\n"
              << IDENT << "      |- Data: " << vec_to_str(data) << "\n"
              << IDENT << "      \\- Dims: " << vec_to_str(dims) << "\n"
              << std::endl;
}

int main() {
    char *serialized_dd = getenv("SERIALIZED_DDICT");
    if (serialized_dd == nullptr) {
        throw std::runtime_error("DDict descriptor not found!");
    }

    timespec timeout{5, 0};
    std::cout << IDENT << "App: Creating client" << std::endl;
    raddex::drg::ddict::Client client{serialized_dd, &timeout};
    std::cout << IDENT << "App: Client created" << std::endl;

    poll_for_scalar_key<int>(client, "py-int");
    poll_for_scalar_key<double>(client, "py-double");
    poll_for_vector_key<int>(client, "py-int-tensor");
    poll_for_vector_key<double>(client, "py-float-tensor");

    std::this_thread::sleep_for(3'000ms);
    std::cout << IDENT << "App: Setting Double" << std::endl;
    client.put_scalar<double>("cpp-double", 1.23);

    std::this_thread::sleep_for(3'000ms);
    std::cout << IDENT << "App: Setting Int" << std::endl;
    client.put_scalar<int>("cpp-int", 987);

    std::this_thread::sleep_for(3'000ms);
    std::cout << IDENT << "App: Setting Double Tensor" << std::endl;
    std::vector<double> v(12);
    std::iota(v.begin(), v.end(), 0);
    client.put_tensor("cpp-double-tensor", {4, 3}, v);

    std::this_thread::sleep_for(3'000ms);
    std::cout << IDENT << "App: Setting Long Tensor" << std::endl;
    client.put_tensor<long>("cpp-long-tensor", {2, 2, 2},
                            {1, 2, 3, 4, 5, 6, 7, 8});

    return 0;
}
