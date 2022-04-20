from sort import Example


def test_example(example_factory):
    example = example_factory(first_name="test")

    assert example.first_name == "test"


def test_example_ordering(example_factory, db_session):
    example1 = example_factory(first_name="test", second_name="cest")
    example2 = example_factory(first_name="atest", second_name="atest")
    example3 = example_factory(first_name="atest", second_name="ttest")

    results = (
        db_session.query(Example)
        .order_by(Example.first_name)
        .order_by(Example.second_name.desc())
    ).all()

    assert results == [example3, example2, example1]
