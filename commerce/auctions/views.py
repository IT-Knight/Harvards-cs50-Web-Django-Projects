from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.views.generic import View, TemplateView
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .models import Auction, User, Comment, Bid, Watchlist, Categories

# Create your views here.

# Option 1
# def index(request):
#     index_template = loader.render_to_string("auctions/index.html",
#                                              context={'listings': Auction.objects.all()})
#     return HttpResponse(index_template)

# Option 2
def index(request):
    index_template = loader.get_template("auctions/index.html")
    context = {'listings': Auction.objects.filter(closed=False)}
    return HttpResponse(index_template.render(context, request))

# Option 3
# class IndexTemplateView(TemplateView):
#     template_name = "auctions/index.html"
#
#     def get_context_data(self, **kwargs):
#         return {'listings': Auction.objects.all()}


def login_view(request):
    if request.method == "GET":
        return render(request, "auctions/login.html")

    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:  # is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid credentials."
            })


def logout_view(request):
    logout(request)
    return redirect('index')


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect('index')
    else:
        return render(request, "auctions/register.html")


class CreateListing(View):

    def get(self, request):
        create_listing_template = loader.get_template("auctions/create_listing.html")
        category_list = Categories.objects.all()
        context = {"categories": category_list}
        return HttpResponse(create_listing_template.render(context, request))

    def post(self, request):
        name = request.POST["name"]
        d11n = request.POST["description"]
        price: float = float(request.POST["price"])
        expire_date = datetime.strptime(request.POST["expire_date"].replace("T", " "), "%Y-%m-%d %H:%M")
        image_url = request.POST["image_url"]
        category, new_category = request.POST.get("category"), request.POST.get("new_category")

        if new_category:
            category = Categories(name=new_category.lower())
            category.save()
        elif category:
            category = Categories.objects.get(name=category)

        new_listing = Auction.objects.create(author=User.objects.get(pk=request.user.id),
                                             title=name,
                                             desc=d11n,
                                             price=price,
                                             expires=expire_date,
                                             image=image_url,
                                             category=category)
        new_listing.save()

        if category or new_category:
            category.listing.add(new_listing)
            category.save()

        return redirect('index')


class Listing(View):
    listing_template = loader.get_template('auctions/listing.html')

    @staticmethod
    def max_bid(request, list_id):
        if Bid.objects.filter(auction_id=list_id).exists():
            return Bid.objects.filter(auction_id=list_id).order_by('bid_amount').last()
        else:
            return None

    @staticmethod
    def in_watchlist_check(request, list_id):
        return Watchlist.objects.filter(user__id=request.user.id, listings__id=list_id).exists()

    @staticmethod
    def check_bid_type(bid: str):
        dots = bid.count(".")
        commas = bid.count(",")
        if dots > 1 or commas > 1:
            return False

        # check for not digit symbols
        test = "".join([sym for sym in bid if sym not in (".", ",")])
        if test.isdigit():
            return True
        else:
            return False

    def check_is_expired(self, request, list_id, current_listing):
        listing_expire_date = current_listing.expires
        now = timezone.now()
        if listing_expire_date < now:
            current_listing.expired = True
            current_listing.closed = True
            max_bid_obj = self.max_bid(request, list_id)
            if max_bid_obj:
                current_listing.winner = User.objects.get(pk=request.user.id)
            current_listing.save()
            return True
        else:
            return False

    def close_listing(self, request, list_id, current_listing):
        current_listing.closed = True
        max_bid = self.max_bid(request, list_id)
        if max_bid:
            winner = max_bid.participant.id
            current_listing.winner = User.objects.get(pk=winner)
        current_listing.save()
        return True

    def get(self, request, list_id):
        current_listing = get_object_or_404(Auction, id=list_id)
        # check if listing in watchlist
        in_watchlist = Watchlist.objects.filter(user__id=request.user.id, listings__id=list_id).exists()

        # check if listing is expired
        is_expired = self.check_is_expired(request, list_id, current_listing)

        # get Max bid if exists
        max_bid = self.max_bid(request, list_id)

        # get Listing Comments
        comments = current_listing.comments
        context = {"listing": current_listing,
                   "in_watchlist": in_watchlist,
                   "max_bid": max_bid,
                   "comments": comments}
        return HttpResponse(self.listing_template.render(context, request))

    def post(self, request, list_id):
        # basic context variables
        current_listing = get_object_or_404(Auction, id=list_id)
        is_expired = self.check_is_expired(request, list_id, current_listing)
        in_watchlist = self.in_watchlist_check(request, list_id)
        min_bid: float = float(current_listing.price)
        max_bid = self.max_bid(request, list_id)
        comments = current_listing.comments
        context = {"listing": current_listing,  # == Auction.objects.get(id=list_id)
                   "in_watchlist": in_watchlist,
                   "min_bid": min_bid,
                   "max_bid": max_bid,
                   "comments": comments}

        # process Comments
        comment = request.POST.get('comment')
        if comment:
            comment_obj = Comment(user_id=request.user.id, item_id=list_id, comment=comment)
            comment_obj.save()
            current_listing.comments.add(comment_obj)
            current_listing.save()
            context.update({"comments": Auction.objects.get(id=list_id).comments})


        # process Close by author
        request_close = request.POST.get("close")
        if request_close:
            is_closed = self.close_listing(request, list_id, current_listing)
            context.update({"closed": is_closed})  # True


        # process Bids
        request_new_bid = request.POST.get('new_bid')
        if request_new_bid:
            request_new_bid.replace(",", ".")
            context.update({"users_request_bid": request_new_bid})
            bid_type_is_valid = self.check_bid_type(request_new_bid)
            if not bid_type_is_valid:
                context.update({"error_message": "Invalid input format!"})
                return HttpResponse(self.listing_template.render(context, request))

            if max_bid:
                if float(request_new_bid) > float(max_bid.bid_amount):
                    Bid(participant_id=request.user.id, auction=current_listing, bid_amount=request_new_bid).save()
                    context["max_bid"] = self.max_bid(request, list_id)
                    context.pop("users_request_bid")
                else:
                    context.update({"error_message": "Bid must be greater then Max bid!"})

            elif float(request_new_bid) >= float(current_listing.price):
                Bid(participant_id=request.user.id, auction=current_listing, bid_amount=request_new_bid).save()
                context["max_bid"] = self.max_bid(request, list_id)
                context.pop("users_request_bid")
            else:
                context.update({"error_message": "Bid is lower then starting bid!"})

        # process Add-Delete Watchlists
        watchlist_request = request.POST.get('watchlist')
        if watchlist_request:
            current_user_object = User.objects.get(id=request.user.id)

            if watchlist_request == "delete":
                user_watchlist = Watchlist.objects.get(user__id=request.user.id)
                user_watchlist.listings.remove(current_listing)
                user_watchlist.save()
                context["in_watchlist"] = False

            if watchlist_request == "add":
                watchlist_object_exists = Watchlist.objects.filter(user__id=request.user.id).exists()
                if not watchlist_object_exists:
                    user_watchlist = Watchlist(user=current_user_object)
                    user_watchlist.save()
                else:
                    user_watchlist = Watchlist.objects.get(user__id=request.user.id)
                user_watchlist.listings.add(current_listing)
                user_watchlist.save()
                context["in_watchlist"] = True

        return HttpResponse(self.listing_template.render(context, request))


@login_required
def explore_my_listings(request):
    user_listings = Auction.objects.filter(author__id=request.user.id)
    return render(request, 'auctions/my_listings.html', {"user_listings": user_listings})


@login_required
def explore_watchlist(request):
    watchlist_object_exists = Watchlist.objects.filter(user__id=request.user.id).exists()
    if not watchlist_object_exists:
        current_user_object = User.objects.get(id=request.user.id)
        user_watchlist = Watchlist(user=current_user_object)
        user_watchlist.save()

    watchlist = Watchlist.objects.get(user__id=request.user.id)
    return render(request, 'auctions/watchlist.html', {"watchlist": watchlist})


def categories(request):
    categories_template = loader.get_template("auctions/categories.html")
    active_categories = Categories.objects.filter(listing__closed=False, listing__expired=False)
    unique_categories = set([x.name for x in active_categories])
    context = {"categories": unique_categories}
    return HttpResponse(categories_template.render(context, request))


def category(request, category):
    category_template = loader.get_template("auctions/category.html")
    category_obj = Categories.objects.get(name=category)
    active_listings = category_obj.listing.filter(closed=False, expired=False)
    context = {"category_name": category, "active_listings": active_listings}
    return HttpResponse(category_template.render(context, request))

