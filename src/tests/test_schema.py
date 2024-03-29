from datetime import datetime

from .schema import schema


def test_examples_query(example_factory, db_session):
    example = example_factory(first_name="test")
    query = """
        {
            examples {
                edges {
                    node {
                        firstName
                    }
                }
            }
        }
    """
    expected_result = {
        "examples": {"edges": [{"node": {"firstName": example.first_name}}]}
    }

    result = schema.execute(query, context_value={"session": db_session})

    assert result.data == expected_result


def test_examples_sorting_default_field_ASC(example_factory, db_session):
    example1 = example_factory(first_name="test")
    example2 = example_factory(first_name="atest")
    query = """
        {
            examples (sort: {firstName: "ASC"}) {
                edges {
                    node {
                        firstName
                    }
                }
            }
        }
    """
    expected_result = {
        "examples": {
            "edges": [
                {"node": {"firstName": example2.first_name}},
                {"node": {"firstName": example1.first_name}},
            ]
        }
    }

    result = schema.execute(query, context_value={"session": db_session})

    assert result.errors is None
    assert result.data == expected_result


def test_examples_sorting_default_field_DESC(example_factory, db_session):
    example1 = example_factory(first_name="test")
    example2 = example_factory(first_name="atest")
    query = """
        {
            examples (sort: {firstName: "DESC"}) {
                edges {
                    node {
                        firstName
                    }
                }
            }
        }
    """
    expected_result = {
        "examples": {
            "edges": [
                {"node": {"firstName": example1.first_name}},
                {"node": {"firstName": example2.first_name}},
            ]
        }
    }

    result = schema.execute(query, context_value={"session": db_session})

    assert result.errors is None
    assert result.data == expected_result


def test_examples_sorting_custom_field_DESC(example_factory, db_session):
    example1 = example_factory(first_name="test", second_name="bmarek")
    example2 = example_factory(first_name="jurek", second_name="ak")
    example3 = example_factory(first_name="atest", second_name=None)
    query = """
        {
            examples (sort: {name: "ASC"}) {
                edges {
                    node {
                        firstName
                    }
                }
            }
        }
    """
    expected_result = {
        "examples": {
            "edges": [
                {"node": {"firstName": example2.first_name}},
                {"node": {"firstName": example3.first_name}},
                {"node": {"firstName": example1.first_name}},
            ]
        }
    }

    result = schema.execute(query, context_value={"session": db_session})

    assert result.errors is None
    assert result.data == expected_result


def test_examples_sorting_custom_field_DESC_using_join(
    example_factory, item_factory, db_session
):
    example1 = example_factory(
        first_name="x",
        items=[item_factory(created=datetime(year=2021, month=12, day=1))],
    )
    example2 = example_factory(
        first_name="y",
        items=[item_factory(created=datetime(year=2022, month=12, day=1))],
    )
    example3 = example_factory(
        first_name="z",
        items=[item_factory(created=datetime(year=2011, month=12, day=1))],
    )

    query = """
        {
            examples (sort: {itemCreated: "DESC"}) {
                edges {
                    node {
                        firstName
                    }
                }
            }
        }
    """
    expected_result = {
        "examples": {
            "edges": [
                {"node": {"firstName": example2.first_name}},
                {"node": {"firstName": example1.first_name}},
                {"node": {"firstName": example3.first_name}},
            ]
        }
    }

    result = schema.execute(query, context_value={"session": db_session})

    assert result.errors is None
    assert result.data == expected_result
