from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.HomeView.as_view(), name='home'),
    path('<int:pk>/graph/', views.graph_view , name='graph'),
    path('<int:pk>/edit/', views.edit_view , name='edit'),
    path('<int:pk>/auth/', views.auth_view , name='auth'),
    path('logout/', views.logout_view , name='logout'),
    path('<int:pk>/update/', views.update_view, name='update'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
