import requests
import json
import time
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Origin": "https://www.flyfrontier.com",
    "Referer": "https://www.flyfrontier.com/",
}

def get_all_routes():
    url = "https://booking.flyfrontier.com/Resource/GetMarkets"
    print("Fetching route data for validation...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        routes = {market['fromStation']: market['toStations'] for market in data.get('markets', [])}
        airport_names = {
            detail['stationCode']: detail.get('cityAndCode', detail['stationCode'])
            for detail in data.get('marketDetails', [])
        }
        print("Route data loaded successfully.")
        return routes, airport_names
    except requests.exceptions.RequestException as e:
        print(f"Error fetching route data: {e}")
        return None, None
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the route data response.")
        return None, None

def check_gowild_on_date(origin, destination, check_date):
    api_url = "https://booking.flyfrontier.com/Flight/RetrieveSchedule"
    params = {
        "calendarSelectableDays.Origin": origin,
        "calendarSelectableDays.Destination": destination,
    }

    try:
        response = requests.get(api_url, headers=HEADERS, params=params, timeout=20)
        response.raise_for_status()
        data = response.json().get("calendarSelectableDays", {})
        if not data:
            return False
        date_to_check_str = check_date.strftime("%#m/%#d/%Y").replace('/0','/')
        disabled_dates = set(data.get("disabledDates", []))
        if date_to_check_str in disabled_dates:
            return False
        last_available_date_str = data.get("lastAvailableDate", "").split(" ")[0]
        if last_available_date_str:
            last_available_date = datetime.strptime(last_available_date_str, '%Y-%m-%d')
            if check_date > last_available_date:
                return False
        return True
    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError, AttributeError):
        return False

def main():
    routes, airport_names = get_all_routes()
    if not routes:
        return
    origin_code = input("Enter your origin airport code (e.g., JFK): ").upper().strip()
    if origin_code not in airport_names or origin_code not in routes:
        print(f"Error: Origin airport '{origin_code}' is not a valid Frontier origin.")
        return
    while True:
        date_str = input(f"Enter the date you want to fly from {origin_code} (YYYY-MM-DD): ").strip()
        try:
            check_date = datetime.strptime(date_str, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            
    origin_name = airport_names.get(origin_code, origin_code)
    destinations_to_check = routes.get(origin_code, [])
    if not destinations_to_check:
        print(f"No direct flights found from {origin_name} in the route map.")
        return
    print("-" * 50)
    print(f"Searching for all available GoWild! destinations from {origin_name} on {date_str}...")
    available_destinations = []
    total_routes = len(destinations_to_check)
    for i, dest_code in enumerate(destinations_to_check):
        print(f"  ({i + 1}/{total_routes}) Checking route: {origin_code} -> {dest_code}...")
        is_available = check_gowild_on_date(origin_code, dest_code, check_date)
        if is_available:
            dest_name = airport_names.get(dest_code, dest_code)
            available_destinations.append(dest_name)
        time.sleep(0.3)
    print("-" * 50)
    if available_destinations:
        print(f"\n✅ Success! Found {len(available_destinations)} GoWild! destination(s) from {origin_name} on {date_str}:")
        for name in sorted(available_destinations):
            print(f"  - {name}")
    else:
        print(f"\n❌ No available GoWild! flights found from {origin_name} on {date_str}.")

if __name__ == "__main__":
    main()