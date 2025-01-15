import tkinter as tk
from PIL import Image, ImageTk
import os
import crypto_data, functions


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
        headers = [("COINS", 2, 0), ("PRICE", 2, 2), ("HOLDINGS", 2, 12),
                   ("BALANCE", 2, 6), ("INVESTED", 2, 8), ("PROFIT", 2, 10),
                   ("BREAK EVEN", 2, 4), ("WALLET", 2, 18)]
        for text, row, col in headers:
            self.create_header(text, row, col)


header_style = {"font": ("Arial", 20, "bold"), "fill": "white"}
label_style = {"font": ("Arial", 16, "bold"), "fg": "#800080", "bg": "black"}
price_style = {"font": ("Arial", 16, "bold"), "fg": "#00FF00", "bg": "black"}
amount_style = {"font": ("Arial", 16), "fg": "#66FF66", "bg": "black"}  # Lighter green
balance_style = {"font": ("Arial", 16), "fg": "#A64DFF", "bg": "black"}  # Brighter purple
invested_style = {"font": ("Arial", 16), "fg": "#A64DFF", "bg": "black"}  # Brighter purple
profit_style = {"font": ("Arial", 16), "fg": "#008000", "bg": "black"}
break_even_style = {"font": ("Arial", 16), "fg": "#ffff00", "bg": "black"}

def adjust_label_colors(tracker):
    styles = [label_style, price_style, amount_style, balance_style, invested_style, profit_style, break_even_style]
    factors = [1.5, 2.5, 2.0, 2.5, 2.5, 2.0, 1.5]
    for style, factor in zip(styles, factors):
        style["fg"] = tracker.brighten_color(style["fg"], factor=factor)

def initialize_tracker(root):
    global tracker
    tracker = functions.CryptoTracker(root)

def setup_grid(root):
    for index, coin in enumerate(crypto_data.coins):
        labels = [
            (crypto_data.label_labels, coin, label_style, 0),
            (crypto_data.price_labels, "Loading...", price_style, 2),
            (crypto_data.amount_labels, f"{crypto_data.holdings[coin]:.1f}", amount_style, 12),
            (crypto_data.balance_labels, "0", balance_style, 6),
            (crypto_data.invested_labels, f"${crypto_data.invested[coin]:,.2f}", invested_style, 8),
            (crypto_data.profit_labels, "0", profit_style, 10),
            (crypto_data.break_even_labels, "0", break_even_style, 4)
        ]
        for label_dict, text, style, col in labels:
            label = tk.Label(root, text=text, **style)
            label.grid(row=index + 3, column=col, padx=10, pady=4)
            label_dict[coin] = label

        icon_label = tk.Label(root)
        coin_name = crypto_data.coin_id_map.get(coin, coin).lower()
        icon_path = os.path.join("assets", "coin_icons", f"{coin_name}.png")
        img = Image.open(icon_path).resize((30, 30))
        photo = ImageTk.PhotoImage(img)
        icon_label.config(image=photo)
        icon_label.image = photo
        icon_label.grid(row=index + 3, column=1, padx=10, pady=4)
        crypto_data.icon_labels[coin] = icon_label

        wallet_name = crypto_data.wallet_mapping.get(coin, "NA")
        wallet_label = tk.Label(root, text=wallet_name, font=("Arial", 16, "bold"), fg="black", bg="red")
        wallet_label.grid(row=index + 3, column=18, padx=10, pady=4)
        crypto_data.wallet_labels[coin] = wallet_label

        update_wallet_label_for_coin(coin)

def update_wallet_label_for_coin(coin):
    wallet_group = crypto_data.wallet_mapping.get(coin, "NA")
    color = "gray" if wallet_group == "NA" else crypto_data.wallet_group_colors.get(wallet_group, "white")
    crypto_data.wallet_labels[coin].config(fg="black", bg=color, text=wallet_group, width=15)

def setup_exit_buttonIV(root):
    exit_button = tk.Button(root, text="Exit", command=lambda: (crypto_data.stop_event.set(), root.quit()),
                            font=("Arial", 20, "bold"), bg="red", fg="white", relief="solid", width=10, height=2)
    exit_button.bind("<Enter>", lambda e: exit_button.config(bg="darkred"))
    exit_button.bind("<Leave>", lambda e: exit_button.config(bg="red"))
    exit_button.grid(row=len(crypto_data.coins) + 3, column=3, columnspan=5, padx=10, pady=20)
