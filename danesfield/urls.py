from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_extensions.routers import ExtendedSimpleRouter

from danesfield.core.views.dataset import DatasetRunViewSet, DatasetViewSet

router = ExtendedSimpleRouter()
dataset_routes = router.register('datasets', DatasetViewSet)
dataset_routes.register(
    'runs',
    DatasetRunViewSet,
    basename='run',
    parents_query_lookups=[f'dataset__{DatasetViewSet.lookup_field}'],
)


# OpenAPI generation
schema_view = get_schema_view(
    openapi.Info(title='Danesfield', default_version='v1', description=''),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('admin/', admin.site.urls),
    path('api/s3-upload/', include('s3_file_field.urls')),
    path('api/', include(router.urls)),
    path('api/docs/redoc/', schema_view.with_ui('redoc'), name='docs-redoc'),
    path('api/docs/swagger/', schema_view.with_ui('swagger'), name='docs-swagger'),
    path('', include('rgd.urls')),
    path('', include('rgd_3d.urls')),
    path('', include('rgd_imagery.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
