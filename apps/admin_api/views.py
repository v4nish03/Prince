from django.shortcuts import render
from graphene_django.views import GraphQLView
from .middleware import graphql_jwt_middleware
from .schema import schema 

class PrivateGraphQLView(GraphQLView):
    def get_context(self, request):
        return request

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.middleware = [graphql_jwt_middleware]