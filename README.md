# graphene-sqlalchemy-sort

```python
class ExampleSort(SortSet):
    class Meta:
        model = Example
        fields = ["first_name", "second_name", "name"]

    @classmethod
    def name_sort(cls):
        return case(
            [
                (Example.second_name.is_(None), Example.first_name),
                (Example.first_name.is_(None), Example.second_name),
            ],
            else_=Example.second_name,
        )



Query:
"""
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

```