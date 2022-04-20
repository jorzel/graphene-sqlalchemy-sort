from sort import Example


def test_example():
    example = Example(first_name="test")

    assert example.first_name == "test"
