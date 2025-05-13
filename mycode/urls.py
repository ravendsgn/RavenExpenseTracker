from django.contrib import admin
from django.urls import path,include,re_path
from django.views.generic.base import RedirectView

fav_icon = RedirectView.as_view(url='/static/icons/favicon.ico', permanent=True)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('expenses/', include('userexpense.urls')),
    path('', include('dashboard.urls')),
    path('auth/', include('allauth.urls')),
    path('income/', include('userincome.urls')),
    path('preferences/', include('userprefer.urls')),
    re_path(r'^favicon\.ico$', fav_icon),
]
