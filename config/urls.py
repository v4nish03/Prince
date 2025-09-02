"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.urls import path
from apps.user_api.views import UserFileUploadGraphQLView
from graphene_django.views import GraphQLView
from apps.admin_api.schema import schema as admin_schema
from apps.admin_api.views import PrivateGraphQLView
from apps.user_api.schema_user import user_schema as user_schema
from django.views.decorators.csrf import csrf_exempt
from apps.superadmin_api.schema_superadmin import superadmin_schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/admin/', csrf_exempt(PrivateGraphQLView.as_view(graphiql=True, schema=admin_schema))),
    path('graphql/user/', csrf_exempt(UserFileUploadGraphQLView.as_view(graphiql=True, schema=user_schema))),
    path('graphql/superadmin/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=superadmin_schema)))
]

