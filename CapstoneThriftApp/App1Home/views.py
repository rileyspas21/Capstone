from django.shortcuts import render, redirect
from .forms import CraigslistSearchForm, AuthForm
from .utils import CraigslistScraper, EbayScraper
from .models import UserItems, RecentSearch, PriceHistory
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from decimal import Decimal
import re
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib import messages


from django.db import IntegrityError

def homepage(request):
    #hit the user with a popup if they are not signed in
    if not request.user.is_authenticated:
        if request.method == 'POST' or request.GET.get('search_item'):
            messages.error(request, "You must be signed in to perform a search.")
            return redirect('login')

    form = CraigslistSearchForm()
    craigslist_results = None
    ebay_results = None
    recent_searches = []

    if request.user.is_authenticated:
        #get user's recent searches
        all_searches = RecentSearch.objects.filter(user=request.user).order_by('-timestamp')
        seen = set()
        recent_searches = []
        for search in all_searches:
            key = (search.search_item, search.max_price)
            if key not in seen:
                recent_searches.append(search)
                seen.add(key)

    search_item = request.GET.get('search_item')
    max_price = request.GET.get('max_price')

    if search_item and max_price:
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = None

        if max_price is not None:
            craigslist_data = CraigslistScraper(search_item, max_price)
            craigslist_results = craigslist_data.get("listings", [])
            avg_price_craigslist = craigslist_data.get("average_price", 0)

            ebay_data = EbayScraper(search_item, "95926", max_price)
            ebay_results = ebay_data.get("listings", [])
            avg_price_ebay = ebay_data.get("average_price", 0)

            #combine the avgs from both platforms
            all_prices = []
            if avg_price_craigslist:
                all_prices.append(avg_price_craigslist)
            if avg_price_ebay:
                all_prices.append(avg_price_ebay)

            if all_prices:
                avg_price = sum(all_prices) / len(all_prices)

                #check if there was already an entry today
                today = now().date()
                try:
                    #add entry to DB
                    price_history, created = PriceHistory.objects.get_or_create(
                        user=request.user,
                        search_item=search_item,
                        max_price=max_price,
                        timestamp=today,
                        defaults={"avg_price": avg_price},
                    )
                    if not created:
                        #update avg_price if record already exists
                        price_history.avg_price = avg_price
                        price_history.save()
                except IntegrityError:
                    pass  #to avoid duplicates

            #store results in session
            request.session['craigslist_results'] = craigslist_results
            request.session['ebay_results'] = ebay_results

            #fill form with the search params
            form = CraigslistSearchForm(initial={'search_item': search_item, 'max_price': max_price})

    elif request.method == 'POST' and 'search_item' in request.POST:
        form = CraigslistSearchForm(request.POST)
        if form.is_valid():
            search_item = form.cleaned_data['search_item']
            max_price = form.cleaned_data['max_price']

            #save user search
            if request.user.is_authenticated:
                RecentSearch.objects.create(
                    user=request.user,
                    search_item=search_item,
                    max_price=max_price
                )

            craigslist_data = CraigslistScraper(search_item, max_price)
            craigslist_results = craigslist_data.get("listings", [])
            avg_price_craigslist = craigslist_data.get("average_price", 0)

            ebay_data = EbayScraper(search_item, "95926", max_price)
            ebay_results = ebay_data.get("listings", [])
            avg_price_ebay = ebay_data.get("average_price", 0)

            #combine the avgs from both platforms
            all_prices = []
            if avg_price_craigslist:
                all_prices.append(avg_price_craigslist)
            if avg_price_ebay:
                all_prices.append(avg_price_ebay)

            if all_prices:
                avg_price = sum(all_prices) / len(all_prices)

                #check if there was already an entry today
                today = now().date()
                try:
                    #add entry to db
                    price_history, created = PriceHistory.objects.get_or_create(
                        user=request.user,
                        search_item=search_item,
                        max_price=max_price,
                        timestamp=today,
                        defaults={"avg_price": avg_price},
                    )
                    if not created:
                        #update avg_price if record already exists
                        price_history.avg_price = avg_price
                        price_history.save()
                except IntegrityError:
                    pass  #to avoid duplicates

            #store results in session
            request.session['craigslist_results'] = craigslist_results
            request.session['ebay_results'] = ebay_results

    context = {
        'form': form,
        'craigslist_results': craigslist_results,
        'ebay_results': ebay_results,
        'recent_searches': recent_searches,
        'search_item': search_item,
        'max_price': max_price,
    }
    return render(request, 'homepage.html', context)



@login_required
def saveListings(request):
    if request.method == 'POST' and 'selected_listings' in request.POST:
        selected_listings = request.POST.getlist('selected_listings')  #get all selected IDs

        craigslist_results = request.session.get('craigslist_results', [])
        ebay_results = request.session.get('ebay_results', [])

        for listing_id in selected_listings:
            #craigslist reults
            listing = next((item for item in craigslist_results if item['id'] == listing_id), None)
            if not listing:
                #ebay results
                listing = next((item for item in ebay_results if item['id'] == listing_id), None)

            if listing:
                #save listing to DB
                UserItems.objects.create(
                    user=request.user,
                    WantedItemName=listing['title'],
                    WantedItemPrice=Decimal(re.sub(r'[^\d.]', '', listing['price'])),  #strip '$'
                    WantedItemLocation=listing.get('location', 'N/A'),
                    WantedItemURL=listing.get('url') or listing.get('link'),
                    WantedItemImage=listing.get('image_url', '')
                )

    return redirect('savedListings')


@login_required
def savedListings(request):
    listings = UserItems.objects.filter(user=request.user)
    return render(request, 'savedListings.html', {'listings': listings})


@login_required
def removeListing(request, listing_id):
    if request.method == "POST":
        #get the user's listing and delete
        UserItems.objects.filter(user=request.user, id=listing_id).delete()
    return redirect('savedListings')


@login_required
def priceGraph(request, search_item, max_price):
    try:
        max_price = float(max_price)
    except ValueError:
        return JsonResponse({"error": "Invalid max_price format"}, status=400)

    history = PriceHistory.objects.filter(
        user=request.user,
        search_item=search_item,
        max_price=max_price
    ).order_by('timestamp')

    data = {
        'labels': [entry.timestamp.strftime('%Y-%m-%d') for entry in history],
        'prices': [float(entry.avg_price) for entry in history],
    }
    return JsonResponse(data)


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  #log in after registering
            return redirect('homepage')  #go straight to homepage
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def customLogin(request):
    if request.method == "POST":
        form = AuthForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  #LOGIN
                return redirect('homepage')
    else:
        form = AuthForm()
    
    return render(request, 'registration/login.html', {'form': form})
