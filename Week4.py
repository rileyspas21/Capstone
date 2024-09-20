import requests
from bs4 import BeautifulSoup

search_item = input("What item do you want to search for?: ")
max_price_input = input("What is your maximum price?: ")

#typecast user input
try:
    max_price = float(max_price_input)
except ValueError:
    print("wompity womp try again")
    exit()

base_url = 'https://chico.craigslist.org/search/sss'
headers = {#chat GPT said this might prevent me from getting blocked by anti-crawler but i dont think it does anything
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}




params = {'query': search_item}
all_results = []
seen_urls = set()  #store ALL urls that get scraped
page_number = 0
max_pages = 10  #set a max page (cna no longer go infinite)
#just have it run for 5 pages (there is never 5 pages worth of stuff anyway, but jsut in case)
while page_number < max_pages:
    offset = page_number * 120
    params.update({'s': offset})

    #print(f"Scraping page {page_number + 1}...")
    response = requests.get(base_url, params=params, headers=headers)
    #code 200 means LFG
    if response.status_code != 200:
        print("Failed to retrieve the page.")
        break

    soup = BeautifulSoup(response.text, 'html.parser')
    listings = soup.find_all('li', class_='cl-static-search-result') #listings html

    no_more_listings = False  #flag to track if new listings were found on the current page THIS SHIT DOESNT WORK

    for listing in listings: #the secret sauce
        try:
            title_element = listing.find('div', class_='title')
            title = title_element.text.strip() if title_element else 'N/A'
            url_element = listing.find('a')
            url = url_element['href'] if url_element else 'N/A'

            if url in seen_urls:  #check for dupe url
                print(f"Duplicate URL found: {url}. Stopping scraping.")
                no_more_listings = True  #break out of the listings loop (if there is aduplicate we are researching the same page oops)
                break  


            price_element = listing.find('div', class_='price')
            price_text = price_element.text.strip() if price_element else 'N/A'
            price = float(price_text.replace('$', '').replace(',', '')) if price_text != 'N/A' else float('inf')

            location_element = listing.find('div', class_='location')
            location = location_element.text.strip() if location_element else 'N/A'

            if price <= max_price:
                listing_info = f'Title: {title}\nURL: {url}\nPrice: {price_text}\nLocation: {location}\n{"-" * 40}'
                all_results.append(listing_info)
                seen_urls.add(url)  #add url to seen
            else:
                print(f'Skipping {title}, as its price ${price_text} exceeds your maximum price of ${max_price}.')

        except Exception as e:
            print(f"Couldn't get listing data: {e}")

    if no_more_listings:
        break  #exit the outer loop if we've found a seen url (we are rescraping a page)

    page_number += 1


print("\nListings found:\n")
for result in all_results:
    print(result)

print(f"\nThere are {len(all_results)} results.")
