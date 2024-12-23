# functions.py
import os
import crypto_data
from PIL import Image, ImageTk
import tkinter as tk
import requests

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
                response = requests.get(f"{crypto_data.COINGECKO_API_URL}{coin_id}")
                coin_data = response.json()
                if 'market_data' in coin_data and 'current_price' in coin_data['market_data']:
                    price = coin_data['market_data']['current_price']['usd']
                    prices_dict[f"{excluded_coin_name}USDT"] = str(price)
            except Exception as e:
                continue

    root.after(900000, fetch_excluded_coin_prices, prices_dict, root)

def sort_prices(prices_dict, update_wallet_label_for_coin, update_icon_for_coin, update_net_value, root,
                label_style):
    global sorted_once
    sorted_once = True

    # Sort the coins
    sorted_coins = sorted(
        crypto_data.holdings.items(),
        key=lambda x: (
                crypto_data.holdings[x[0]] * float(prices_dict.get(x[0], 0))  # Ensure default is 0 if price not found
                - crypto_data.invested[x[0]]
        ),
        reverse=True
    )

    # Hide all labels before refreshing
    for coin in crypto_data.coins:
        # Create wallet label if it doesn't exist
        if coin not in crypto_data.wallet_labels:
            wallet_name = crypto_data.wallet_mapping.get(coin, "NA")
            crypto_data.wallet_labels[coin] = tk.Label(root, text=wallet_name, font=("Arial", 16), fg="cyan",
                                                       bg="black")
        # Now you can safely forget the wallet label
        crypto_data.wallet_labels[coin].grid_forget()
        crypto_data.label_labels[coin].grid_forget()
        crypto_data.price_labels[coin].grid_forget()
        crypto_data.amount_labels[coin].grid_forget()
        crypto_data.balance_labels[coin].grid_forget()
        crypto_data.invested_labels[coin].grid_forget()
        crypto_data.profit_labels[coin].grid_forget()
        crypto_data.break_even_labels[coin].grid_forget()
        crypto_data.icon_labels[coin].grid_forget()

    for idx, (coin, _) in enumerate(sorted_coins):
        # Fetch the price, default to None if not found
        price = prices_dict.get(coin, None)

        if price is None:
            print(f"Price for {coin} not available.")  # Debugging line
            balance = 0  # No price available, set balance to 0 (or handle as needed)
        else:
            balance = crypto_data.holdings[coin] * float(price)

        profit = balance - crypto_data.invested[coin]

        row_idx = idx + 3

        update_icon_for_coin(coin)
        # Now grid the labels after updating their content
        crypto_data.icon_labels[coin].grid(row=row_idx, column=1, padx=10, pady=4)
        crypto_data.label_labels[coin].grid(row=row_idx, column=0, padx=10, pady=4, sticky="w")  # Left-aligned
        crypto_data.price_labels[coin].grid(row=row_idx, column=2, padx=10, pady=4)
        crypto_data.amount_labels[coin].grid(row=row_idx, column=12, padx=10, pady=4)
        crypto_data.balance_labels[coin].grid(row=row_idx, column=6, padx=10, pady=4)
        crypto_data.invested_labels[coin].grid(row=row_idx, column=8, padx=10, pady=4)
        crypto_data.profit_labels[coin].grid(row=row_idx, column=10, padx=10, pady=4)
        crypto_data.break_even_labels[coin].grid(row=row_idx, column=4, padx=10, pady=4)
        crypto_data.wallet_labels[coin].grid(row=idx + 3, column=18, padx=10, pady=4)
        # Update the wallet label's color based on its group
        update_wallet_label_for_coin(coin)
    update_net_value()

# Open the image, resize it, and return the Tkinter-compatible format
def load_and_update_icon(coin: str):
    coin_name = crypto_data.coin_id_map.get(coin, "default")
    icon_path = os.path.join("C:\\Users\\lette\\PycharmProjects\\IndoVault\\coin_icons", f"{coin_name}.png")
    img = Image.open(icon_path).resize((30, 30))
    icon_tk = ImageTk.PhotoImage(img)

    if coin in crypto_data.icon_labels:
        crypto_data.icon_labels[coin].config(image=icon_tk)
        crypto_data.icon_labels[coin].image = icon_tk
