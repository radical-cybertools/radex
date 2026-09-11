#include "radex/client_c.h"
#include "radex/client_base.hpp"
#include "radex/exceptions.hpp"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cassert>
#include <unordered_map>
#include <vector>
#include <memory>
#include <algorithm>

// ============================================================================
// In-Memory Client Implementation (UnorderedMap) - Test Only
// ============================================================================

namespace {

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
        try {
            auto buf = _map.at(std::string{key});
            auto ptr = std::make_unique<uint8_t[]>(buf.size());
            std::copy(buf.begin(), buf.end(), ptr.get());
            return {std::move(ptr), buf.size()};
        } catch (const std::out_of_range&) {
            throw radex::KeyNotFoundError(std::string("Key not found: ") + std::string(key));
        }
    }

    radex::detail::BytesBuffer
    wait_for_bytes(std::string_view key,
                   std::chrono::milliseconds timeout) override {
        return IClient::wait_for_bytes(key, timeout);
    }
};

} // anonymous namespace

// ============================================================================
// Factory function for in-memory client (test only)
// ============================================================================

extern "C" {

void* radex_client_local_create(void) {
  try {
    auto* client = new UnorderedMapClient();
    return static_cast<void*>(client);
  } catch (const std::exception&) {
    fprintf(stderr, "RaDex Error: RADEX_ERR_UNKNOWN\n");
    abort();
  }
}

} // extern "C"

// ============================================================================
// C Interface Test
// ============================================================================

int main(int argc, char* argv[]) {
  printf("Testing RaDex C Interface...\n");

  printf("Using in-memory (unordered map) backend...\n");
  void* client = radex_client_local_create();
  printf("  Client created\n");

  // Define test values
  const char* key_int32 = "test_key_int32";
  const int32_t test_value_int32 = 42;
  const char* key_float32 = "test_key_float32";
  const float test_value_float32 = 2.71828f;
  const char* key_float64 = "test_key_float64";
  const double test_value_float64 = 3.14159;

  // Test put_int32 with handle
  printf("\nTesting put_int32...\n");
  void* handle_put_int32 = radex_outgoing_handle_create(key_int32);
  assert(handle_put_int32 && "handle creation failed");
  int stat = radex_client_put_int32(client, (radex_outgoing_handle_t*)handle_put_int32, test_value_int32);
  assert(stat == RADEX_OK && "put_int32 failed");
  printf("  put_int32 succeeded\n");
  radex_outgoing_handle_destroy((radex_outgoing_handle_t*)handle_put_int32);

  // Test get_int32 with handle
  printf("\nTesting get_int32...\n");
  void* handle_get_int32 = radex_incoming_handle_create(key_int32);
  assert(handle_get_int32 && "handle creation failed");
  int32_t value_int32 = 0;
  stat = radex_client_get_int32(client, (radex_incoming_handle_t*)handle_get_int32, &value_int32);
  assert(stat == RADEX_OK && "get_int32 failed");
  assert(value_int32 == test_value_int32 && "get_int32 returned wrong value");
  printf("  get_int32 succeeded, value=%d\n", value_int32);
  radex_incoming_handle_destroy((radex_incoming_handle_t*)handle_get_int32);

  // Test put_float32 with handle
  printf("\nTesting put_float32...\n");
  void* handle_put_float32 = radex_outgoing_handle_create(key_float32);
  assert(handle_put_float32 && "handle creation failed");
  stat = radex_client_put_float32(client, (radex_outgoing_handle_t*)handle_put_float32, test_value_float32);
  assert(stat == RADEX_OK && "put_float32 failed");
  printf("  put_float32 succeeded\n");
  radex_outgoing_handle_destroy((radex_outgoing_handle_t*)handle_put_float32);

  // Test get_float32 with handle
  printf("\nTesting get_float32...\n");
  void* handle_get_float32 = radex_incoming_handle_create(key_float32);
  assert(handle_get_float32 && "handle creation failed");
  float value_float32 = 0.0f;
  stat = radex_client_get_float32(client, (radex_incoming_handle_t*)handle_get_float32, &value_float32);
  assert(stat == RADEX_OK && "get_float32 failed");
  assert(value_float32 == test_value_float32 && "get_float32 returned wrong value");
  printf("  get_float32 succeeded, value=%f\n", value_float32);
  radex_incoming_handle_destroy((radex_incoming_handle_t*)handle_get_float32);

  // Test put_float64 with handle
  printf("\nTesting put_float64...\n");
  void* handle_put_float64 = radex_outgoing_handle_create(key_float64);
  assert(handle_put_float64 && "handle creation failed");
  stat = radex_client_put_float64(client, (radex_outgoing_handle_t*)handle_put_float64, test_value_float64);
  assert(stat == RADEX_OK && "put_float64 failed");
  printf("  put_float64 succeeded\n");
  radex_outgoing_handle_destroy((radex_outgoing_handle_t*)handle_put_float64);

  // Test get_float64 with handle
  printf("\nTesting get_float64...\n");
  void* handle_get_float64 = radex_incoming_handle_create(key_float64);
  assert(handle_get_float64 && "handle creation failed");
  double value_float64 = 0.0;
  stat = radex_client_get_float64(client, (radex_incoming_handle_t*)handle_get_float64, &value_float64);
  assert(stat == RADEX_OK && "get_float64 failed");
  assert(value_float64 == test_value_float64 && "get_float64 returned wrong value");
  printf("  get_float64 succeeded, value=%lf\n", value_float64);
  radex_incoming_handle_destroy((radex_incoming_handle_t*)handle_get_float64);

  // Test contains with handle
  printf("\nTesting contains...\n");
  void* handle_contains_exists = radex_incoming_handle_create(key_int32);
  assert(handle_contains_exists && "handle creation failed");
  stat = radex_client_contains(client, (radex_incoming_handle_t*)handle_contains_exists);
  assert(stat == 1 && "contains should return 1 for existing key");
  printf("  contains succeeded for existing key\n");
  radex_incoming_handle_destroy((radex_incoming_handle_t*)handle_contains_exists);

  void* handle_contains_missing = radex_incoming_handle_create("nonexistent_key");
  assert(handle_contains_missing && "handle creation failed");
  stat = radex_client_contains(client, (radex_incoming_handle_t*)handle_contains_missing);
  // Should be 0 or error, not 1
  assert(stat != 1 && "contains should not return 1 for nonexistent key");
  printf("  contains correctly returned false for nonexistent key\n");
  radex_incoming_handle_destroy((radex_incoming_handle_t*)handle_contains_missing);

  // Test error handling - get nonexistent key
  printf("\nTesting error handling...\n");
  void* handle_error = radex_incoming_handle_create("truly_nonexistent_key_12345");
  assert(handle_error && "handle creation failed");
  int32_t dummy = 0;
  stat = radex_client_get_int32(client, (radex_incoming_handle_t*)handle_error, &dummy);
  assert(stat != RADEX_OK && "should return error for nonexistent key");
  assert(stat == RADEX_ERR_KEY_NOT_FOUND && "should return KEY_NOT_FOUND error");
  printf("  Error handling works: got error code %d\n", stat);
  radex_incoming_handle_destroy((radex_incoming_handle_t*)handle_error);

  // Destroy client
  printf("\nCleaning up...\n");
  stat = radex_client_destroy(client);
  assert(stat == RADEX_OK && "destroy failed");
  printf("  Client destroyed\n");

  printf("\nAll C interface tests passed!\n");
  return 0;
}
