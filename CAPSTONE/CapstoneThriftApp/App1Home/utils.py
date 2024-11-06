import requests
import json
import re
from bs4 import BeautifulSoup

def CraigslistScraper(search_item, max_price_input):
    #typecast user input for maximum price
    try:
        max_price = float(max_price_input)
    except ValueError:
        return {"error": "not a valid price"}  #ERROR

    base_url = 'https://chico.craigslist.org/search/sss' #craigslist 
    headers = {
        'User-Agent': 'PostmanRuntime/7.42.0', #postman header
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    params = {'query': search_item}
    all_results = []
    seen_urls = set()  #store ALL URLs that get scraped
    page_number = 0
    max_pages = 10  #set a maximum page limit (in case of infinite)

    while page_number < max_pages:
        offset = page_number * 120 
        params.update({'s': offset}) #need this to input the offset for the GET request

        response = requests.get(base_url, params=params, headers=headers) #GET
        if response.status_code != 200:
            return {"error": "couldn't grab the page"}  #ERROR

        #for parsing the json
        jsonTagStart = response.text.find('id="ld_searchpage_results"') #the element in response
        jsonDataStart = response.text.find('>', jsonTagStart) + 1
        jsonDataEnd = response.text.find('</script>', jsonDataStart)
        jsonDataString = response.text[jsonDataStart:jsonDataEnd].strip()

        try:
            jsonData = json.loads(jsonDataString)
        except json.JSONDecodeError:
            return {"error": "couldn't parse jsonData"} #ERROR

        listings = jsonData.get('itemListElement', [])
        if not listings:  #no listings found so stop now
            break

        for listing in listings:
            try:
                item = listing.get('item', {})
                title = item.get('name', 'N/A')

                #print("processing title: {title}") #cur item

                #search for the URL in the HTML using the item title
                url_pattern = rf'<a href="([^"]+)"[^>]*>\s*<div class="title">{re.escape(title)}</div>' #This is a way to search for the url by searching for a <a> tag
                match = re.search(url_pattern, response.text, re.IGNORECASE)
                url = match.group(1) if match else 'N/A'  # Get the URL from the match

                #print("found URL: {url}")

                #skip if no URLor if its been seen already
                if url == 'N/A' or url in seen_urls:
                    continue

                price = item.get('offers', {}).get('price', 'N/A')
                if price != 'N/A':
                    price = float(price)
                else:
                    price = float('N/A')  #set as N/A if the price is not listed

                location = item.get('offers', {}).get('availableAtOrFrom', {}).get('address', {}).get('addressLocality', 'N/A')

                #get image URL
                images = item.get('image', [])
                imageUrl = images[0] if images else None

                if price <= max_price:
                    #add listing to results and mark as seen
                    all_results.append({
                        'title': title,
                        'url': url,
                        'price': f"${price:.2f}",
                        'location': location,
                        'image_url': imageUrl
                    })
                    seen_urls.add(url)  #marked as seen
            except Exception as e:
                print("Error processing listing: {e}")  #ERROR
                continue  #edgecase catcher

        page_number += 1 

    return all_results

def fetch_ebay_listings(keyword, zip_code):
    listings = []
    base_url = f"https://www.ebay.com/sch/i.html?_from=R40&_stpos={zip_code}&_nkw={keyword}&_sacat=0&_fspt=1&rt=nc&LH_BIN=1&_sadis=50"

    for page in range(1, 5):
        url = f"{base_url}&_ipg=240&_pgn={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        #loop but skip first 2 items (blank ebay defaults)
        for idx, item in enumerate(soup.select('.s-item')):
            # Skip the first two items
            if idx < 2:
                continue

            title = item.select_one('.s-item__title').get_text(strip=True) if item.select_one('.s-item__title') else 'N/A'
            price = item.select_one('.s-item__price').get_text(strip=True) if item.select_one('.s-item__price') else 'N/A'
            link = item.select_one('.s-item__link')['href'] if item.select_one('.s-item__link') else 'N/A'

            #TEST
            image_url = item.select_one('img')['src'] if item.select_one('img') else 'N/A'

            listings.append({
                'title': title,
                'price': price,
                'link': link,
                'image_url': image_url
            })
    
    return listings

