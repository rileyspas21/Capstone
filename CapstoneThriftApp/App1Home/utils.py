import requests
from bs4 import BeautifulSoup

def CraigslistScraper(search_item, max_price_input):
    #typecast user input
    try:
        max_price = float(max_price_input)
    except ValueError:
        return {"error": "Invalid maximum price"}  #error if price input is invalid

    base_url = 'https://chico.craigslist.org/search/sss'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    params = {'query': search_item}
    all_results = []
    seen_urls = set()  #store ALL urls that get scraped
    page_number = 0
    max_pages = 10  #set a max page limit

    while page_number < max_pages:
        offset = page_number * 120
        params.update({'s': offset})

        response = requests.get(base_url, params=params, headers=headers)
        if response.status_code != 200:
            return {"error": "Failed to retrieve the page."}  #error if page retrieval fails

        soup = BeautifulSoup(response.text, 'html.parser')
        listings = soup.find_all('li', class_='cl-static-search-result')  #craigslist listings html

        no_more_listings = False  #to track if new listings were found on the cur page

        for listing in listings:
            try:
                title_element = listing.find('div', class_='title')
                title = title_element.text.strip() if title_element else 'N/A'
                url_element = listing.find('a')
                url = url_element['href'] if url_element else 'N/A'

                if url in seen_urls:  #check for duplicates
                    no_more_listings = True
                    break  #break if duplicate

                price_element = listing.find('div', class_='price')
                price_text = price_element.text.strip() if price_element else 'N/A'
                price = float(price_text.replace('$', '').replace(',', '')) if price_text != 'N/A' else float('inf')

                location_element = listing.find('div', class_='location')
                location = location_element.text.strip() if location_element else 'N/A'

                image_element = listing.find('img')
                image_url = image_element['src'] if image_element else None  #get image url or N/A

                print(response.text)
                print(f'Scraped image URL: {image_url}')  #debugging print

                if price <= max_price:
                    all_results.append({
                        'title': title,
                        'url': url,
                        'price': price_text,
                        'location': location,
                        'image_url': image_url #troubleshooting8888888888888888888888888888888888888888888888888888888
                    })
                    seen_urls.add(url)  #add url to seen list
            except Exception as e:
                continue  #skip if it gets stuck

        if no_more_listings:
            break  #duplocate found we are rescraping so break

        page_number += 1

    return all_results  #return
