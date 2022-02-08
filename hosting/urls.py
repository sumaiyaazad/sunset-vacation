from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()


urlpatterns = [
    path('categories/', views.getCategories, name="getCategories"),
    path('subcategories/<str:category>/', views.getSubCategories, name="getSubCategories"),
    path('properties/', views.PropertyHostingView.as_view()),
    path('properties/<int:hosting_id>/', views.PropertyHostingView.as_view()),
    # path('', include(router.urls))
]
