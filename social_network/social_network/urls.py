from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from posts.views import PostDetailAPIView, PostListAPIView


urlpatterns = [
    path('api/posts/', PostListAPIView.as_view(), name='post-list'),
    path('api/posts/<int:pk>/', PostDetailAPIView.as_view(), name='post-detail'),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
