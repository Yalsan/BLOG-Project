from django.urls import path
from . import views

urlpatterns = [
    path("", views.Homepage, name="homepage"),
    path("category/<str:cat_name>/", views.categoryview, name="categoryview"),

    path("post/create/", views.post_create, name="post_create"),
    path("post/<int:id>/", views.article_detail, name="article_detail"),
    path("post/<int:id>/edit/", views.update, name="update"),
    path("post/<int:id>/delete/", views.post_delete, name="post_delete"),

    path("load-more/", views.load_more_articles, name="load_more_articles"),

    path("contact/", views.contact_page, name="contact"),
    path("contact/submit/", views.contact_htmx, name="contact_htmx"),

    path("signup/", views.sign_up, name="signup"),
    path("signin/", views.sign_in, name="signin"),
    path("logout/", views.log_out, name="logout"),
]
