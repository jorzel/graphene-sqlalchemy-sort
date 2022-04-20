from typing import TYPE_CHECKING

import graphene
from graphene.types.inputobjecttype import InputObjectTypeOptions
from sqlalchemy import desc, inspection, nullslast
from sqlalchemy.orm.attributes import InstrumentedAttribute

if TYPE_CHECKING:
    from typing import Iterable


def _custom_field_func_name(custom_field: str) -> str:
    return custom_field + "_sort"


def is_model_joined(query, model) -> bool:
    if hasattr(query, "_compile_state"):  # SQLAlchemy >= 1.4
        join_entities = query._compile_state()._join_entities  # type: ignore
    else:
        join_entities = query._join_entities  # type: ignore
    if model in [mapper.class_ for mapper in join_entities]:
        return True
    return False


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
        for field in sort_fields:
            if not hasattr(cls, _custom_field_func_name(field)):
                continue
            graphql_sort_fields[field] = graphene.InputField(graphene.String)
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
            if hasattr(cls, _custom_field_func_name(_field)):
                query, _field = getattr(cls, _custom_field_func_name(_field))(query)
            if ordering.strip().lower() == "desc":
                _field = nullslast(desc(_field))
            else:
                _field = nullslast(_field)
            sort_fields.append(_field)
        return query.order_by(*sort_fields)
