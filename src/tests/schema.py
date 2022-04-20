import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from sqlalchemy import case

from sort import SortSet, is_model_joined

from .models import Example, Item


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


class SchemaQuery(graphene.ObjectType):
    examples = SQLAlchemyConnectionField(ExampleNode, sort=ExampleSort())

    def resolve_examples(self, info, **kwargs):
        query = info.context["session"].query(Example)
        if kwargs.get("sort"):
            query = ExampleSort().sort(query, kwargs["sort"])
        return query


schema = graphene.Schema(query=SchemaQuery)
