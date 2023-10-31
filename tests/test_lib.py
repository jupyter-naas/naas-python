import pytest


def test_lib_add_import():
    import naas_python as naas

    # Test if ``naas.space.add`` is a valid method and callable

    assert callable(naas.space.add)


def test_missing_keys_call():
    import naas_python as naas

    # Test if ``naas.space.add`` is a valid method and callable

    with pytest.raises(TypeError):
        naas.space.add()
