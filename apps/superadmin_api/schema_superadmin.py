import graphene
from .queries.queriesSuper import Query as SuperAdminQuery
from .mutations.mutationsSuper import Mutation as SuperAdminMutation

class Query(SuperAdminQuery, graphene.ObjectType):
    pass

class Mutation(SuperAdminMutation, graphene.ObjectType):
    pass

superadmin_schema = graphene.Schema(query=Query, mutation=Mutation)