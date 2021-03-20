import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Subquery
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post


def paginator_func(queryset, page):
    paginator = Paginator(queryset, 10)
    is_page_number = bool(page)
    page_number = page if is_page_number else 1
    page_obj = paginator.page(page_number)
    return page_obj


def index(request):

    if request.method == 'POST':
        user_id = request.user.id
        text = request.POST['text']
        Post(user_id=user_id, text=text).save()

    index_template = loader.get_template('network/index.html')
    all_posts = Post.objects.all().order_by('-posted')
    # all_posts2 = Post.objects.annotate(is_post_liked_by_user=Subquery(all_posts.))
    all_posts2 = []
    for post in all_posts:
        post.is_liked_by_user = post.liked_by.filter(id=request.user.id).exists()
        print(post.is_liked_by_user)
        all_posts2.append(post)

    page_obj = paginator_func(queryset=all_posts2, page=request.GET.get('page'))

    context = {"all_posts": page_obj}

    return HttpResponse(index_template.render(context, request))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
@login_required
def edit_post(request):
    if request.method == "PUT":  # only for JavaScript - edit-post

        data = json.loads(request.body)
        post_id = data.get('post_id')

        try:  # маловероятно
            post = Post.objects.get(user_id=request.user.id, pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)

        # validation post author == user
        if post.user.id != request.user.id:
            return JsonResponse({"error": "YOU SHALL NOT PAAASSSS!!!"}, status=404)

        if data.get("edited"):
            post.text = data['text']
            post.edited = data["edited"]
            post.save()

        return HttpResponse(status=204)

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)


def profile(request, username):
    profile_template = loader.get_template('network/profile.html')
    user = User.objects.get(username=username)
    user_posts = user.author.all().order_by('-posted')
    user_posts2 = []
    for post in user_posts:
        post.is_liked_by_user = post.liked_by.filter(id=request.user.id).exists()
        print(post.is_liked_by_user)
        user_posts2.append(post)

    # Buttons Follow - Unfollow
    if request.method == "POST":
        to_do = request.POST.get('to_do')
        user_me = User.objects.get(id=request.user.id)
        if to_do == 'follow':
            # Add auth_user to profile_user followers
            user.followers.add(user_me)
            user.save()
            # Add profile_user to auth_user following
            user_me.following.add(user)
            user_me.save()
        elif to_do == 'unfollow':
            # Remove profile_user from auth_user following
            user_me.following.remove(user)
            user_me.save()
            # Remove auth_user from profile_user followers
            user.followers.remove(user_me)
            user.save()

    followers, following = user.followers.count(), user.following.count()

    page_obj = paginator_func(queryset=user_posts2, page=request.GET.get('page'))

    context = {"user_posts": page_obj,
               "profile_user": username,
               'follows': [followers, following]}

    if username != str(request.user):
        profile_user_followed = user.followers.filter(id=request.user.id).exists()
        context.update({"profile_user_followed": profile_user_followed})

    return HttpResponse(profile_template.render(context, request))


@login_required()
def following(request):
    following_template = loader.get_template('network/following.html')
    user_me = User.objects.get(id=request.user.id)
    users_following = user_me.following.all()
    following_users_posts = Post.objects.filter(user__in=users_following).order_by("-posted") if users_following.exists() else None
    page_obj = following_users_posts
    following_users_posts2 = []

    if following_users_posts:
        for post in following_users_posts:
            post.is_liked_by_user = post.liked_by.filter(id=request.user.id).exists()
            print(post.is_liked_by_user)
            following_users_posts2.append(post)

        page_obj = paginator_func(queryset=following_users_posts, page=request.GET.get('page'))

    context = {"following_users_posts": page_obj}

    return HttpResponse(following_template.render(context, request))


@csrf_exempt
@login_required()
def like(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)

    post_id = data.get('post_id')
    todo = data.get('to_do')
    print(post_id, todo)
    user = User.objects.get(id=request.user.id)
    post = Post.objects.get(id=post_id)

    if todo == "like":
        print('here1')
        post.liked_by.add(user)
    elif todo == "dislike":
        print('here2')
        post.liked_by.remove(user)
    else:
        return JsonResponse({"error": "HACKER! YOU SHALL NOOOT PAAAASSSSS!"}, status=400)
    post.save()

    return JsonResponse({"id": 100050500}, status=204)