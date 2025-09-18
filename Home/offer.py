import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import sys

def setup_driver():
    """Setup and configure the Chrome WebDriver with appropriate options."""
    try:
        print("Setting up Chrome WebDriver...")
        options = webdriver.ChromeOptions()
        
        # Comment out headless mode for debugging
        # options.add_argument('--headless')
        
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver_manager to handle driver installation
        print("Installing ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        print("Chrome WebDriver setup complete")
        return driver
    except Exception as e:
        print(f"Error setting up driver: {e}")
        print("Please make sure Chrome browser is installed and up to date")
        sys.exit(1)

def fetch_valid_image_src(element):
    """Try to fetch the correct image source from various attributes."""
    try:
        # First try to find img tag
        img = element.find_element(By.TAG_NAME, 'img')
        
        # Try different attributes in order of preference
        for attr in ['src', 'data-src', 'data-original']:
            img_src = img.get_attribute(attr)
            if img_src and not img_src.endswith('mdefault.png'):
                return img_src
        
        # If no valid image found in img tag, try background-image
        style = element.get_attribute('style')
        if style and 'background-image' in style:
            return style.split('url("')[1].split('")')[0]
            
        return None

    except Exception as e:
        print(f"Error fetching image source: {e}")
        return None

def extract_product_info(element):
    """Extract product information from an element."""
    try:
        product_data = {}
        
        # Get product link
        try:
            link_elem = element.find_element(By.TAG_NAME, 'a')
            product_data['Product Link'] = link_elem.get_attribute('href')
        except NoSuchElementException:
            product_data['Product Link'] = None

        # Get product name/title
        try:
            name_elem = element.find_element(By.CSS_SELECTOR, '.product-title, .product-name, h3, h4')
            product_data['Product Name'] = name_elem.text.strip()
        except NoSuchElementException:
            product_data['Product Name'] = None

        # Get price
        try:
            price_elem = element.find_element(By.CSS_SELECTOR, '.price, .product-price, [class*="price"]')
            product_data['Price'] = price_elem.text.strip()
        except NoSuchElementException:
            product_data['Price'] = None

        # Get image
        product_data['Image Source'] = fetch_valid_image_src(element)

        # Get any discount or offer text
        try:
            offer_elem = element.find_element(By.CSS_SELECTOR, '.discount, .offer, [class*="discount"], [class*="offer"]')
            product_data['Offer'] = offer_elem.text.strip()
        except NoSuchElementException:
            product_data['Offer'] = None

        return product_data

    except Exception as e:
        print(f"Error extracting product info: {e}")
        return None

def scrape_products(driver, url):
    """Scrape product information from the given URL."""
    print(f"Accessing URL: {url}")
    driver.get(url)
    products_data = []
    unique_links = set()

    try:
        # Wait for products to load (adjust selector based on website structure)
        print("Waiting for products to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.product-card, .product-item, [class*="product"]'))
        )
        
        # Scroll to load all products
        print("Scrolling to load all products...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 5  # Limit scrolling attempts to prevent infinite loops
        
        while scroll_attempts < max_scroll_attempts:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for content to load
            
            # Calculate new scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_attempts += 1

        # Find all product elements
        print("Finding product elements...")
        product_elements = driver.find_elements(By.CSS_SELECTOR, '.product-card, .product-item, [class*="product"]')
        print(f"Found {len(product_elements)} product elements")
        
        for index, element in enumerate(product_elements, 1):
            try:
                print(f"Processing product {index}/{len(product_elements)}")
                product_info = extract_product_info(element)
                if product_info and product_info['Product Link'] and product_info['Product Link'] not in unique_links:
                    unique_links.add(product_info['Product Link'])
                    products_data.append(product_info)
                    print(f"Added product: {product_info.get('Product Name', 'Unknown')}")
            except StaleElementReferenceException:
                print(f"Stale element for product {index}, skipping...")
                continue
            except Exception as e:
                print(f"Error processing product {index}: {e}")
                continue

        return products_data

    except TimeoutException:
        print("Timeout waiting for products to load")
        return []
    except Exception as e:
        print(f"Error scraping products: {e}")
        return []

def extract_banner_info(banner):
    """Extract information from a banner element."""
    try:
        banner_data = {}
        
        # Get banner image
        try:
            img = banner.find_element(By.TAG_NAME, 'img')
            banner_data['Image Source'] = img.get_attribute('src')
            if not banner_data['Image Source'] or banner_data['Image Source'].endswith('mdefault.png'):
                banner_data['Image Source'] = img.get_attribute('data-src')
            banner_data['Alt Text'] = img.get_attribute('alt')
        except NoSuchElementException:
            banner_data['Image Source'] = None
            banner_data['Alt Text'] = None

        # Get banner link
        try:
            link = banner.find_element(By.TAG_NAME, 'a')
            banner_data['Link'] = link.get_attribute('href')
        except NoSuchElementException:
            banner_data['Link'] = None

        # Get banner text/description if available
        try:
            text_elem = banner.find_element(By.CSS_SELECTOR, '.banner-text, .banner-description, p, h2, h3')
            banner_data['Description'] = text_elem.text.strip()
        except NoSuchElementException:
            banner_data['Description'] = None

        return banner_data

    except Exception as e:
        print(f"Error extracting banner info: {e}")
        return None

def scrape_banners(driver, url):
    """Scrape banner information from the given URL."""
    print(f"Accessing URL: {url}")
    banners_data = []
    unique_links = set()

    try:
        # Navigate to the URL with error handling
        try:
            driver.get(url)
        except WebDriverException as e:
            print(f"Error accessing URL: {e}")
            print("Trying alternative URL...")
            # Try alternative URL if the first one fails
            alt_url = "https://www.reliancedigital.in/smartphones"
            print(f"Accessing alternative URL: {alt_url}")
            driver.get(alt_url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        time.sleep(10)  # Increased wait time
        
        # Try to find any banner-like elements
        print("Looking for banner elements...")
        
        # First try to find the main banner container
        banner_containers = [
            '.banner-container',
            '.carousel-container',
            '.slider-container',
            '.swiper-container',
            '.hero-section',
            '.main-banner-section'
        ]
        
        banner_found = False
        for container in banner_containers:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, container))
                )
                print(f"Found banner container: {container}")
                banner_found = True
                break
            except TimeoutException:
                continue
        
        if not banner_found:
            print("No banner container found, trying direct banner selectors...")
        
        # Find all banner elements
        banner_selectors = [
            '.banner',
            '.carousel-item',
            '.slick-slide',
            '[class*="banner"]',
            '[class*="carousel"]',
            '.hero-banner',
            '.main-banner',
            '.slider-item',
            '.swiper-slide',
            '.product-banner',
            '.category-banner'
        ]

        for selector in banner_selectors:
            try:
                print(f"Trying selector: {selector}")
                banners = driver.find_elements(By.CSS_SELECTOR, selector)
                if banners:
                    print(f"Found {len(banners)} banners with selector: {selector}")
                    for banner in banners:
                        try:
                            banner_info = extract_banner_info(banner)
                            if banner_info and banner_info.get('Link') and banner_info['Link'] not in unique_links:
                                unique_links.add(banner_info['Link'])
                                banners_data.append(banner_info)
                                print(f"Added banner: {banner_info.get('Description', 'Unknown')}")
                        except StaleElementReferenceException:
                            print("Stale element reference, skipping...")
                            continue
                        except Exception as e:
                            print(f"Error processing banner: {e}")
                            continue
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        # If no banners found, try to find any images that might be banners
        if not banners_data:
            print("No banners found with standard selectors, trying to find any large images...")
            try:
                images = driver.find_elements(By.TAG_NAME, 'img')
                for img in images:
                    try:
                        # Check if image is large enough to be a banner
                        width = img.get_attribute('width')
                        height = img.get_attribute('height')
                        if width and height and int(width) > 300 and int(height) > 100:
                            banner_info = {
                                'Image Source': img.get_attribute('src'),
                                'Alt Text': img.get_attribute('alt'),
                                'Link': None,
                                'Description': None
                            }
                            if banner_info['Image Source'] and banner_info['Image Source'] not in unique_links:
                                unique_links.add(banner_info['Image Source'])
                                banners_data.append(banner_info)
                                print(f"Added image as banner: {banner_info['Alt Text']}")
                    except Exception as e:
                        print(f"Error processing image: {e}")
                        continue
            except Exception as e:
                print(f"Error finding images: {e}")

        return banners_data

    except TimeoutException:
        print("Timeout waiting for banners to load")
        return []
    except Exception as e:
        print(f"Error scraping banners: {e}")
        return []

def save_to_json(data, filename):
    """Save data to JSON file with proper error handling."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        # Save the data
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        
        print(f"Data successfully saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to JSON file: {e}")
        return False

def main():
    # URL to scrape - only phones/mobiles page
    url = "https://www.reliancedigital.in/smartphones/c/S101711"
    output_file = "phone_banners.json"
    
    print("Starting the scraping process...")
    driver = None
    
    try:
        driver = setup_driver()
        print(f"\nScraping banners from phones page: {url}")
        banners = scrape_banners(driver, url)
        
        if banners:
            print(f"\nTotal banners found: {len(banners)}")
            if save_to_json(banners, output_file):
                print(f"Data saved to {output_file}")
            else:
                print("Failed to save data to JSON file")
        else:
            print("No banners were scraped from the phones page")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
    
    finally:
        if driver:
            print("Closing the browser...")
            try:
driver.quit()
                print("Browser closed")
            except Exception as e:
                print(f"Error closing browser: {e}")

if __name__ == "__main__":
    main()
