# graphene-sqlalchemy-sort
Customized sorting for: https://github.com/graphql-python/graphene-sqlalchemy

Inspiration: https://github.com/art1415926535/graphene-sqlalchemy-filter

```python

class Example(Base):
    __tablename__ = "example"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    second_name = Column(String)
    items = relationship("Item", uselist=True, lazy="dynamic")


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime)
    example_id = Column(
        Integer, ForeignKey("example.id", ondelete="CASCADE"), index=True
    )


class ExampleNode(SQLAlchemyObjectType):
    class Meta:
        model = Example
        interfaces = (graphene.relay.Node,)


class ExampleSort(SortSet):
    class Meta:
        model = Example
        fields = ["first_name", "second_name", "name", "item_created"]

    @classmethod
    def name_sort(cls, query):
        return query, case(
            [
                (Example.second_name.is_(None), Example.first_name),
                (Example.first_name.is_(None), Example.second_name),
            ],
            else_=Example.second_name,
        )

    @classmethod
    def item_created_sort(cls, query):
        if not is_model_joined(query, Item):
            query = query.join("items")
        return query, Item.created


class Query(graphene.ObjectType):
    examples = SQLAlchemyConnectionField(ExampleNode, sort=ExampleSort())

    def resolve_examples(self, info, **kwargs):
        query = info.context["session"].query(Example)
        if kwargs.get("sort"):
            query = ExampleSort().sort(query, kwargs["sort"])
        return query


schema = graphene.Schema(query=Query)
```


## Sorting using default field
```yaml
{
    examples (sort: {firstName: "ASC"}) {
        edges {
            node {
                firstName
            }
        }
    }
}
```


## Sorting using custom field
```yaml
{
    examples (sort: {name: "ASC"}) {
        edges {
            node {
                firstName
            }
        }
    }
}
```

## Sorting using custom field with join
```yaml
{
    examples (sort: {itemCreated: "DESC"}) {
        edges {
            node {
                firstName
            }
        }
    }
}
```