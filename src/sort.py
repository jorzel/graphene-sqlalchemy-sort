import logging
from typing import TYPE_CHECKING

import graphene
from graphene.types.inputobjecttype import InputObjectTypeOptions
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    case,
    create_engine,
    desc,
    inspection,
    nullslast,
)
from sqlalchemy.orm import configure_mappers, declarative_base
from sqlalchemy.orm.attributes import InstrumentedAttribute

if TYPE_CHECKING:
    from typing import Iterable

# logging config
LOGGER_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# db config
DB_URI = "sqlite:///:memory:"
engine = create_engine(DB_URI)
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Example(Base):
    __tablename__ = "example"

    id = Column(Integer, primary_key=True, autoincrement=True)
    counter = Column(Integer, default=0, nullable=False)
    first_name = Column(String)
    second_name = Column(String)

    def __str__(self):
        return f"Example(id={self.id}, first_name={self.first_name}, second_name={self.second_name}"

    __repr__ = __str__


configure_mappers()


class ExampleNode(SQLAlchemyObjectType):
    class Meta:
        model = Example
        interfaces = (graphene.relay.Node,)


class SortSetOptions(InputObjectTypeOptions):
    model = None
    fields = None


class SortSet(graphene.InputObjectType):
    model = None

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls, model=None, fields=None, _meta=None, **options
    ):
        if model is None and fields:
            raise AttributeError("Model not specified")

        if not _meta:
            _meta = SortSetOptions(cls)

        cls.model = model
        _meta.model = model

        _meta.fields = cls._generate_default_sort_fields(model, fields)
        _meta.fields.update(cls._generate_custom_sort_fields(model, fields))
        if not _meta.fields:
            _meta.fields = {}
        super().__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def _generate_default_sort_fields(cls, model, sort_fields: "Iterable[str]"):
        graphql_sort_fields = {}
        model_fields = cls._get_model_fields(model, sort_fields)
        for field_name, field_object in model_fields.items():
            graphql_sort_fields[field_name] = graphene.InputField(graphene.String)
        return graphql_sort_fields

    @classmethod
    def _generate_custom_sort_fields(cls, model, sort_fields: "Iterable[str]"):
        graphql_sort_fields = {}
        for sort_field in sort_fields:
            if not hasattr(cls, sort_field + "_sort"):
                continue
            graphql_sort_fields[sort_field] = graphene.InputField(graphene.String)
        return graphql_sort_fields

    @classmethod
    def _get_model_fields(cls, model, only_fields: "Iterable[str]"):
        model_fields = {}
        inspected = inspection.inspect(model)
        for descr in inspected.all_orm_descriptors:
            if isinstance(descr, InstrumentedAttribute):
                attr = descr.property
                name = attr.key
                if name not in only_fields:
                    continue

                column = attr.columns[0]
                model_fields[name] = {
                    "column": column,
                    "type": column.type,
                    "nullable": column.nullable,
                }
        return model_fields

    @classmethod
    def sort(cls, query, args):
        sort_fields = []
        for field, ordering in args.items():
            _field = field
            custom_field = field + "_sort"
            if hasattr(cls, custom_field):
                _field = getattr(cls, custom_field)()
            if ordering.strip().lower() == "desc":
                _field = nullslast(desc(_field))
            else:
                _field = nullslast(_field)
            sort_fields.append(_field)
        return query.order_by(*sort_fields)


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


class SchemaQuery(graphene.ObjectType):
    examples = SQLAlchemyConnectionField(
        ExampleNode,
        sort=ExampleSort(),
    )

    def resolve_examples(self, info, **kwargs):
        query = info.context["session"].query(Example)
        if kwargs.get("sort"):
            query = ExampleSort().sort(query, kwargs["sort"])
        return query


schema = graphene.Schema(query=SchemaQuery)
