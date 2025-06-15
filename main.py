import requests
import json
import re
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# List of realistic user agents to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
]

def test_proxy_connection():
    """
    Test the proxy connection using Selenium with detection prevention.
    
    Returns:
        bool: True if proxy is working, False otherwise.
    """
    print("Testing proxy connection with Selenium...")
    
    # Configure Chrome options for stealth mode
    options = Options()
    options.add_argument("--headless")  # Run in background for testing
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Add proxy configuration with IP authentication
    options.add_argument("--proxy-server=http://p.webshare.io:9999")
    
    # Add realistic user agent
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"--user-agent={user_agent}")
    
    driver = None
    try:
        # Initialize the webdriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Apply stealth settings
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        
        # Test proxy by visiting httpbin.org
        driver.get('http://httpbin.org/ip')
        
        # Wait for the page to load and extract IP
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "pre"))
        )
        
        ip_element = driver.find_element(By.TAG_NAME, "pre")
        ip_data = json.loads(ip_element.text)
        print(f"✓ Proxy working! Your IP through proxy: {ip_data['origin']}")
        return True
        
    except Exception as e:
        print(f"✗ Proxy test failed with error: {e}")
        return False
    finally:
        if driver:
            driver.quit()

def search_frontier_flights(origin, destination, date_str, use_proxy=False):
    """
    Scrapes Frontier's website using Selenium with stealth mode and detection prevention.

    Args:
        origin (str): The 3-letter IATA code for the origin airport (e.g., 'JFK').
        destination (str): The 3-letter IATA code for the destination airport (e.g., 'ATL').
        date_str (str): The departure date in 'YYYY-MM-DD' format.
        use_proxy (bool): Whether to use the proxy server (default: True).

    Returns:
        A list of fare dictionaries, or None if the request/parsing fails.
    """
    print(f"Searching for flights from {origin} to {destination} on {date_str}...\n")

    # Configure Chrome options for stealth mode
    options = Options()
    # Don't use headless mode to avoid detection
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Configure proxy if enabled
    if use_proxy:
        # Use proxy with IP authentication
        options.add_argument("--proxy-server=http://p.webshare.io:9999")
        print(f"Using proxy: p.webshare.io:9999 (IP authentication)")
    else:
        print("Using direct connection (no proxy)")
    
    # Add realistic user agent
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"--user-agent={user_agent}")
    
    # Additional stealth options
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-hang-monitor")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-prompt-on-repost")
    options.add_argument("--disable-sync")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--no-first-run")
    options.add_argument("--safebrowsing-disable-auto-update")

    driver = None
    try:
        # Initialize the webdriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Apply stealth settings
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        
        # Convert date string 'YYYY-MM-DD' to 'Mon DD, YYYY' format
        try:
            dt_object = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = dt_object.strftime('%b %d, %Y')  # e.g., 'Jun 16, 2025'
        except ValueError:
            print(f"Error: Invalid date format. Please use YYYY-MM-DD.")
            return None

        # Step 1: Visit Frontier homepage first to establish session
        print("Step 1: Visiting Frontier homepage to establish session...")
        driver.get("https://www.flyfrontier.com/")
        
        # Wait for page to load and add human-like delay
        time.sleep(random.uniform(3.0, 6.0))
        
        # Simulate some human behavior - scroll a bit
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(random.uniform(1.0, 2.0))
        
        # Step 2: Navigate to the flight search page with parameters
        params_internal = {
            'o1': origin,
            'd1': destination,
            'dd1': formatted_date,
            'ADT': 1,
            'mon': 'true',
            'promo': '',
            'ftype': 'DD'  # DD for Discount Den, use 'STD' for Standard
        }
        internal_select_url = f"https://booking.flyfrontier.com/Flight/InternalSelect?{urlencode(params_internal)}"
        
        print(f"Step 2: Navigating to search URL...")
        driver.get(internal_select_url)
        
        # Wait for potential redirects and page loading
        time.sleep(random.uniform(4.0, 7.0))
        
        # Step 3: Navigate to the Select page
        print("Step 3: Loading flight results...")
        select_url = "https://booking.flyfrontier.com/Flight/Select"
        driver.get(select_url)
        
        # Wait for the page to fully load
        time.sleep(random.uniform(5.0, 8.0))
        
        # Add some human-like scrolling while waiting for data to load
        for _ in range(3):
            scroll_amount = random.randint(200, 400)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(1.0, 2.0))
        
        # Step 4: Extract flight data from the page
        print("Step 4: Extracting flight data...")
        page_source = driver.page_source
        
        # Look for the flight data script
        soup = BeautifulSoup(page_source, 'html.parser')
        data_script = soup.find('script', text=re.compile(r'var\s+model\s*=\s*'))
        
        if not data_script:
            # Check for specific error messages
            if "no direct flights are available" in page_source.lower():
                print(f"\nNo flights found for this route on {date_str}.")
                return None
            elif "captcha" in page_source.lower() or "security check" in page_source.lower():
                print("\n⚠️  CAPTCHA or security check detected!")
                print("The browser window should be visible. Please solve any CAPTCHA if present.")
                input("Press Enter after solving any CAPTCHA to continue...")
                
                # Try to extract data again after CAPTCHA resolution
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                data_script = soup.find('script', text=re.compile(r'var\s+model\s*=\s*'))
                
                if not data_script:
                    print("Still couldn't find flight data after CAPTCHA resolution.")
                    return None
            else:
                print("\nError: Could not find the flight data script in the HTML response.")
                # Save the page source for debugging
                with open('debug_page_source.html', 'w') as f:
                    f.write(page_source)
                print("Page source saved to debug_page_source.html for analysis.")
                return None

        # Step 5: Extract and parse the JSON data
        match = re.search(r'var\s+model\s*=\s*(\{.*?\});', data_script.string, re.DOTALL)
        if not match:
            print("Error: Could not extract the JSON data from the script tag.")
            return None

        json_data_str = match.group(1)
        flight_data = json.loads(json_data_str)
        
        # Step 6: Navigate the dictionary to get the fare cells
        journeys = flight_data.get('journey', {})
        if not journeys.get('isSuccess', False):
            error_message = journeys.get('message', 'No flights found on this date.')
            print(f"\nFrontier reported an issue: {error_message}")
            return None
            
        fare_tensor = journeys.get('fareTensor', {})
        fare_cells = fare_tensor.get('cells', [])
        
        print(f"Successfully extracted {len(fare_cells)} fare options.")
        return fare_cells

    except Exception as e:
        error_msg = str(e)
        if use_proxy and ("proxy" in error_msg.lower() or "connection" in error_msg.lower()):
            print(f"Proxy-related error occurred: {e}")
            print("You may want to:")
            print("1. Check if your proxy credentials are correct")
            print("2. Try running without proxy by setting use_proxy=False")
        else:
            print(f"An error occurred during the browser operation: {e}")
        return None
    finally:
        if driver:
            # Keep browser open for a moment in case user needs to see something
            print("Closing browser in 3 seconds...")
            time.sleep(3)
            driver.quit()

def create_proxy_auth_extension():
    """
    Create a Chrome extension for proxy authentication.
    This works around Chrome's limitation with inline proxy auth.
    """
    import zipfile
    import os
    import tempfile
    
    # Create manifest for proxy auth extension
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    
    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "p.webshare.io",
                port: parseInt("9999")
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    // No authentication needed for IP-based authentication
    """
    
    # Create temp directory for extension
    temp_dir = tempfile.mkdtemp()
    extension_path = os.path.join(temp_dir, "proxy_auth_extension.zip")
    
    with zipfile.ZipFile(extension_path, 'w') as zf:
        zf.writestr("manifest.json", manifest_json)
        zf.writestr("background.js", background_js)
    
    return extension_path

if __name__ == '__main__':
    # Test proxy connection first
    print("=== Proxy Connection Test ===")
    proxy_working = test_proxy_connection()
    print()
    
    if not proxy_working:
        print("⚠️  Proxy test failed. You can:")
        print("1. Continue with proxy anyway (might work for actual scraping)")
        print("2. Continue without proxy")
        print("3. Exit and check your IP authentication with webshare.io")
        
        choice = input("\nEnter your choice (1/2/3): ").strip()
        if choice == '2':
            use_proxy = False
            print("Continuing without proxy...")
        elif choice == '3':
            print("Exiting. Please check your IP whitelist with webshare.io")
            exit()
        else:
            use_proxy = True
            print("Continuing with proxy anyway...")
    else:
        use_proxy = True
    
    print("\n=== Flight Search ===")
    origin_airport = "JFK"
    destination_airport = "ATL"
    # Updated to use a current date for testing
    departure_date = "2025-07-15" 

    # all_fares = search_frontier_flights(origin_airport, destination_airport, departure_date, use_proxy=use_proxy)
    all_fares = search_frontier_flights(origin_airport, destination_airport, departure_date, True)


    if all_fares:
        print("\n--- Available Fares ---")
        for fare in all_fares:
            price = fare.get('priceSpecification', {}).get('totalPrice')
            fare_type = fare.get('fareClassInput', 'N/A')
            fare_brand = fare.get('brandedFareClass', 'N/A')
            is_sold_out = fare.get('isSoldOut', False)

            if is_sold_out:
                print(f"- {fare_brand} ({fare_type}): SOLD OUT")
            elif price is not None:
                print(f"- {fare_brand} ({fare_type}): ${price:.2f}")
    else:
        print("\nCould not retrieve flight information.")