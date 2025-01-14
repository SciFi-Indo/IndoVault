import os, requests, threading
import tkinter as tk
from tkinter import TclError
from PIL import Image, ImageTk
from typing import Optional

import crypto_data, functions, blank_slate, utils

root = tk.Tk()
root.title("IndoVault - Cryptocurrency crypto_data")
root.attributes('-fullscreen', True)

background_label, deposited_entry, deposited_box, net_value_box = None, None, None, None
is_locked, threads_active = False, True
DEPOSIT_FILE = "deposited_value.txt"
deposited_value = tk.StringVar(value="0")


def setup_background_image(root):
    global background_label, background_photo
    image_path = r"assets\DSC00188.jpeg"
    image = Image.open(image_path)

    if image.mode != "RGBA":
        image = image.convert("RGBA")

    if not background_label:
        background_label = tk.Label(root)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        background_label.lift()

    def resize_image():
        window_width, window_height = root.winfo_width(), root.winfo_height()
        image_resized = image.resize((window_width, window_height), Image.Resampling.LANCZOS)
        background_photo = ImageTk.PhotoImage(image_resized)
        background_label.config(image=background_photo)
        background_label.image = background_photo

    root.update_idletasks()
    resize_image()

setup_background_image(root)

def create_net_value_box():
    global net_value_box

    if net_value_box is not None:
        return

    net_value_box = tk.Canvas(root, width=220, height=90, bg="black", bd=0, highlightthickness=2, highlightbackground="red")
    net_value_box.create_oval(10, 10, 210, 80, fill="darkblue", outline="darkblue", width=0)
    net_value_box.create_text(110, 30, text="NET VALUE", font=("Arial", 14, "bold"), fill="white", justify="center")
    net_value_box.create_text(110, 60, text="$0.00", font=("Arial", 18, "bold"), fill="green", justify="center")
    net_value_box.grid(row=len(crypto_data.coins) + 3, column=0, columnspan=5, pady=20)

def delayed_create_net_value_box(*args):
    create_net_value_box()

root.after(100, delayed_create_net_value_box, (0,))

def save_deposited_value(value):
    with open(DEPOSIT_FILE, "w") as file:
        file.write(value)

def load_deposited_value():
    try:
        if os.path.exists(DEPOSIT_FILE):
            with open(DEPOSIT_FILE, "r") as file:
                return file.read().strip()
    except Exception as e:
        print(f"Error loading deposited value: {e}")
    return "0"

def on_enter(value, entry):
    global is_locked
    save_deposited_value(value.get())
    entry.config(state="disabled", fg="white", bg="darkblue", insertbackground="white")
    is_locked = True

def focus_in(value=None, entry=None):
    if not is_locked:
        value.set("")
        entry.select_range(0, tk.END)

def focus_out(value=None):
    if not is_locked:
        value.set(load_deposited_value())

def on_click_outside(event, entry_widget, value_widget):
    if not is_locked:
        if entry_widget.winfo_containing(event.x_root, event.y_root) != entry_widget:
            root.focus_set()
            value_widget.set(load_deposited_value())

def create_deposited_box():
    local_deposited_box = tk.Canvas(
        root, width=220, height=90, bg="black", bd=0, highlightthickness=2, highlightbackground="red"
    )
    local_deposited_box.create_rectangle(0, 0, 220, 90, fill="black", outline="black", width=0)
    local_deposited_box.create_oval(10, 10, 210, 80, fill="darkblue", outline="darkblue", width=0)
    local_deposited_box.create_text(110, 30, text="DEPOSITED", font=("Arial", 14, "bold"), fill="white", justify="center")
    local_deposited_box.create_text(30, 60, text="$", font=("Arial", 18, "bold"), fill="red", anchor="w")
    return local_deposited_box


def create_deposited_entry():
    entry_widget = tk.Entry(
        root, textvariable=deposited_value, font=("Arial", 18, "bold"), fg="red", justify="left",
        bd=0, bg="darkblue", insertbackground="white", width=9
    )

    def ensure_dollar_sign(p):
        if p == "" or p == "0":
            deposited_value.set("0")
        elif p.isdigit():
            return True
        return False

    entry_widget.config(
        validate="key", validatecommand=(root.register(ensure_dollar_sign), "%P")
    )
    return entry_widget


def bind_deposited_entry_events(entry_widget):
    entry_widget.bind("<FocusIn>", lambda _: focus_in(value=deposited_value, entry=entry_widget))
    entry_widget.bind("<FocusOut>", lambda _: focus_out(value=deposited_value))
    entry_widget.bind("<Return>", lambda _: on_enter(value=deposited_value, entry=entry_widget))

def create_value_boxes():
    global deposited_value, deposited_entry, deposited_box

    deposited_value.set(load_deposited_value())

    deposited_box = create_deposited_box()
    deposited_entry = create_deposited_entry()

    bind_deposited_entry_events(deposited_entry)

    deposited_box.create_window(110, 60, window=deposited_entry)

    deposited_box.grid(row=len(crypto_data.coins) + 3, column=11, columnspan=2, pady=20)

    root.bind("<Button-1>", lambda event: on_click_outside(event, deposited_entry, deposited_value))


coin_gecko_prices_fetched = False
prices_dict = {coin: "0" for coin in crypto_data.coins}
sorted_once = False

def get_price(coin, retries=7):
    if any(excluded_coin in coin for excluded_coin in crypto_data.excluded_coins):
        functions.fetch_excluded_coin_prices(prices_dict, root)
        return prices_dict.get(coin, "0")

    try:
        response = requests.get(crypto_data.BINANCE_API_URL, params={"symbol": coin})
        response.raise_for_status()
        response_data = response.json()
        if 'price' in response_data:
            price = str(float(response_data["price"]))
            if price != "0":
                brightened_color = functions.brighten_color("#008000", factor=2.5)
                crypto_data.price_labels[coin].config(text=f"${price}", fg=brightened_color)
                update_balance_for_coin(coin, price)
                update_profit_for_coin(coin, price)
                update_break_even_price_for_coin(coin)
            return price
        return "0"
    except requests.exceptions.RequestException:
        if retries > 0:
            return get_price(coin, retries - 1)
        return "0"


def update_prices(start_idx: int = 0):
    def worker(current_idx: int):
        if crypto_data.stop_event.is_set():
            return

        if current_idx >= len(crypto_data.coins):
            if not sorted_once:
                func_args = [prices_dict, functions.load_and_update_icon,
                             utils.update_wallet_label_for_coin, update_net_value, root]
                functions.sort_prices(*func_args)
            root.after(17000, update_prices, 0)
            return

        coin = crypto_data.coins[current_idx]
        price = get_price(coin)
        prices_dict[coin] = price

        def update_label():
            label = crypto_data.price_labels.get(coin)
            if label and label.winfo_exists():
                try:
                    label.config(text="Loading...", fg="red")
                    update_price_for_coin(coin, price, current_idx)
                except TclError:
                    print(f"Label for {coin} has been destroyed or is invalid.")

        root.after(0, update_label)

    threading.Thread(target=worker, args=(start_idx,)).start()


def update_price_for_coin(coin, price, current_idx):
    brightened_green = functions.brighten_color(utils.price_style["fg"], factor=2.5)
    crypto_data.price_labels[coin].config(text=f"${price}", fg=brightened_green)
    update_balance_for_coin(coin, price); update_profit_for_coin(coin, price)
    update_break_even_price_for_coin(coin); update_prices(current_idx + 1)
    update_net_value()


def update_balance_for_coin(coin, price):
    try:
        price_float = float(price)
        balance = crypto_data.holdings[coin] * price_float
        crypto_data.balance_labels[coin].config(text=f"${balance:.2f}")
    except ValueError:
        print(f"Invalid price for {coin}: {price}. Skipping balance update.")

def update_profit_for_coin(coin, price):
    balance = crypto_data.holdings[coin] * float(price)
    profit = balance - crypto_data.invested[coin]
    if profit >= 0:
        brightened_color = functions.brighten_color("#008000", factor=2.0)
        crypto_data.profit_labels[coin].config(text=f"${profit:.2f}", fg=brightened_color, font=("Arial", 16, "bold"))
    else:
        brightened_color = functions.brighten_color("#ff0000", factor=1.5)
        crypto_data.profit_labels[coin].config(text=f"${profit:.2f}", fg=brightened_color, font=("Arial", 16))

def calculate_break_even(coin):
    if crypto_data.holdings[coin] == 0:
        return 0
    return crypto_data.invested[coin] / crypto_data.holdings[coin]

def update_break_even_price_for_coin(coin):
    break_even_price = calculate_break_even(coin)
    current_price = prices_dict.get(coin, 0)
    if current_price != 0:
        break_even_price_formatted = f"{break_even_price:.5f}"
        if float(current_price) >= break_even_price:
            brightened_color = functions.brighten_color("#008000", factor=2.5)
            crypto_data.break_even_labels[coin].config(text=f"${break_even_price_formatted}", fg=brightened_color)
        else:
            brightened_color = functions.brighten_color("#ff0000", factor=2.5)
            crypto_data.break_even_labels[coin].config(text=f"${break_even_price_formatted}", fg=brightened_color)
    else:
        break_even_price_formatted = f"{break_even_price:.5f}"
        crypto_data.break_even_labels[coin].config(text=f"${break_even_price_formatted}",
                                       fg="yellow")

def update_net_value():
    global net_value_box
    total_net_value = 0
    for coin, holdings_amount in crypto_data.holdings.items():
        price = prices_dict.get(coin, 0)
        if price != 0:
            total_net_value += holdings_amount * float(price)

    invested_amount = 10075
    actual_net_value = total_net_value - invested_amount
    text_color = "#32CD32" if actual_net_value >= 0 else "#FF4500"

    net_value_box.delete("all")
    net_value_box.create_oval(10, 10, 200, 80, fill="darkblue", outline="darkblue", width=0)
    net_value_box.create_text(105, 30, text="NET VALUE", font=("Arial", 14, "bold"), fill="white", justify="center")
    net_value_box.create_text(105, 60, text=f"${actual_net_value:.2f}", font=("Arial", 18, "bold"),
                              fill=text_color, justify="center")


functions.fetch_excluded_coin_prices(prices_dict, root)
root.grid_columnconfigure(16, weight=1, minsize=150)

for idx, coin in enumerate(crypto_data.coins):
    functions.load_and_update_icon(coin)

    wallet_name = crypto_data.wallet_mapping.get(coin, "NA")

    if coin not in crypto_data.wallet_labels:
        crypto_data.wallet_labels[coin] = tk.Label(root, text=wallet_name, font=("Arial", 16, "bold"), fg="black",
                                                   bg="lightgray")

    crypto_data.wallet_labels[coin].grid_forget()
    crypto_data.wallet_labels[coin].grid(row=idx + 3, column=18, padx=10, pady=4)

#Initializations

blank_slate.setup_blank_slate_button(root, create_value_boxes, create_net_value_box,
                                      update_prices, get_price)
create_value_boxes(); utils.HeaderCreator(root, utils.header_style).create_all_headers()
utils.setup_grid(root); update_prices(); utils.setup_exit_buttonIV(root)


root.mainloop()
