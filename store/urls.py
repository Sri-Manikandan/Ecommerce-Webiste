from django.urls import path
from . import views
app_name = 'store'
urlpatterns = [
    path('', views.store, name="store"),
    path('store/', views.store1, name="store1"),
    path('store/<category>', views.store1, name="store1"),
   
]
