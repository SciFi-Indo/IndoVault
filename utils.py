# utils.py

import tkinter as tk
from PIL import Image, ImageTk
import os
import crypto_data  # Import the crypto_data module to access the global data
import functions

# Styling and padding values with hex color codes
header_style = {"font": ("Arial", 20, "bold"), "fill": "white"}
label_style = {"font": ("Arial", 16, "bold"), "fg": "#800080", "bg": "black"}  # purple -> #800080
price_style = {"font": ("Arial", 16, "bold"), "fg": "#00FF00", "bg": "black"}  # Green for coin prices
amount_style = {"font": ("Arial", 16), "fg": "#008000", "bg": "black"}  # green -> #008000
balance_style = {"font": ("Arial", 16), "fg": "#800080", "bg": "black"}  # purple -> #800080
invested_style = {"font": ("Arial", 16), "fg": "#800080", "bg": "black"}  # purple -> #800080
profit_style = {"font": ("Arial", 16), "fg": "#008000", "bg": "black"}  # green -> #008000
break_even_style = {"font": ("Arial", 16), "fg": "#ffff00", "bg": "black"}  # yellow -> #ffff00

# Apply the brighten_color function with a higher factor for the green styles
label_style["fg"] = functions.brighten_color(label_style["fg"], factor=1.5)
price_style["fg"] = functions.brighten_color(price_style["fg"], factor=2.5)
amount_style["fg"] = functions.brighten_color(amount_style["fg"], factor=2.0)  # Brighter green
balance_style["fg"] = functions.brighten_color(balance_style["fg"], factor=2.5)
invested_style["fg"] = functions.brighten_color(invested_style["fg"], factor=2.5)
profit_style["fg"] = functions.brighten_color(profit_style["fg"], factor=2.0)  # Brighter green
break_even_style["fg"] = functions.brighten_color(break_even_style["fg"], factor=1.5)

def setup_grid(root):
    # Create label for coin name
    for index, coin in enumerate(crypto_data.coins):
        label = tk.Label(root, text=coin, **label_style)
        label.grid(row=index + 3, column=0, padx=10, pady=4, sticky="w")
        crypto_data.label_labels[coin] = label

        # Create price label
        label = tk.Label(root, text="Loading...", **price_style)
        label.grid(row=index + 3, column=2, padx=10, pady=4)
        crypto_data.price_labels[coin] = label

        # Create amount label
        label = tk.Label(root, text=f"{crypto_data.holdings[coin]:.1f}", **amount_style)
        label.grid(row=index + 3, column=12, padx=10, pady=4)
        crypto_data.amount_labels[coin] = label

        # Create balance label
        label = tk.Label(root, text="0", **balance_style)
        label.grid(row=index + 3, column=6, padx=10, pady=4)
        crypto_data.balance_labels[coin] = label

        # Create invested label
        label = tk.Label(root, text=f"${crypto_data.invested[coin]:,.2f}", **invested_style)
        label.grid(row=index + 3, column=8, padx=10, pady=4)
        crypto_data.invested_labels[coin] = label

        # Create profit label
        label = tk.Label(root, text="0", **profit_style)
        label.grid(row=index + 3, column=10, padx=10, pady=4)
        crypto_data.profit_labels[coin] = label

        # Create break-even label
        label = tk.Label(root, text="0", **break_even_style)
        label.grid(row=index + 3, column=4, padx=10, pady=4)
        crypto_data.break_even_labels[coin] = label

        # Create icon label
        label = tk.Label(root)
        coin_name = crypto_data.coin_id_map.get(coin, coin).lower()
        icon_path = os.path.join("assets", "coin_icons", f"{coin_name}.png")
        img = Image.open(icon_path).resize((30, 30))
        photo = ImageTk.PhotoImage(img)
        label.config(image=photo)
        label.image = photo
        label.grid(row=index + 3, column=1, padx=10, pady=4)
        crypto_data.icon_labels[coin] = label

        # Add wallet label
        wallet_name = crypto_data.wallet_mapping.get(coin, "NA")
        crypto_data.wallet_labels[coin] = tk.Label(root, text=wallet_name, font=("Arial", 16, "bold"),
                                                   fg="black", bg="red")
        crypto_data.wallet_labels[coin].grid(row=index + 3, column=18, padx=10, pady=4)

        # Update wallet label color and name
        update_wallet_label_for_coin(coin)


# Function to create headers

class HeaderCreator:
    def __init__(self, root, header_style):
        self.root = root
        self.header_style = header_style
        self.headers = []

    def create_header(self, text, row, col):
        header = tk.Canvas(self.root, width=200, height=60, bg="black", bd=0, highlightthickness=0)
        header.create_oval(5, 5, 195, 55, fill="blue", outline="blue", width=0)
        header.create_text(100, 30, text=text, **self.header_style)
        header.grid(row=row, column=col, padx=10, pady=(10, 5))
        self.headers.append(header)

    def create_all_headers(self):
        self.create_header("COINS", 2, 0)
        self.create_header("PRICE", 2, 2)
        self.create_header("HOLDINGS", 2, 12)
        self.create_header("BALANCE", 2, 6)
        self.create_header("INVESTED", 2, 8)
        self.create_header("PROFIT", 2, 10)
        self.create_header("BREAK EVEN", 2, 4)
        self.create_header("WALLET", 2, 18)

# Updated wallet label function:

def update_wallet_label_for_coin(coin):
    wallet_group = crypto_data.wallet_mapping.get(coin, "NA")

    # Set color based on the group
    if wallet_group == "NA":
        color = "gray"  # Default color for "NA"
    else:
        color = crypto_data.wallet_group_colors.get(wallet_group, "white")  # Fallback to white for unknown groups

    # Update wallet label text and color
    crypto_data.wallet_labels[coin].config(fg="black", bg=color, text=wallet_group, width=15)


# Function to set up the exit button

def setup_exit_buttonIV(root):
    # Exit Button Setup
    exit_button = tk.Button(root, text="Exit", command=lambda: (crypto_data.stop_event.set(), root.quit()),
                            font=("Arial", 20, "bold"), bg="red", fg="white", relief="solid", width=10, height=2)

    # Hover effect setup
    exit_button.bind("<Enter>", lambda e: exit_button.config(bg="darkred"))
    exit_button.bind("<Leave>", lambda e: exit_button.config(bg="red"))

    # Place the button
    exit_button.grid(row=len(crypto_data.coins) + 3, column=3, columnspan=5, padx=10, pady=20)


