# mi_app/scalars.py
import decimal
from graphene.types import Scalar
from graphql.language import ast

class Decimal(Scalar):
    @staticmethod
    def serialize(dec):
        assert isinstance(dec, decimal.Decimal), (
            f'Valor recibido no compatible con Decimal: "{repr(dec)}"'
        )
        return str(dec)

    @staticmethod
    def parse_value(value):
        if isinstance(value, decimal.Decimal):
            return value
        if isinstance(value, str):
            try:
                return decimal.Decimal(value)
            except decimal.InvalidOperation:
                raise ValueError(f'El valor "{value}" no puede convertirse a Decimal.')
        raise ValueError(f'El valor "{value}" no puede convertirse a Decimal.')

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, (ast.StringValue, ast.IntValue, ast.FloatValue)):
            try:
                return cls.parse_value(node.value)
            except ValueError:
                raise ValueError(f'No se puede convertir el literal "{node.value}" a Decimal.')
        raise ValueError(f'No se puede convertir el literal "{node}" a Decimal.')