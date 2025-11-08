import requests
import numpy as np
import time

API_KEY = "your apiiiiiiii"  # Replace with your own API key
BASE_URL = "https://csfloat.com/api/v1"

headers = {
    "Authorization": f"{API_KEY}",
    "Content-Type": "application/json"
}

def calculate_median(prices):
    return np.median(prices) if prices else 0

def calculate_standard_deviation(prices):
    return np.std(prices) if len(prices) > 1 else 0

def calculate_weighted_average(price_quantity_pairs):
    total_weighted_price = sum(p * q for p, q in price_quantity_pairs)
    total_quantity = sum(q for p, q in price_quantity_pairs)
    return total_weighted_price / total_quantity if total_quantity > 0 else 0

def search_item_by_market_hash_name(item_name):
    if "stattrak" in item_name.lower():
        category = 2
    elif "souvenir" in item_name.lower():
        category = 3
    elif any(x in item_name.lower() for x in ["sticker", "case", "graffiti", "music kit", "charm", "pin", "patch"]):
        category = 0
    else:
        category = 1

    params = {"market_hash_name": item_name.strip(), "category": category, "sort": "lowest_price"}
    for _ in range(3):  # Retry mechanism
        response = requests.get(f"{BASE_URL}/listings", headers=headers, params=params)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if isinstance(data, list) and data:
                lowest_price_item = sorted(data, key=lambda x: x['price'])[0]
                return lowest_price_item['id'], lowest_price_item['price'], lowest_price_item['item'].get('paint_index', None)
        elif response.status_code == 429:
            print("🚧 Rate limited while searching item. Retrying...")
            time.sleep(5)
        else:
            break
    return None, None, None

def get_buy_orders(item_id, avg_sold_price):
    for _ in range(3):  # Retry mechanism
        response = requests.get(f"{BASE_URL}/listings/{item_id}/buy-orders?limit=10", headers=headers)
        if response.status_code == 200:
            buy_orders = response.json()
            filtered_orders = []
            if buy_orders:
                for order in buy_orders:
                    price, quantity = order["price"], order["qty"]
                    if price >= 0.5 * avg_sold_price:
                        filtered_orders.append((price, quantity))
                median_buy_price = calculate_median([p for p, q in filtered_orders])
                return median_buy_price if median_buy_price > 0 else calculate_weighted_average(filtered_orders)
        elif response.status_code == 429:
            print("🚧 Rate limited while fetching buy orders. Retrying...")
            time.sleep(5)
        else:
            break
    return None

def get_sold_prices(item_name, paint_index):
    for _ in range(3):  # Retry mechanism
        response = requests.get(f"{BASE_URL}/history/{requests.utils.quote(item_name, safe='()')}/sales?paint_index={paint_index}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                sold_prices = [sale["price"] for sale in data if "price" in sale]
                if not sold_prices:
                    return []
                std_dev = calculate_standard_deviation(sold_prices)
                median_price = calculate_median(sold_prices)
                filtered_prices = [p for p in sold_prices if p <= median_price + (1.5 * std_dev)]
                return filtered_prices if filtered_prices else sold_prices
        elif response.status_code == 429:
            print("🚧 Rate limited while fetching sold prices. Retrying...")
            time.sleep(5)
        else:
            break
    return []

# Load item list from .txt
with open("items.txt", "r", encoding="utf-8") as file:
    items = [line.strip() for line in file.readlines() if line.strip()]

output_lines = []

for item_name in items:
    print(f"⏳ Processing: {item_name}")
    item_id, item_price, paint_index = search_item_by_market_hash_name(item_name)
    time.sleep(5)

    if item_id and item_price and paint_index is not None:
        sold_prices = get_sold_prices(item_name, paint_index)
        time.sleep(5)

        if sold_prices:
            avg_sold_price = calculate_median(sold_prices)
            avg_buy_price = get_buy_orders(item_id, avg_sold_price)
            time.sleep(5)

            if avg_buy_price is not None:
                price_difference = abs(avg_sold_price - avg_buy_price)
                relative_difference = price_difference / avg_sold_price if avg_sold_price > 0 else 0

                if relative_difference < 0.05:
                    sold_price_weight = 1.2
                    buy_order_weight = 1.2
                elif relative_difference < 0.15:
                    sold_price_weight = 1.5
                    buy_order_weight = 1.2
                else:
                    sold_price_weight = 1.7
                    buy_order_weight = 1.0

                final_adjusted_price = (avg_buy_price * buy_order_weight + avg_sold_price * sold_price_weight) / (buy_order_weight + sold_price_weight)
                usd_price = round(final_adjusted_price / 100, 2)

                print(f"✅ {item_name}: {usd_price} USD")
                output_lines.append(f"{item_name},{usd_price}")
            else:
                print(f"⚠️ Only Buy Orders available for {item_name}")
        else:
            print(f"⚠️ No sold prices found for {item_name}")
    else:
        print(f"❌ No data found for {item_name}")

# Write to output file
with open("output_prices.txt", "w", encoding="utf-8") as f:
    for line in output_lines:
        f.write(line + "\n")

print("✅ Done! All prices have been saved in 'output_prices.txt'.")
