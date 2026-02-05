from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .models import Article, Category, Contact
from .forms import ArticleForm


def is_htmx(request):
    return request.headers.get("HX-Request") == "true"


def Homepage(request):
    articles_qs = Article.objects.order_by("-date")
    paginator = Paginator(articles_qs, 5)
    page_obj = paginator.get_page(1)

    ctx = {"articles": page_obj}

    if is_htmx(request):
        return render(request, "partials/home_content.html", ctx)

    return render(request, "index.html", ctx)


def categoryview(request, cat_name):
    category = get_object_or_404(Category, name=cat_name)
    category_articles = Article.objects.filter(category=category).order_by("-date")

    ctx = {"category": category, "category_articles": category_articles}

    if is_htmx(request):
        return render(request, "partials/categories_content.html", ctx)

    return render(request, "categories.html", ctx)


def contact_page(request):
    if is_htmx(request):
        return render(request, "partials/contact_content.html")
    return render(request, "contact.html")


def article_detail(request, id):
    article = get_object_or_404(Article, id=id)
    is_author = request.user.is_authenticated and request.user == article.author
    form = ArticleForm(instance=article) if is_author else None

    ctx = {
        "article": article,
        "form": form,
        "is_author": is_author,
    }

    if is_htmx(request):
        return render(request, "partials/article_detail_content.html", ctx)

    return render(request, "article_details.html", ctx)


@login_required
def post_create(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        content = (request.POST.get("content") or "").strip()
        category_id = request.POST.get("category")
        image = request.FILES.get("image")

        if not title or not content or not category_id:
            ctx = {"categories": categories, "error": "Fill all fields"}
            if is_htmx(request):
                return render(request, "partials/create_content.html", ctx)
            return render(request, "create.html", ctx)

        category = get_object_or_404(Category, id=category_id)

        Article.objects.create(
            title=title,
            content=content,
            category=category,
            author=request.user,
            image=image,
        )

        if is_htmx(request):
            articles_qs = Article.objects.order_by("-date")
            paginator = Paginator(articles_qs, 5)
            page_obj = paginator.get_page(1)
            return render(request, "partials/home_content.html", {"articles": page_obj})

        return redirect("homepage")

    ctx = {"categories": categories}
    if is_htmx(request):
        return render(request, "partials/create_content.html", ctx)
    return render(request, "create.html", ctx)


@login_required
def update(request, id):
    article = get_object_or_404(Article, id=id)
    categories = Category.objects.all()

    if request.method == "POST":
        article.title = (request.POST.get("title") or "").strip()
        article.content = (request.POST.get("content") or "").strip()

        category_id = request.POST.get("category")
        if category_id:
            article.category = get_object_or_404(Category, id=category_id)

        if request.POST.get("remove_image") == "1":
            if article.image:
                article.image.delete(save=False)
            article.image = None

        new_image = request.FILES.get("image")
        if new_image:
            if article.image:
                article.image.delete(save=False)
            article.image = new_image

        article.save()

        is_author = request.user == article.author
        form = ArticleForm(instance=article) if is_author else None
        ctx = {"article": article, "form": form, "is_author": is_author}

        if is_htmx(request):
            return render(request, "partials/article_detail_content.html", ctx)

        return redirect("article_detail", id=article.id)

    ctx = {"article": article, "categories": categories}
    if is_htmx(request):
        return render(request, "partials/edit_content.html", ctx)
    return render(request, "edit_page.html", ctx)


def post_delete(request, id):
    post = get_object_or_404(Article, id=id)

    if request.method == "POST":
        post.delete()

        if is_htmx(request):
            articles_qs = Article.objects.order_by("-date")
            paginator = Paginator(articles_qs, 5)
            page_obj = paginator.get_page(1)
            return render(request, "partials/home_content.html", {"articles": page_obj})

        return redirect("homepage")

    ctx = {"post": post}
    if is_htmx(request):
        return render(request, "partials/delete_content.html", ctx)
    return render(request, "delete.html", ctx)


def sign_up(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        password2 = request.POST.get("password2") or ""

        if password != password2:
            ctx = {"error": "Passwords do not match"}
            if is_htmx(request):
                return render(request, "partials/signup_content.html", ctx)
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            ctx = {"error": "Username already exists"}
            if is_htmx(request):
                return render(request, "partials/signup_content.html", ctx)
            messages.info(request, "Username already exists.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            ctx = {"error": "Email already exists"}
            if is_htmx(request):
                return render(request, "partials/signup_content.html", ctx)
            messages.info(request, "Email already exists.")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)

        if is_htmx(request):
            articles_qs = Article.objects.order_by("-date")
            paginator = Paginator(articles_qs, 5)
            page_obj = paginator.get_page(1)
            return render(request, "partials/home_content.html", {"articles": page_obj})

        return redirect("homepage")

    if is_htmx(request):
        return render(request, "partials/signup_content.html")
    return render(request, "sign_up.html")


def sign_in(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if is_htmx(request):
                articles_qs = Article.objects.order_by("-date")
                paginator = Paginator(articles_qs, 5)
                page_obj = paginator.get_page(1)
                return render(request, "partials/home_content.html", {"articles": page_obj})

            return redirect("homepage")

        ctx = {"error": "Username or Password is incorrect"}
        if is_htmx(request):
            return render(request, "partials/signin_content.html", ctx)
        messages.info(request, "Username or Password is incorrect")
        return redirect("signin")

    if is_htmx(request):
        return render(request, "partials/signin_content.html")
    return render(request, "login_page.html")


@require_POST
def log_out(request):
    logout(request)

    if is_htmx(request):
        articles_qs = Article.objects.order_by("-date")
        paginator = Paginator(articles_qs, 5)
        page_obj = paginator.get_page(1)
        return render(request, "partials/home_content.html", {"articles": page_obj})

    messages.success(request, "You have been logged out.")
    return redirect("homepage")


def load_more_articles(request):
    page_number = request.GET.get("page", 1)
    articles_qs = Article.objects.order_by("-date")
    paginator = Paginator(articles_qs, 5)
    page_obj = paginator.get_page(page_number)

    return render(request, "partials/article_list.html", {"articles": page_obj})


@require_POST
def contact_htmx(request):
    name = (request.POST.get("name") or "").strip()
    email = (request.POST.get("email") or "").strip()
    subject = (request.POST.get("subject") or "").strip()
    message = (request.POST.get("message") or "").strip()

    if not name or not email or not message:
        return HttpResponse("<p>Fill required fields.</p>")

    Contact.objects.create(
        name=name,
        email=email,
        subject=subject,
        message=message
    )

    return HttpResponse("<p>Message sent successfully!</p>")
