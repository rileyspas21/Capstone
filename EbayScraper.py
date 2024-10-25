import requests
from bs4 import BeautifulSoup

def fetch_ebay_listings(keyword, zip_code):
    listings = []
    base_url = f"https://www.ebay.com/sch/i.html?_from=R40&_stpos={zip_code}&_nkw={keyword}&_sacat=0&_fspt=1&rt=nc&LH_BIN=1&_sadis=100"

    for page in range(1, 5):  #new approach jsut doing first 5 because Ebay has WAYYYYY more listings (might reduce mile radius around zipcode to reduce #)
        url = f"{base_url}&_ipg=240&_pgn={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        #grab info from ebay's HTML structure
        for item in soup.select('.s-item'):
            title = item.select_one('.s-item__title').get_text(strip=True) if item.select_one('.s-item__title') else 'N/A'
            price = item.select_one('.s-item__price').get_text(strip=True) if item.select_one('.s-item__price') else 'N/A'
            link = item.select_one('.s-item__link')['href'] if item.select_one('.s-item__link') else 'N/A'
            image_url = item.select_one('.s-item__image-img')['src'] if item.select_one('.s-item__image-img') else 'N/A'

            listings.append({#add to list
                'title': title,
                'price': price,
                'link': link,
                'image_url': image_url
            })

    return listings

#TEST
zip_code = '95926'
keyword = 'adidas'
ebay_listings = fetch_ebay_listings(keyword, zip_code)

for listing in ebay_listings:
    print(listing)
