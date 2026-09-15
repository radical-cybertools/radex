import dataclasses
import math
import os
import textwrap
import time
from collections.abc import Iterable

import dragon
import numpy as np
import pytest
from dragon.native.process import Popen
from radex.handles.handles import IncomingHandle, OutgoingHandle


def _comma_seperate_ints(ints: Iterable[int]) -> str:
    return ", ".join(str(i) for i in ints)


@dataclasses.dataclass(frozen=True)
class _TestTensorValues:
    key: str
    shape: tuple[int, ...]

    @property
    def size(self) -> int:
        return math.prod(self.shape)

    @property
    def cpp_dims_init_list(self) -> str:
        return f"{{ {_comma_seperate_ints(self.shape)} }}"


def test_get_cpp_scalar(cpp_dragon_compile, ddict, client, np_dtype, cpp_type_name):
    key = "some-scalar"
    bin_ = cpp_dragon_compile(textwrap.dedent(f"""\
        #include "radex/dragon.hpp"
        #include "radex/handles.hpp"
        #include <cstdint>

        int main(void) {{
            timespec timeout {{5, 0}};
            radex::drg::ddict::Client client {{"{ddict.serialize()}", &timeout}};
            {cpp_type_name} value = 123;
            client.put_scalar(radex::data::OutgoingHandle("{key}"), value);
            return 0;
        }}
        """))

    assert not client.contains(key)
    proc = Popen(executable=os.fspath(bin_), args=[], env=os.environ)
    proc.wait()
    assert proc.returncode == 0

    assert client.contains(key)
    value = client.get_scalar(IncomingHandle(key))
    assert value.dtype == np_dtype
    assert value == np_dtype(123)


def test_get_cpp_tensor(cpp_dragon_compile, ddict, client, np_dtype, cpp_type_name):
    n_elements = 12
    tensors = {
        "tensor-1d": (12,),
        "tensor-2d": (6, 2),
        "tensor-3d": (2, 3, 2),
    }

    put_tensors = "\n".join(textwrap.dedent(f"""\
            client.put_tensor(radex::data::OutgoingHandle("{key}"),
                              {{{_comma_seperate_ints(shape)}}},
                              tensor);""") for key, shape in tensors.items())
    bin_ = cpp_dragon_compile(textwrap.dedent(f"""\
        #include "radex/dragon.hpp"
        #include "radex/handles.hpp"
        #include <vector>
        #include <numeric>
        #include <cstdint>

        int main(void) {{
            timespec timeout {{5, 0}};
            radex::drg::ddict::Client client {{"{ddict.serialize()}", &timeout}};
            std::vector<{cpp_type_name}> tensor({n_elements});
            std::iota(tensor.begin(), tensor.end(), 0);
            {put_tensors}
            return 0;
        }}
        """))

    assert not any(client.contains(tensor) for tensor in tensors)
    proc = Popen(executable=os.fspath(bin_), args=[], env=os.environ)
    proc.wait()
    assert proc.returncode == 0

    expected = np.arange(n_elements, dtype=np_dtype)
    for key, shape in tensors.items():
        assert client.contains(key)
        ret = client.get_tensor(IncomingHandle(key))
        assert ret.dtype == np_dtype
        assert ret.shape == shape
        assert (ret == expected.reshape(shape)).all()


def test_put_py_scalar(cpp_dragon_compile, ddict, client, np_dtype, cpp_type_name):
    key = "some-scalar"
    bin_ = cpp_dragon_compile(textwrap.dedent(f"""\
        #include "radex/dragon.hpp"
        #include "radex/handles.hpp"
        #include <cstdint>

        int main(void) {{
            timespec timeout {{5, 0}};
            radex::drg::ddict::Client client {{"{ddict.serialize()}", &timeout}};
            auto x = client.get_scalar<{cpp_type_name}>(
                radex::data::IncomingHandle("{key}"));
            return x == 34 ? 0 : 1;
        }}
        """))

    assert not client.contains(key)
    client.put_scalar(OutgoingHandle(key), np_dtype(34))
    assert client.contains(key)

    proc = Popen(executable=os.fspath(bin_), args=[], env=os.environ)
    proc.wait()
    assert proc.returncode == 0


def test_put_py_tensor(cpp_dragon_compile, ddict, client, np_dtype, cpp_type_name):
    n_elements = 16
    tensors = {
        "tensor-1d": (16,),
        "tensor-2d": (4, 4),
        "tensor-4d": (2, 2, 2, 2),
    }

    eval_tensors = "\n".join(
        f'eval_tensor(client, "{key}", {{ {_comma_seperate_ints(shape)} }}, data);\n'
        for key, shape in tensors.items()
    )

    bin_ = cpp_dragon_compile(textwrap.dedent(f"""\
        #include "radex/dragon.hpp"
        #include "radex/handles.hpp"
        #include <cstdint>
        #include <vector>
        #include <numeric>
        #include <exception>

        template <typename T>
        void eval_tensor(radex::IClient& client,
                         const std::string& key,
                         const std::vector<radex::detail::MetaInt>& expected_dims,
                         const std::vector<T>& expected_data) {{
            auto [dims, data] = client.get_tensor<T>(radex::data::IncomingHandle(key));
            if (expected_dims != dims)
                throw std::logic_error(key + ": Dims do not match");
            if (expected_data != data)
                throw std::logic_error(key + ": Data does not match");
        }}

        int main(void) {{
            timespec timeout {{5, 0}};
            radex::drg::ddict::Client client {{"{ddict.serialize()}", &timeout}};

            std::vector<{cpp_type_name}> data({n_elements});
            std::iota(data.begin(), data.end(), 0);

            {eval_tensors}

            return 0;
        }}
        """))

    assert not any(client.contains(tensor) for tensor in tensors)
    for key, shape in tensors.items():
        tensor = np.arange(n_elements, dtype=np_dtype).reshape(shape)
        client.put_tensor(OutgoingHandle(key), tensor)
    assert all(client.contains(tensor) for tensor in tensors)

    proc = Popen(executable=os.fspath(bin_), args=[], env=os.environ)
    proc.wait()
    assert proc.returncode == 0


@pytest.mark.slow
def test_wait_for_scalars(
    cpp_dragon_compile,
    ddict,
    client,
    np_dtype,
    cpp_type_name,
):
    py_key = "some-py-val"
    cpp_key = "some-cpp-val"

    py_put_delay = 3  # seconds
    cpp_put_delay = 3  # seconds

    bin_ = cpp_dragon_compile(textwrap.dedent(f"""\
        #include "radex/dragon.hpp"
        #include "radex/handles.hpp"
        #include <iostream>
        #include <chrono>
        #include <thread>

        int main(void) {{
            timespec timeout {{5, 0}};
            radex::drg::ddict::Client client {{"{ddict.serialize()}", &timeout}};
            {cpp_type_name} value = 123;
            std::this_thread::sleep_for(std::chrono::seconds({cpp_put_delay}));
            client.put_scalar(radex::data::OutgoingHandle("{cpp_key}"), value);

            auto x = client.wait_for_scalar<{cpp_type_name}>(
                radex::data::IncomingHandle("{py_key}"), std::chrono::milliseconds({10000}));
            return x == 12 ? 0 : 1;
        }}
        """))

    assert not client.contains(py_key)
    assert not client.contains(cpp_key)

    try:
        proc = Popen(executable=os.fspath(bin_), args=[])
        start_t = time.perf_counter()
        value = client.wait_for_scalar(IncomingHandle(cpp_key), 10)
        py_wait_time = time.perf_counter() - start_t

        time.sleep(py_put_delay)
        client.put_scalar(OutgoingHandle(py_key), np_dtype(12))
    except Exception:
        proc.kill()
        raise
    finally:
        proc.wait()

    wait_interval = 2.0
    assert cpp_put_delay - wait_interval < py_wait_time < cpp_put_delay + wait_interval
    assert value.dtype == np_dtype
    assert value == np_dtype(123)
    assert proc.returncode == 0


@pytest.mark.slow
def test_wait_for_tensors(
    cpp_dragon_compile,
    ddict,
    client,
    np_dtype,
    cpp_type_name,
):
    py_key = "some-py-val"
    cpp_key = "some-cpp-val"

    py_put_delay = 2  # seconds
    cpp_put_delay = 2  # seconds

    cpp_tensor_size = 36
    cpp_tensor_shape = (4, 3, 3)
    expected_cpp_tensor = np.arange(cpp_tensor_size, dtype=np_dtype).reshape(
        cpp_tensor_shape
    )

    py_tensor_data = [12, 34, 56, 78, 90, 0]
    py_tenosr_shape = (2, 3)
    py_tensor = np.array(py_tensor_data, dtype=np_dtype).reshape(py_tenosr_shape)

    bin_ = cpp_dragon_compile(textwrap.dedent(f"""\
        #include "radex/dragon.hpp"
        #include "radex/handles.hpp"
        #include <chrono>
        #include <numeric>
        #include <thread>
        #include <vector>

        int main(void) {{
            timespec timeout {{5, 0}};
            radex::drg::ddict::Client client {{"{ddict.serialize()}", &timeout}};

            std::vector<{cpp_type_name}> cpp_tensor({cpp_tensor_size});
            std::iota(cpp_tensor.begin(), cpp_tensor.end(), 0);

            std::vector<{cpp_type_name}> expected_py_data
                {{{_comma_seperate_ints(py_tensor_data)}}};
            std::vector<radex::detail::MetaInt> expected_py_dims
                {{{_comma_seperate_ints(py_tenosr_shape)}}};

            std::this_thread::sleep_for(std::chrono::seconds({cpp_put_delay}));
            client.put_tensor(
                radex::data::OutgoingHandle("{cpp_key}"),
                {{{_comma_seperate_ints(cpp_tensor_shape)}}},
                cpp_tensor);

            auto [dims, data] = client.wait_for_tensor<{cpp_type_name}>(
                radex::data::IncomingHandle("{py_key}"), std::chrono::milliseconds({10000}));
            if (dims != expected_py_dims)
                throw std::logic_error("Dims did not match");
            if (data != expected_py_data)
                throw std::logic_error("Data did not match");
            return 0;
        }}
        """))
    assert not client.contains(py_key)
    assert not client.contains(cpp_key)

    try:
        proc = Popen(executable=os.fspath(bin_), args=[])
        start_t = time.perf_counter()
        cpp_tensor = client.wait_for_tensor(IncomingHandle(cpp_key), 10)
        py_wait_time = time.perf_counter() - start_t

        time.sleep(py_put_delay)
        client.put_tensor(OutgoingHandle(py_key), py_tensor)
    except Exception:
        proc.kill()
        raise
    finally:
        proc.wait()
    wait_interval = 2.0
    assert cpp_put_delay - wait_interval < py_wait_time < cpp_put_delay + wait_interval
    assert cpp_tensor.dtype == expected_cpp_tensor.dtype == np_dtype
    assert (cpp_tensor == expected_cpp_tensor).all()
    assert proc.returncode == 0


@pytest.mark.slow
def test_gather_scalars(cpp_dragon_compile, ddict, client, np_dtype, cpp_type_name):
    bin_ = cpp_dragon_compile(textwrap.dedent(f"""\
        #include "radex/dragon.hpp"
        #include "radex/handles.hpp"
        #include <iostream>
        #include <chrono>
        #include <thread>

        int main(void) {{
            timespec timeout {{5, 0}};
            radex::drg::ddict::Client client {{"{ddict.serialize()}", &timeout}};
            client.put_scalar<{cpp_type_name}>(radex::data::OutgoingHandle("cpp-0"), 123);
            client.put_scalar<{cpp_type_name}>(radex::data::OutgoingHandle("cpp-1"), 456);
            client.put_scalar<{cpp_type_name}>(radex::data::OutgoingHandle("cpp-2"), 789);

            auto got = client.gather_scalars<{cpp_type_name}>({{
                radex::data::IncomingHandle("py-0"),
                radex::data::IncomingHandle("py-1"),
                radex::data::IncomingHandle("py-2")
                }}, std::chrono::milliseconds({10_000}));
            std::vector<{cpp_type_name}> expected {{ 12, 17, 8 }};
            return got == expected ? 0 : 1;
        }}
        """))

    assert not any(
        client.contains(k) for k in ["cpp-0", "cpp-1", "cpp-2", "py-0", "py-1", "py-2"]
    )

    try:
        proc = Popen(executable=os.fspath(bin_), args=[])
        scalars = client.gather_scalars(
            [
                IncomingHandle("cpp-2"),
                IncomingHandle("cpp-1"),
                IncomingHandle("cpp-0"),
            ],
            10,
        )

        client.put_scalar(OutgoingHandle("py-2"), np_dtype(8))
        client.put_scalar(OutgoingHandle("py-1"), np_dtype(17))
        client.put_scalar(OutgoingHandle("py-0"), np_dtype(12))
    except Exception:
        proc.kill()
        raise
    finally:
        proc.wait()

    assert all(v.dtype == np_dtype for v in scalars)
    assert scalars == [np_dtype(789), np_dtype(456), np_dtype(123)]
    assert proc.returncode == 0


@pytest.mark.slow
def test_gather_tensors(
    cpp_dragon_compile,
    ddict,
    client,
    np_dtype,
    cpp_type_name,
):
    cpp_put_delay = 3
    cpp_iota_tensor = _TestTensorValues("cpp_iota_tensor", (4, 5))
    cpp_zeros_tensor = _TestTensorValues("cpp_zeros_tensor", (3, 6, 7, 2))
    cpp_ones_tensor = _TestTensorValues("cpp_ones_tensor", (2, 2, 2, 2, 2))

    py_iota_tensor = _TestTensorValues("py-iota-tensor", (3, 3, 3))
    py_zeros_tensor = _TestTensorValues("py-zeros-tensor-key", (5,))
    py_ones_tensor = _TestTensorValues("py-ones-tensor-key", (5, 6, 7, 8))

    bin_ = cpp_dragon_compile(textwrap.dedent(f"""\
        #include "radex/dragon.hpp"
        #include "radex/handles.hpp"
        #include <chrono>
        #include <numeric>
        #include <string>
        #include <thread>
        #include <vector>

        int main(void) {{
            timespec timeout {{5, 0}};
            radex::drg::ddict::Client client {{"{ddict.serialize()}", &timeout}};

            std::vector<{cpp_type_name}> x_py_zeros_data({py_zeros_tensor.size}, 0);
            std::vector<radex::detail::MetaInt> x_py_zeros_dims
                {py_ones_tensor.cpp_dims_init_list};
            std::vector<{cpp_type_name}> x_py_ones_data({py_ones_tensor.size}, 1);
            std::vector<radex::detail::MetaInt> x_py_ones_dims
                {py_ones_tensor.cpp_dims_init_list};

            std::vector<{cpp_type_name}> cpp_iota_tensor({cpp_iota_tensor.size});
            std::iota(cpp_iota_tensor.begin(), cpp_iota_tensor.end(), 0);
            client.put_tensor(
                radex::data::OutgoingHandle("{cpp_zeros_tensor.key}"),
                {cpp_zeros_tensor.cpp_dims_init_list},
                std::vector<{cpp_type_name}>({cpp_zeros_tensor.size}, 0));
            client.put_tensor(
                radex::data::OutgoingHandle("{cpp_ones_tensor.key}"),
                {cpp_ones_tensor.cpp_dims_init_list},
                std::vector<{cpp_type_name}>({cpp_ones_tensor.size}, 1));
            std::this_thread::sleep_for(std::chrono::seconds({cpp_put_delay}));
            client.put_tensor(
                radex::data::OutgoingHandle("{cpp_iota_tensor.key}"),
                {cpp_iota_tensor.cpp_dims_init_list},
                cpp_iota_tensor);

            std::vector<radex::data::IncomingHandle> in_handles {{
                radex::data::IncomingHandle("{py_iota_tensor.key}"),
                radex::data::IncomingHandle("{py_zeros_tensor.key}"),
                radex::data::IncomingHandle("{py_ones_tensor.key}"),
            }};
            auto got_tensors = client.gather_tensors<{cpp_type_name}>(
                in_handles, std::chrono::milliseconds({10_000}));

            std::vector<{cpp_type_name}> x_py_iota_data({py_iota_tensor.size});
            std::iota(x_py_iota_data.begin(), x_py_iota_data.end(), 0);
            std::vector<std::pair<std::vector<radex::detail::MetaInt>,
                                  std::vector<{cpp_type_name}>>>
                x_tensors {{
                    {{ {py_iota_tensor.cpp_dims_init_list}, x_py_iota_data }},
                    {{ {py_zeros_tensor.cpp_dims_init_list},
                       std::vector<{cpp_type_name}>({py_zeros_tensor.size}, 0) }},
                    {{ {py_ones_tensor.cpp_dims_init_list},
                       std::vector<{cpp_type_name}>({py_ones_tensor.size}, 1) }} }};

            if (got_tensors.size() != in_handles.size())
                throw std::logic_error("Got different number of tensors than handles");

            if (got_tensors.size() != x_tensors.size())
                throw std::logic_error("Did not get expected number of tensors");

            for (int i = 0; i < got_tensors.size(); i++) {{
                const auto& [got_dims, got_data] = got_tensors[i];
                const auto& [x_dims, x_data] = x_tensors[i];
                std::string err_header = std::string("Tensor ") + std::to_string(i);
                if (got_dims != x_dims)
                    throw std::logic_error(err_header + " dims did not match");
                if (got_data != x_data)
                    throw std::logic_error(err_header + " data did not match");
            }}

            return 0;
        }}
        """))

    assert not any(
        client.contains(t.key)
        for t in (
            cpp_iota_tensor,
            cpp_zeros_tensor,
            cpp_ones_tensor,
            py_iota_tensor,
            py_zeros_tensor,
            py_ones_tensor,
        )
    )

    make_iota = lambda info: np.arange(0, info.size, dtype=np_dtype).reshape(info.shape)
    make_zeros = lambda info: np.zeros(info.shape, dtype=np_dtype)
    make_ones = lambda info: np.ones(info.shape, dtype=np_dtype)

    client.put_tensor(OutgoingHandle(py_ones_tensor.key), make_ones(py_ones_tensor))
    client.put_tensor(OutgoingHandle(py_iota_tensor.key), make_iota(py_iota_tensor))
    in_handles, x_cpp_tensors = zip(
        *(
            (IncomingHandle(info.key), make(info))
            for info, make in (
                (cpp_zeros_tensor, make_zeros),
                (cpp_iota_tensor, make_iota),
                (cpp_ones_tensor, make_ones),
            )
        )
    )

    try:
        proc = Popen(executable=os.fspath(bin_), args=[])
        start_t = time.perf_counter()
        got_cpp_tensors = client.gather_tensors(list(in_handles), 10)
        py_wait_time = time.perf_counter() - start_t

        client.put_tensor(
            OutgoingHandle(py_zeros_tensor.key),
            make_zeros(py_zeros_tensor),
        )
    except Exception:
        proc.kill()
        raise
    finally:
        proc.wait()
    wait_interval = 2.0
    assert cpp_put_delay - wait_interval < py_wait_time < cpp_put_delay + wait_interval

    assert len(got_cpp_tensors) == len(x_cpp_tensors) == len(in_handles)
    for got_tensor, x_tensor in zip(got_cpp_tensors, x_cpp_tensors):
        assert got_tensor.dtype == x_tensor.dtype == np_dtype
        assert got_tensor.shape == x_tensor.shape
        assert (got_tensor == x_tensor).all()
    assert proc.returncode == 0
