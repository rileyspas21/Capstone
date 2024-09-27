from django.shortcuts import render
from .forms import CraigslistSearchForm
from .utils import CraigslistScraper 

def homepage(request):
    form = CraigslistSearchForm()
    results = None

    if request.method == 'POST':
        form = CraigslistSearchForm(request.POST)
        if form.is_valid():
            search_item = form.cleaned_data['search_item']
            max_price = form.cleaned_data['max_price']
            results = CraigslistScraper(search_item, max_price) #might save the results to the database here (after testing)


    context = {
        'form': form,
        'results': results
    }
    return render(request, 'homepage.html', context)
