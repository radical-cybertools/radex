import os
import textwrap
from collections.abc import Iterable

import dragon
import numpy as np
from dragon.native.process import Popen


def _comma_seperate_ints(ints: Iterable[int]) -> str:
    return ", ".join(str(i) for i in ints)


def test_get_cpp_scalar(cpp_dragon_compile, ddict, client, np_dtype, cpp_type_name):
    key = "some-scalar"
    bin_ = cpp_dragon_compile(textwrap.dedent(f"""\
        #include "radex/dragon.hpp"

        int main(void) {{
            timespec timeout {{5, 0}};
            radex::drg::ddict::Client client {{"{ddict.serialize()}", &timeout}};
            {cpp_type_name} value = 123;
            client.put_scalar("{key}", value);
            return 0;
        }}
        """))

    assert not client.contains(key)
    proc = Popen(executable=os.fspath(bin_), args=[])
    proc.wait()
    assert proc.returncode == 0

    assert client.contains(key)
    value = client.get_scalar(key)
    assert value.dtype == np_dtype
    assert value == np_dtype(123)


def test_get_cpp_tensor(cpp_dragon_compile, ddict, client, np_dtype, cpp_type_name):
    n_elements = 12
    tensors = {
        "tensor-1d": (12,),
        "tensor-2d": (6, 2),
        "tensor-3d": (2, 3, 2),
    }

    put_tensors = "\n".join(
        f'client.put_tensor("{key}", {{{_comma_seperate_ints(shape)}}}, tensor);'
        for key, shape in tensors.items()
    )
    bin_ = cpp_dragon_compile(textwrap.dedent(f"""\
        #include "radex/dragon.hpp"
        #include <vector>
        #include <numeric>

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
    proc = Popen(executable=os.fspath(bin_), args=[])
    proc.wait()
    assert proc.returncode == 0

    expected = np.arange(n_elements, dtype=np_dtype)
    for key, shape in tensors.items():
        assert client.contains(key)
        ret = client.get_tensor(key)
        assert ret.dtype == np_dtype
        assert ret.shape == shape
        assert (ret == expected.reshape(shape)).all()


def test_put_py_scalar(cpp_dragon_compile, ddict, client, np_dtype, cpp_type_name):
    key = "some-scalar"
    bin_ = cpp_dragon_compile(textwrap.dedent(f"""\
        #include "radex/dragon.hpp"

        int main(void) {{
            timespec timeout {{5, 0}};
            radex::drg::ddict::Client client {{"{ddict.serialize()}", &timeout}};
            auto x = client.get_scalar<{cpp_type_name}>("{key}");
            return x == 34 ? 0 : 1;
        }}
        """))

    assert not client.contains(key)
    client.put_scalar(key, np_dtype(34))
    assert client.contains(key)

    proc = Popen(executable=os.fspath(bin_), args=[])
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
        #include <vector>
        #include <numeric>
        #include <exception>

        template <typename T>
        void eval_tensor(radex::IClient& client,
                         const std::string& key,
                         const std::vector<radex::detail::MetaInt>& expected_dims,
                         const std::vector<T>& expected_data) {{
            auto [dims, data] = client.get_tensor<T>(key);
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
        client.put_tensor(key, tensor)
    assert all(client.contains(tensor) for tensor in tensors)

    proc = Popen(executable=os.fspath(bin_), args=[])
    proc.wait()
    assert proc.returncode == 0
