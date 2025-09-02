import graphene
from .queries.queriesAdmin import Query
from .mutations.mutationsAdmin import MutationAdmin
from .middleware import graphql_jwt_middleware

schema = graphene.Schema(query=Query, mutation=MutationAdmin)
