import requests
import json
import re
from bs4 import BeautifulSoup


def CraigslistScraper(search_item, max_price_input):
    try:
        max_price = float(max_price_input)
    except ValueError:
        return {"error": "not a valid price"}

    base_url = 'https://chico.craigslist.org/search/sss'
    headers = {
        'User-Agent': 'PostmanRuntime/7.42.0',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    params = {'query': search_item}
    all_results = []
    seen_urls = set()
    page_number = 0
    max_pages = 10
    all_prices = []  #total amoun to get average

    while page_number < max_pages:
        offset = page_number * 120
        params.update({'s': offset})  #update the offset as we go

        response = requests.get(base_url, params=params, headers=headers)
        if response.status_code != 200:
            return {"error": "couldn't grab the page"}

        jsonTagStart = response.text.find('id="ld_searchpage_results"')
        jsonDataStart = response.text.find('>', jsonTagStart) + 1
        jsonDataEnd = response.text.find('</script>', jsonDataStart)
        jsonDataString = response.text[jsonDataStart:jsonDataEnd].strip()

        try:
            jsonData = json.loads(jsonDataString)
        except json.JSONDecodeError:
            return {"error": "couldn't parse jsonData"}

        listings = jsonData.get('itemListElement', [])
        if not listings:
            break

        for listingIndex, listing in enumerate(listings):
            try:
                item = listing.get('item', {})
                title = item.get('name', 'N/A')
                url_pattern = rf'<a href="([^"]+)"[^>]*>\s*<div class="title">{re.escape(title)}</div>'
                match = re.search(url_pattern, response.text, re.IGNORECASE)
                url = match.group(1) if match else 'N/A'

                if url == 'N/A' or url in seen_urls:
                    continue

                price = item.get('offers', {}).get('price', 'N/A')
                if price != 'N/A':
                    price = float(price)
                    if price <= max_price:  #only add prices under max
                        all_prices.append(price)
                else:
                    price = float('inf')  #skiiiip

                #skip anything over max
                if price > max_price:
                    continue

                location = item.get('offers', {}).get('availableAtOrFrom', {}).get('address', {}).get('addressLocality', 'no locality')
                images = item.get('image', [])
                imageUrl = images[0] if images else None

                all_results.append({
                    'id': f"craigslist_{page_number}_{listingIndex}",
                    'title': title,
                    'url': url,
                    'price': f"${price:.2f}" if price != float('inf') else 'N/A',
                    'location': location,
                    'image_url': imageUrl
                })
                seen_urls.add(url)
            except Exception:
                continue

        page_number += 1

    #average for CL
    avg_price = sum(all_prices) / len(all_prices) if all_prices else 0

    return {"listings": all_results, "average_price": avg_price}


def EbayScraper(keyword, zip_code, max_price_input):
    try:
        max_price = float(max_price_input)
    except ValueError:
        return {"error": "not a valid price"}

    listings = []
    all_prices = []  #total amount to get average
    base_url = f"https://www.ebay.com/sch/i.html?_from=R40&_stpos={zip_code}&_nkw={keyword}&_sacat=0&_fspt=1&rt=nc&LH_BIN=1&_sadis=25"

    for page in range(1, 5):
        url = f"{base_url}&_ipg=240&_pgn={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        for idx, item in enumerate(soup.select('.s-item')):
            if idx < 2:  #skip first 2 (always redundant)
                continue

            try:
                title = item.select_one('.s-item__title').get_text(strip=True) if item.select_one('.s-item__title') else 'no title'
                price_text = item.select_one('.s-item__price').get_text(strip=True) if item.select_one('.s-item__price') else 'N/A'

                #extract the price
                price_match = re.search(r"[\d.,]+", price_text)
                price = float(price_match.group().replace(',', '')) if price_match else None
                if price and price <= max_price:  #only add if the price is under max
                    all_prices.append(price)

                #skip listings over the max price
                if price and price > max_price:
                    continue

                link = item.select_one('.s-item__link')['href'] if item.select_one('.s-item__link') else 'no link'
                image_url = item.select_one('img')['src'] if item.select_one('img') else None

                listings.append({
                    'id': f"ebay_{page}_{idx}",
                    'title': title,
                    'price': f"${price:.2f}" if price else 'N/A',
                    'link': link,
                    'image_url': image_url
                })
            except Exception:
                continue

    #Crunch da numbers Ebay
    avg_price = sum(all_prices) / len(all_prices) if all_prices else 0

    return {"listings": listings, "average_price": avg_price}
