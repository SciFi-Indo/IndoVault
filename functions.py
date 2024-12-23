# functions.py
import os
from crypto_data import *
from PIL import Image, ImageTk
import tkinter as tk
import requests

def fetch_excluded_coin_prices(prices_dict, root):
    for excluded_coin_name in excluded_coins:
        coin_id = coin_id_map.get(f"{excluded_coin_name}USDT", "")
        if coin_id:
            try:
                response = requests.get(f"{COINGECKO_API_URL}{coin_id}")
                coin_data = response.json()
                if 'market_data' in coin_data and 'current_price' in coin_data['market_data']:
                    price = coin_data['market_data']['current_price']['usd']
                    prices_dict[f"{excluded_coin_name}USDT"] = str(price)
            except Exception as e:
                continue

    root.after(900000, fetch_excluded_coin_prices, prices_dict, root)

def sort_prices(prices_dict, update_wallet_label_for_coin, update_icon_for_coin, update_net_value, root):
    global sorted_once
    sorted_once = True

    # Sort the coins
    sorted_coins = sorted(
        holdings.items(),
        key=lambda x: (
                holdings[x[0]] * float(prices_dict.get(x[0], 0))  # Ensure default is 0 if price not found
                - invested[x[0]]
        ),
        reverse=True
    )

    # Hide all labels before refreshing
    for coin in coins:
        # Create wallet label if it doesn't exist
        if coin not in wallet_labels:
            wallet_name = wallet_mapping.get(coin, "NA")
            wallet_labels[coin] = tk.Label(root, text=wallet_name, font=("Arial", 16), fg="cyan",
                                            bg="black")
        # Now you can safely forget the wallet label
        wallet_labels[coin].grid_forget()
        label_labels[coin].grid_forget()
        price_labels[coin].grid_forget()
        amount_labels[coin].grid_forget()
        balance_labels[coin].grid_forget()
        invested_labels[coin].grid_forget()
        profit_labels[coin].grid_forget()
        break_even_labels[coin].grid_forget()
        icon_labels[coin].grid_forget()

    for idx, (coin, _) in enumerate(sorted_coins):
        # Fetch the price, default to None if not found
        price = prices_dict.get(coin, None)

        if price is None:
            print(f"Price for {coin} not available.")  # Debugging line
            balance = 0  # No price available, set balance to 0 (or handle as needed)
        else:
            balance = holdings[coin] * float(price)

        profit = balance - invested[coin]

        row_idx = idx + 3

        update_icon_for_coin(coin)
        # Now grid the labels after updating their content
        icon_labels[coin].grid(row=row_idx, column=1, padx=10, pady=4)
        label_labels[coin].grid(row=row_idx, column=0, padx=10, pady=4, sticky="w")  # Left-aligned
        price_labels[coin].grid(row=row_idx, column=2, padx=10, pady=4)
        amount_labels[coin].grid(row=row_idx, column=12, padx=10, pady=4)
        balance_labels[coin].grid(row=row_idx, column=6, padx=10, pady=4)
        invested_labels[coin].grid(row=row_idx, column=8, padx=10, pady=4)
        profit_labels[coin].grid(row=row_idx, column=10, padx=10, pady=4)
        break_even_labels[coin].grid(row=row_idx, column=4, padx=10, pady=4)
        wallet_labels[coin].grid(row=idx + 3, column=16, padx=10, pady=4, sticky="e")
        # Update the wallet label's color based on its group
        update_wallet_label_for_coin(coin)
    update_net_value()


# Open the image, resize it, and return the Tkinter-compatible format
def load_and_update_icon(coin: str):
    coin_name = coin_id_map.get(coin, "default")
    icon_path = os.path.join("C:\\Users\\lette\\PycharmProjects\\IndoVault\\coin_icons", f"{coin_name}.png")
    img = Image.open(icon_path).resize((30, 30))
    icon_tk = ImageTk.PhotoImage(img)

    if coin in icon_labels:
        icon_labels[coin].config(image=icon_tk)
        icon_labels[coin].image = icon_tk
