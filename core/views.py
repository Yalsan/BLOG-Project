
from django.shortcuts import render,redirect
from .models import *
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import ArticleForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import auth

def Homepage(request):
    articles = Article.objects.all()
    return render(request, 'index.html', {'articles':articles})

def categoryview(request, cat_name):
    category = get_object_or_404(Category, name=cat_name)
    category_articles = Article.objects.filter(category=category)
    return render(request, 'categories.html', {
        'category': category,
        'category_articles': category_articles,
    })



@login_required
def post_create(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        content = (request.POST.get("content") or "").strip()
        category_id = request.POST.get("category")
        image = request.FILES.get("image")

        if not title or not content or not category_id:
            return render(request, "create.html", {
                "categories": categories,
                "error": "Fill all fields",
            })

        category = get_object_or_404(Category, id=category_id)

        Article.objects.create(
            title=title,
            content=content,
            category=category,
            author=request.user,
            image=image,
        )

        return redirect("homepage")

    return render(request, "create.html", {"categories": categories})



@login_required
def update(request, id):
    article = get_object_or_404(Article, id=id)
    categories = Category.objects.all()

    if request.method == "POST":
        article.title = request.POST.get("title", "").strip()
        article.content = request.POST.get("content", "").strip()

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
        return redirect("homepage")

    return render(request, "edit_page.html", {
        "article": article,
        "categories": categories,
    })
def post_delete(request, id):
    post = get_object_or_404(Article, id=id)
    if request.method == 'POST':
        post.delete()
        return redirect('homepage')
    return render(request, 'delete.html', {'post': post})



def article_detail(request, id):
    article = get_object_or_404(Article, id=id)
    is_author = request.user.is_authenticated and request.user == article.author

    if request.method == "POST":
        if is_author and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.POST.get('delete'):
                article.delete()
                return JsonResponse({'status': 'deleted'})

            form = ArticleForm(request.POST, instance=article)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors})

    else:
        form = ArticleForm(instance=article) if is_author else None

    return render(request, 'article_details.html', {
        'article': article,
        'form': form,
        'is_author': is_author,
    })




def sign_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already exists.")
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email already exists.")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect('homepage') 
        else:
            messages.error(request, "Passwords do not match.")
            return redirect('homepage')

    return render(request, "sign_up.html")

def sign_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect("homepage")
        else:
            messages.info(request,'Username or Password is incorrect')
            return redirect("signin")
            
    return render(request,"login_page.html")

@require_POST
def log_out(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('homepage')


    