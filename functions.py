# functions.py
import os
import crypto_data
from PIL import Image, ImageTk
import requests
import threading

sorted_once = False

def brighten_color(hex_color, factor=1.5):
    """Brighten the color by multiplying the RGB components."""
    # Ensure color is in the format #RRGGBB
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    # Apply the brightness factor and clip the value to the range [0, 255]
    r = min(255, int(r * factor))
    g = min(255, int(g * factor))
    b = min(255, int(b * factor))

    return f'#{r:02x}{g:02x}{b:02x}'


def fetch_excluded_coin_prices(prices_dict, root):
    for excluded_coin_name in crypto_data.excluded_coins:
        coin_id = crypto_data.coin_id_map.get(f"{excluded_coin_name}USDT", "")
        if coin_id:
            try:
                response = requests.get(f"{crypto_data.COINGECKO_API_URL}{coin_id}", timeout=10)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                coin_data = response.json()
                if 'market_data' in coin_data and 'current_price' in coin_data['market_data']:
                    price = coin_data['market_data']['current_price']['usd']
                    prices_dict[f"{excluded_coin_name}USDT"] = str(price)
            except (requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout):
                pass  # Handle known errors silently (optional)

    # Schedule the function to run again after 15 minutes (900,000 ms)
    root.after(900000, fetch_excluded_coin_prices, prices_dict, root)

def sort_prices(prices_dict, update_wallet_label_for_coin, update_icon_for_coin, update_net_value, root):
    global sorted_once
    sorted_once = True

    def sort_worker():
        if crypto_data.stop_event.is_set():  # Check if the event is set
            return  # Stop the sorting worker if stop_event is set

        sorted_coins = sort_coins_by_balance(prices_dict)
        root.after(0, hide_labels)
        root.after(0, regrid_labels, sorted_coins, prices_dict, update_wallet_label_for_coin, update_icon_for_coin)
        root.after(0, update_net_value)

    threading.Thread(target=sort_worker).start()


def sort_coins_by_balance(prices_dict):

    return sorted(
        crypto_data.holdings.items(),
        key=lambda x: (
                crypto_data.holdings[x[0]] * float(prices_dict.get(x[0], 0))  # Default to 0 if price not found
                - crypto_data.invested[x[0]]
        ),
        reverse=True
    )

def hide_labels():

    for coin in crypto_data.coins:
        # Forget previous label positions
        crypto_data.wallet_labels[coin].grid_forget()
        crypto_data.label_labels[coin].grid_forget()
        crypto_data.price_labels[coin].grid_forget()
        crypto_data.amount_labels[coin].grid_forget()
        crypto_data.balance_labels[coin].grid_forget()
        crypto_data.invested_labels[coin].grid_forget()
        crypto_data.profit_labels[coin].grid_forget()
        crypto_data.break_even_labels[coin].grid_forget()
        crypto_data.icon_labels[coin].grid_forget()


def regrid_labels(sorted_coins, prices_dict, update_wallet_label_for_coin, update_icon_for_coin):
    for idx, (coin, _) in enumerate(sorted_coins):
        price = prices_dict.get(coin, None)
        balance = 0 if price is None else crypto_data.holdings[coin] * float(price)
        _ = balance - crypto_data.invested[coin]  # Calculate profit, but don't use it
        row_idx = idx + 3  # Adjust row index for proper placement
        # Update icon and wallet labels
        update_icon_for_coin(coin)
        update_wallet_label_for_coin(coin)

        # Re-grid the labels
        grid_labels_for_coin(coin, row_idx)


def grid_labels_for_coin(coin, row_idx):

    crypto_data.icon_labels[coin].grid(row=row_idx, column=1, padx=10, pady=4)
    crypto_data.label_labels[coin].grid(row=row_idx, column=0, padx=10, pady=4, sticky="w")  # Left-aligned
    crypto_data.price_labels[coin].grid(row=row_idx, column=2, padx=10, pady=4)
    crypto_data.amount_labels[coin].grid(row=row_idx, column=12, padx=10, pady=4)
    crypto_data.balance_labels[coin].grid(row=row_idx, column=6, padx=10, pady=4)
    crypto_data.invested_labels[coin].grid(row=row_idx, column=8, padx=10, pady=4)
    crypto_data.profit_labels[coin].grid(row=row_idx, column=10, padx=10, pady=4)
    crypto_data.break_even_labels[coin].grid(row=row_idx, column=4, padx=10, pady=4)
    crypto_data.wallet_labels[coin].grid(row=row_idx, column=18, padx=10, pady=4)

# Open the image, resize it, and return the Tkinter-compatible format
def load_and_update_icon(coin: str):
    coin_name = crypto_data.coin_id_map.get(coin, "default")
    # Using relative path for coin_icons inside assets folder
    icon_path = os.path.join("assets", "coin_icons", f"{coin_name}.png")
    img = Image.open(icon_path).resize((30, 30))
    icon_tk = ImageTk.PhotoImage(img)

    if coin in crypto_data.icon_labels:
        crypto_data.icon_labels[coin].config(image=icon_tk)
        crypto_data.icon_labels[coin].image = icon_tk

