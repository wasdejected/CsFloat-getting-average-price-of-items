# CsFloat-getting-average-price-of-items
This Python script automatically retrieves and analyzes average market prices for CS2/CS:GO items using the CsFloat API. It fetches both buy orders and historical sold prices, filters out anomalies, and calculates a realistic average price for each item in your list. The results are written to output_prices.txt in USD.


⚙️ Features

🔍 Automated item lookup: Searches items by their full market hash name.

📈 Smart price filtering: Removes outliers using median and standard deviation calculations.

💰 Weighted average system: Combines buy orders and sold prices with adaptive weights to reflect real market trends.

⏱ Rate-limit handling: Automatically retries when the CsFloat API returns a 429 Too Many Requests error.

🧠 Category detection: Automatically identifies StatTrak™, Souvenir, and other special item types.

📊 Accurate results: Converts the final average price into USD with proper rounding.


Input:
A text file named items.txt, containing one item name per line.


AK-47 | Redline (Field-Tested)
M4A4 | Desolate Space (Minimal Wear)
Glock-18 | Fade (Factory New)


Output:

AK-47 | Redline (Field-Tested),9.73
M4A4 | Desolate Space (Minimal Wear),12.15
Glock-18 | Fade (Factory New),286.42



🧰 Technical Overview

API Used: CsFloat API

Libraries: requests, numpy, time

Core Functions:

calculate_median() and calculate_standard_deviation() for data smoothing

calculate_weighted_average() for realistic price aggregation

search_item_by_market_hash_name() to locate the item’s market entry

get_sold_prices() to analyze historical sale data

get_buy_orders() to retrieve live market buy orders



🕹️ How to Use

Replace the API_KEY value with your CsFloat API key.

Create items.txt and list the items you want to analyze.

Run the script
