from django.urls import path
from .views import load_districts, load_thanas, load_post_offices

urlpatterns = [
    path('ajax/load-districts/', load_districts),
    path('ajax/load-thanas/', load_thanas),
    path('ajax/load-post/', load_post_offices),
]
