from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException

searchItem = input("What item do you want to search for?: ")
max_price_input = input("What is your maximum price?: ")

#typecast max price for comparison
try:
    max_price = float(max_price_input)
except ValueError:
    print("Invalid price entered. Please enter a numeric value.")
    exit()

#edgedriver path
driverPath = r'C:\Users\riley\Desktop\CAPSTONE\msedgedriver.exe'

#edge options (might do headless later)
edgeOptions = Options()

#load path
service = Service(driverPath)

#configure the driver
driver = webdriver.Edge(service=service, options=edgeOptions)

# raigslist url
driver.get('https://chico.craigslist.org/')

print("Website title:", driver.title)

#go to search bar
search_input = driver.find_element(By.CSS_SELECTOR, 'div.cl-search-dropdown input')

#type the user's input
search_input.send_keys(searchItem)

#enter
search_input.send_keys(Keys.RETURN)

#wait for it to load and div.gallery-card is the html element for istings
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.gallery-card'))
)


#function to extract listings
def extract_listings():
    results = []
    try:
        listings = driver.find_elements(By.CSS_SELECTOR, 'div.gallery-card')

        if not listings:
            print("No listings found or unable to locate listing elements.")
        else:
            print(f"Found {len(listings)} listings on the page.")

        for listing in listings:
            try:
                #title
                title_element = listing.find_element(By.CSS_SELECTOR, 'a.cl-app-anchor')
                title = title_element.text
                
                #url
                url = title_element.get_attribute('href')
                
                #price
                price_element = listing.find_element(By.CSS_SELECTOR, 'span.priceinfo')
                price_text = price_element.text if price_element else 'N/A'
                
                #typecast to flot
                price = float(price_text.replace('$', '').replace(',', '')) if price_text != 'N/A' else float('inf')
                
                #location
                location_element = listing.find_element(By.CSS_SELECTOR, 'div.meta')
                location = location_element.text.split('·')[1].strip() if '·' in location_element.text else 'N/A'
                
                #use maxprice for comparison
                if price <= max_price:
                    listing_info = f'Title: {title}\nURL: {url}\nPrice: {price_text}\nLocation: {location}\n{"-"*40}'
                    results.append(listing_info)
                else:
                    print(f'Skipping {title}, as its price ${price_text} exceeds your maximum price of ${max_price}.')
                
            except NoSuchElementException as e:
                print(f'Element was not in the listing: {e}')
            except Exception as e:
                print(f'Couldn\'t get listing data: {e}')
    
    except Exception as e:
        print(f'Failed: {e}')

    return results

#loop thru all pages
all_results = []
page_number = 1

while True:
    print(f"Scraping page {page_number}...")

    #add results from cur page
    all_results.extend(extract_listings())
    
    try:
        #try to grab next page
        next_button = driver.find_element(By.CSS_SELECTOR, 'button.bd-button.cl-next-page')

        #check if next page is clickable
        if not next_button.is_enabled() or 'disabled' in next_button.get_attribute('class'):
            print("No more pages to scrape or the next page button is not clickable.")
            break
        
        #click the next page
        next_button.click()
        
        #IMPORTANT wait 10ms so it has time to scrape all listings
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.gallery-card'))
        )
        
        page_number += 1
    #slenium and respective error flags
    except NoSuchElementException:
        print("No next page button found.")
        break
    except TimeoutException:
        print("Timed out waiting for next page.")
        break
    except ElementNotInteractableException:
        print("Last page reached.")
        break

print("\nListings found:\n")
for result in all_results:
    print(result)

print(f"\nThere are {len(all_results)} results.")

# close browser
driver.quit()
