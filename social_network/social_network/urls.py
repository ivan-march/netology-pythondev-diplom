from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from posts.views import PostViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include(router.urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
