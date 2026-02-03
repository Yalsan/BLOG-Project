from django.urls import path
from . import views

urlpatterns = [
    path('', views.Homepage, name='homepage'),
    #path('create/',views.post_create, name='create'),
    #path('<int:id>/delete/', views.post_delete, name='delete'),
    path('category/<str:cat_name>/', views.categoryview, name='category'),
    path('create/',views.post_create, name='create'),
    path('article/<int:id>/', views.article_detail, name='article_detail'),
    path("signin",views.sign_in,name="signin"),
    path("signup",views.sign_up,name='signup'),
    path('logout/', views.log_out, name='logout'),
    path("edit/<int:id>/",views.update, name="update"),
    path("delete/<int:id>/", views.post_delete, name="post_delete"),


]