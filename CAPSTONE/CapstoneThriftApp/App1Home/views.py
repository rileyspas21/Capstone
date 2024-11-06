from django.shortcuts import render
from .forms import CraigslistSearchForm
from .utils import CraigslistScraper, fetch_ebay_listings

def homepage(request):
    form = CraigslistSearchForm()
    craigslist_results = None
    ebay_results = None

    if request.method == 'POST':
        form = CraigslistSearchForm(request.POST)
        if form.is_valid():
            search_item = form.cleaned_data['search_item']
            max_price = form.cleaned_data['max_price']

            craigslist_results = CraigslistScraper(search_item, max_price)

            zip_code = "95926"#CHICO
            ebay_results = fetch_ebay_listings(search_item, zip_code)

    context = {
        'form': form,
        'craigslist_results': craigslist_results,
        'ebay_results': ebay_results,
    }
    return render(request, 'homepage.html', context)
