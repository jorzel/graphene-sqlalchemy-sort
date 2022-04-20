from sort import schema


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

    result = schema.execute(query, context={"session": db_session})

    assert result.data == expected_result
