import graphene
from .mutations.mutations import MutationUser
from .queries.queries import Query

user_schema = graphene.Schema(query=Query, mutation=MutationUser)