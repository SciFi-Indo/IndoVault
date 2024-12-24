# Standard Library Imports
import time
import requests
import os
import tkinter as tk
from PIL import Image, ImageTk

# Local Imports
import crypto_data
import functions

# Set up the GUI window
root = tk.Tk()
root.title("IndoVault - Cryptocurrency Tracker")
root.configure(bg="black")
root.attributes('-fullscreen', True)

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

# Global state variables
is_locked = False  # Start with the field unlocked by default
DEPOSIT_FILE = "deposited_value.txt"
deposited_value = tk.StringVar(value="0")  # Default to 0
net_value_box = None  # Initialize as None, so we know it hasn't been created yet

# The actual function that creates the net value box
def create_net_value_box():
    global net_value_box  # Declare the global variable here
    print("Creating net value box...")

    # Prevent re-creating the net value box if it already exists
    if net_value_box:
        return  # Exit if net_value_box already exists

    # Create the canvas for the net value display
    net_value_box = tk.Canvas(root, width=220, height=90, bg="black", bd=0, highlightthickness=2, highlightbackground="red")
    net_value_box.create_oval(10, 10, 210, 80, fill="darkblue", outline="darkblue", width=0)  # Oval dimensions
    net_value_box.create_text(110, 30, text="NET VALUE", font=("Arial", 14, "bold"), fill="white", justify="center")
    net_value_box.create_text(110, 60, text="$0.00", font=("Arial", 18, "bold"), fill="green", justify="center")

    # Place the net value box in the grid
    net_value_box.grid(row=len(crypto_data.coins) + 3, column=0, columnspan=5, pady=20)

# Function that introduces the delay
def delayed_create_net_value_box():
    print("Creating net value box...")  # Debugging line
    create_net_value_box()

# Delay the creation of the net value box by 100ms to ensure window is ready
root.after(100, delayed_create_net_value_box)


# Function to save the deposited value to a file
def save_deposited_value(value):
    with open(DEPOSIT_FILE, "w") as file:
        file.write(value)

# Improved load_deposited_value with error handling
def load_deposited_value():
    try:
        if os.path.exists(DEPOSIT_FILE):
            with open(DEPOSIT_FILE, "r") as file:
                return file.read().strip()  # Remove any extra spaces or newlines
    except Exception as e:
        print(f"Error loading deposited value: {e}")
    return "0"  # Default value if no file exists or an error occurs

# Function to handle "Enter" key press (finalize value entry)
def on_enter(event, deposited_value, deposited_entry):
    global is_locked

    # Save the deposited value to file
    save_deposited_value(deposited_value.get())

    # Lock the field after pressing Enter
    deposited_entry.config(state="disabled", fg="white", bg="darkblue", insertbackground="white")
    is_locked = True  # Lock the entry field

# Function to handle FocusIn (clear content if unlocked)
def focus_in(event=None, deposited_value=None, deposited_entry=None):
    if not is_locked:
        deposited_value.set("")  # Clear the content on click
        deposited_entry.select_range(0, tk.END)

# Function to handle FocusOut (reset to saved value if unlocked)
def focus_out(event=None, deposited_value=None):
    if not is_locked:
        deposited_value.set(load_deposited_value())  # Reset to the saved value when focus is lost

# Function to handle clicking outside (reset value if unlocked)
def on_click_outside(event, deposited_entry, deposited_value):
    if not is_locked:
        if deposited_entry.winfo_containing(event.x_root, event.y_root) != deposited_entry:
            root.focus_set()
            deposited_value.set(load_deposited_value())  # Reset to the saved value (if any)


# Function to create headers
# Create the deposited box (Canvas) and Entry widget

def create_value_boxes():
    global deposited_value, deposited_entry, deposited_box # Access global variables

    # Load the deposited value from the file at the start
    deposited_value.set(load_deposited_value())  # Load from file, default to "0"

    # Create deposited_box (Canvas) for the deposited value input
    deposited_box = tk.Canvas(root, width=220, height=90, bg="black", bd=0, highlightthickness=2, highlightbackground="red")  # Red border
    deposited_box.create_rectangle(0, 0, 220, 90, fill="black", outline="black", width=0)  # Black background
    deposited_box.create_oval(10, 10, 210, 80, fill="darkblue", outline="darkblue", width=0)  # Oval on top
    deposited_box.create_text(110, 30, text="DEPOSITED", font=("Arial", 14, "bold"), fill="white", justify="center")
    deposited_box.create_text(30, 60, text="$", font=("Arial", 18, "bold"), fill="red", anchor="w")

    # Create the Entry widget for user input
    deposited_entry = tk.Entry(root, textvariable=deposited_value, font=("Arial", 18, "bold"), fg="red", justify="left",
                               bd=0, bg="darkblue", insertbackground="white", width=9)

    # Ensure dollar sign in the input (validation function)
    def ensure_dollar_sign(p):
        if p == "" or p == "0":
            deposited_value.set("0")
        elif p.isdigit():
            return True
        return False

    deposited_entry.config(validate="key", validatecommand=(root.register(ensure_dollar_sign), "%P"))

    # Bind events for focus and clicking outside
    deposited_entry.bind("<FocusIn>", lambda event: focus_in(event, deposited_value, deposited_entry))
    deposited_entry.bind("<FocusOut>", lambda event: focus_out(event, deposited_value))

    # Bind "Enter" key to update the value and lock the field
    deposited_entry.bind("<Return>", lambda event: on_enter(event, deposited_value, deposited_entry))

    # Add Entry widget inside the Canvas
    deposited_box.create_window(110, 60, window=deposited_entry)

    # Remove padx from deposited_box to align it similarly to net_value_box
    deposited_box.grid(row=len(crypto_data.coins) + 3, column=11, columnspan=2, pady=20)

    # Bind click event to root window to handle clicking outside (without saving)
    root.bind("<Button-1>", lambda event: on_click_outside(event, deposited_entry, deposited_value))


def create_headers():
    header_coins = tk.Canvas(root, width=200, height=60, bg="black", bd=0, highlightthickness=0)
    header_coins.create_oval(5, 5, 195, 55, fill="blue", outline="blue", width=0)
    header_coins.create_text(100, 30, text="COINS", **header_style)
    header_coins.grid(row=2, column=0, padx=10, pady=(10, 5))

    header_price = tk.Canvas(root, width=180, height=60, bg="black", bd=0, highlightthickness=0)
    header_price.create_oval(5, 5, 175, 55, fill="blue", outline="blue", width=0)
    header_price.create_text(90, 30, text="PRICE", **header_style)
    header_price.grid(row=2, column=2, padx=10, pady=(10, 5))

    header_holdings = tk.Canvas(root, width=200, height=60, bg="black", bd=0, highlightthickness=0)
    header_holdings.create_oval(5, 5, 195, 55, fill="blue", outline="blue", width=0)
    header_holdings.create_text(100, 30, text="HOLDINGS", **header_style)
    header_holdings.grid(row=2, column=12, padx=10, pady=(10, 5))

    header_balance = tk.Canvas(root, width=200, height=60, bg="black", bd=0, highlightthickness=0)
    header_balance.create_oval(5, 5, 195, 55, fill="blue", outline="blue", width=0)
    header_balance.create_text(100, 30, text="BALANCE", **header_style)
    header_balance.grid(row=2, column=6, padx=10, pady=(10, 5))

    header_invested = tk.Canvas(root, width=200, height=60, bg="black", bd=0, highlightthickness=0)
    header_invested.create_oval(5, 5, 195, 55, fill="blue", outline="blue", width=0)
    header_invested.create_text(100, 30, text="INVESTED", **header_style)
    header_invested.grid(row=2, column=8, padx=10, pady=(10, 5))

    header_profit = tk.Canvas(root, width=200, height=60, bg="black", bd=0, highlightthickness=0)
    header_profit.create_oval(5, 5, 195, 55, fill="blue", outline="blue", width=0)
    header_profit.create_text(100, 30, text="PROFIT", **header_style)
    header_profit.grid(row=2, column=10, padx=10, pady=(10, 5))

    header_break_even = tk.Canvas(root, width=200, height=60, bg="black", bd=0, highlightthickness=0)
    header_break_even.create_oval(5, 5, 195, 55, fill="blue", outline="blue", width=0)
    header_break_even.create_text(100, 30, text="BREAK EVEN", **header_style)
    header_break_even.grid(row=2, column=4, padx=10, pady=(10, 5))

    header_wallet = tk.Canvas(root, width=200, height=60, bg="black", bd=0, highlightthickness=0)
    header_wallet.create_oval(5, 5, 195, 55, fill="blue", outline="blue", width=0)
    header_wallet.create_text(100, 30, text="WALLET", **header_style)
    header_wallet.grid(row=2, column=18, padx=10, pady=(10, 5), sticky="e")

# Function to set up the exit button
def setup_exit_button():
    # Exit Button Setup
    exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 20, "bold"), bg="red", fg="white",
                            relief="solid")

    # Hover effect (inline)
    exit_button.bind("<Enter>", lambda e: exit_button.config(bg="darkred"))
    exit_button.bind("<Leave>", lambda e: exit_button.config(bg="red"))

    # Place the button
    exit_button.grid(row=len(crypto_data.coins) + 3, column=5, columnspan=5, padx=10, pady=20)

# Foreground image setup (image will be on top of the grid but transparent)
image_path = r"C:\Users\lette\PycharmProjects\IndoVault\DSC00188.jpeg"
image = Image.open(image_path)

# Convert to RGBA if the image is not in that mode
if image.mode != "RGBA":
    image = image.convert("RGBA")

# Create the label to hold the image
background_label = tk.Label(root)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
background_label.lift()

# Resize the image and update the label
def resize_image():
    window_width, window_height = root.winfo_width(), root.winfo_height()
    image_resized = image.resize((window_width, window_height), Image.Resampling.LANCZOS)
    background_photo = ImageTk.PhotoImage(image_resized)
    background_label.config(image=background_photo)
    background_label.image = background_photo

# Trigger layout update and resize the image
root.update_idletasks()
resize_image()


def setup_grid():
    # Create labels for each coin and position them in a grid
    for idx, coin in enumerate(crypto_data.coins):
        # Initialize label for the coin
        crypto_data.label_labels[coin] = tk.Label(root, text=coin, **label_style)
        crypto_data.label_labels[coin].grid(row=idx + 3, column=0, padx=10, pady=4, sticky="w")

        # Initialize price, amount, balance, etc., labels
        crypto_data.price_labels[coin] = tk.Label(root, text="Loading...", **price_style)
        crypto_data.price_labels[coin].grid(row=idx + 3, column=2, padx=10, pady=4)

        crypto_data.amount_labels[coin] = tk.Label(root, text=f"{crypto_data.holdings[coin]:.1f}", **amount_style)
        crypto_data.amount_labels[coin].grid(row=idx + 3, column=12, padx=10, pady=4)

        crypto_data.balance_labels[coin] = tk.Label(root, text="0", **balance_style)
        crypto_data.balance_labels[coin].grid(row=idx + 3, column=6, padx=10, pady=4)

        crypto_data.invested_labels[coin] = tk.Label(root, text=f"${crypto_data.invested[coin]:,.2f}", **invested_style)
        crypto_data.invested_labels[coin].grid(row=idx + 3, column=8, padx=10, pady=4)

        crypto_data.profit_labels[coin] = tk.Label(root, text="0", **profit_style)
        crypto_data.profit_labels[coin].grid(row=idx + 3, column=10, padx=10, pady=4)

        crypto_data.break_even_labels[coin] = tk.Label(root, text="0", **break_even_style)
        crypto_data.break_even_labels[coin].grid(row=idx + 3, column=4, padx=10, pady=4)

        crypto_data.icon_labels[coin] = tk.Label(root)
        crypto_data.icon_labels[coin].grid(row=idx + 3, column=1, padx=10, pady=4)

        # Initialize wallet label unconditionally (along with the other labels)
        wallet_name = crypto_data.wallet_mapping.get(coin, "NA")
        crypto_data.wallet_labels[coin] = tk.Label(root, text=wallet_name, font=("Arial", 16, "bold"), fg="black", bg="red")
        crypto_data.wallet_labels[coin].grid(row=idx + 3, column=18, padx=10, pady=4)

        # Adjust the coin name to match the lowercase icon filename
        coin_name = crypto_data.coin_id_map.get(coin, coin).lower()
        icon_path = f"C:/Users/lette/PycharmProjects/IndoVault/coin_icons/{coin_name}.png"

        try:
            img = Image.open(icon_path)
            img = img.resize((30, 30))  # Resize to fit the label
            photo = ImageTk.PhotoImage(img)
            crypto_data.icon_labels[coin].config(image=photo)
            crypto_data.icon_labels[coin].image = photo  # Keep a reference to avoid garbage collection
        except Exception as e:
            print(f"Icon not found for {coin}, skipping icon. Error: {e}")

        # Update the wallet label based on the wallet group color
        update_wallet_label_for_coin(coin)  # This will update the color and text for each wallet label

# Flag to check if CoinGecko prices have been fetched
coin_gecko_prices_fetched = False

# Dictionary to store the prices as they are fetched
prices_dict = {coin: "0" for coin in crypto_data.coins}

# A flag to track if sorting has already been done
sorted_once = False

# Modify the get_price function to use CoinGecko prices for excluded coins
def get_price(coin, retries=7):
    if any(excluded_coin in coin for excluded_coin in crypto_data.excluded_coins):
        functions.fetch_excluded_coin_prices(prices_dict, root)  # Ensure CoinGecko prices are fetched
        return prices_dict.get(coin, "0")  # Return the CoinGecko price if it exists

    try:
        response = requests.get(crypto_data.BINANCE_API_URL, params={"symbol": coin})
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        response_data = response.json()
        if 'price' in response_data:
            price = str(float(response_data["price"]))
            if price != "0":  # If price is valid, update the label
                brightened_color = functions.brighten_color("#008000", factor=2.5)
                crypto_data.price_labels[coin].config(text=f"${price}", fg=brightened_color)
                update_balance_for_coin(coin, price)  # Update balance after price
                update_profit_for_coin(coin, price)  # Update profit after price
                update_break_even_price_for_coin(coin)  # Update break-even price
            return price
        return "0"  # Return 0 if no price is found
    except requests.exceptions.RequestException as e:
        if retries > 0:
            return get_price(coin, retries - 1)  # Retry the request
        return "0"  # Return 0 if all retries fail

# Function to update the price for each coin in the GUI (one by one with delay)
def update_prices(idx=0):
    if idx >= len(crypto_data.coins):
        if not sorted_once:
            functions.sort_prices(
                prices_dict, functions.load_and_update_icon, update_wallet_label_for_coin,
                update_net_value, root, label_style
            )
        root.after(300000, update_prices)  # Update prices every 5 minutes
        return

    coin = crypto_data.coins[idx]
    price = get_price(coin)
    prices_dict[coin] = price
    crypto_data.price_labels[coin].config(text="Loading...", fg="red")

    root.after(300, update_price_for_coin, coin, price, idx)
    time.sleep(0.1)  # Small delay to manage load

# Function to update the price for each coin in the GUI (one by one with delay)
def update_price_for_coin(coin, price, idx):
    # Brighten the green color only for the price label
    brightened_green = functions.brighten_color(price_style["fg"], factor=2.5)  # Brighten the green color
    crypto_data.price_labels[coin].config(text=f"${price}", fg=brightened_green)  # Apply the brightened color to price
    update_balance_for_coin(coin, price)  # Update balance after price
    update_profit_for_coin(coin, price)  # Update profit after price
    update_break_even_price_for_coin(coin)  # Update break-even price
    update_prices(idx + 1)  # Continue with the next coin
    update_net_value()  # Ensure the net value updates after each price change

# Function to update the balance for each coin (price * holdings)
def update_balance_for_coin(coin, price):
    try:
        # Ensure that the price is a valid number
        price_float = float(price)
        # Calculate the balance (holdings * price)
        balance = crypto_data.holdings[coin] * price_float

        # Update the balance label with the formatted balance (e.g., 2 decimal places)
        crypto_data.balance_labels[coin].config(text=f"${balance:.2f}")

    except ValueError:
        print(f"Invalid price for {coin}: {price}. Skipping balance update.")
        # Handle the error or skip the coin

# Function to update the profit for each coin (balance - invested)
def update_profit_for_coin(coin, price):
    balance = crypto_data.holdings[coin] * float(price)
    profit = balance - crypto_data.invested[coin]
    # Profit in green if positive, red if negative, bold green if positive
    if profit >= 0:
        brightened_color = functions.brighten_color("#008000", factor=2.0)  # Brighter green for gain
        crypto_data.profit_labels[coin].config(text=f"${profit:.2f}", fg=brightened_color, font=("Arial", 16, "bold"))
    else:
        brightened_color = functions.brighten_color("#ff0000", factor=1.5)  # Brighter red for loss
        crypto_data.profit_labels[coin].config(text=f"${profit:.2f}", fg=brightened_color, font=("Arial", 16))

# Function to calculate break even price
def calculate_break_even(coin):
    if crypto_data.holdings[coin] == 0:
        return 0
    return crypto_data.invested[coin] / crypto_data.holdings[coin]

# Function to update the break even price for each coin
def update_break_even_price_for_coin(coin):
    break_even_price = calculate_break_even(coin)
    current_price = prices_dict.get(coin, 0)  # Get the current price

    # If current price is available, compare it with the break-even price
    if current_price != 0:
        # Display 5 decimal places for break-even price
        break_even_price_formatted = f"{break_even_price:.5f}"

        if float(current_price) >= break_even_price:
            brightened_color = functions.brighten_color("#008000", factor=2.5)  # Brighter green
            crypto_data.break_even_labels[coin].config(text=f"${break_even_price_formatted}", fg=brightened_color)
        else:
            brightened_color = functions.brighten_color("#ff0000", factor=2.5)  # Brighter red
            crypto_data.break_even_labels[coin].config(text=f"${break_even_price_formatted}", fg=brightened_color)

    else:
        # Display 5 decimal places for break-even price when current price is not available
        break_even_price_formatted = f"{break_even_price:.5f}"
        crypto_data.break_even_labels[coin].config(text=f"${break_even_price_formatted}",
                                       fg="yellow")  # Default color (yellow) if price is not available

def update_net_value():
    global net_value_box
    print("Updating net value...")  # Debugging line
    total_net_value = 0
    for coin, holdings_amount in crypto_data.holdings.items():
        price = prices_dict.get(coin, 0)
        if price != 0:
            total_net_value += holdings_amount * float(price)

    invested_amount = 9600
    actual_net_value = total_net_value - invested_amount
    text_color = "#32CD32" if actual_net_value >= 0 else "#FF4500"

    print(f"Total Net Value: {actual_net_value}")  # Debugging line

    # Clear and redraw the canvas
    net_value_box.delete("all")
    net_value_box.create_oval(10, 10, 200, 80, fill="darkblue", outline="darkblue", width=0)
    net_value_box.create_text(105, 30, text="NET VALUE", font=("Arial", 14, "bold"), fill="white", justify="center")
    net_value_box.create_text(105, 60, text=f"${actual_net_value:.2f}", font=("Arial", 18, "bold"), fill=text_color, justify="center")

# Call the function to fetch prices for the excluded coins when the program starts
functions.fetch_excluded_coin_prices(prices_dict, root)
# Ensure column 16 is resizable
root.grid_columnconfigure(16, weight=1, minsize=150)  # Adjust minsize if needed

# Create or update wallet labels with a default color (lightgray)
for idx, coin in enumerate(crypto_data.coins):
    # Try without the delay
    functions.load_and_update_icon(coin)

    wallet_name = crypto_data.wallet_mapping.get(coin, "NA")

    if coin not in crypto_data.wallet_labels:
        crypto_data.wallet_labels[coin] = tk.Label(root, text=wallet_name, font=("Arial", 16, "bold"), fg="black",
                                                   bg="lightgray")

    crypto_data.wallet_labels[coin].grid_forget()  # Reset grid position
    crypto_data.wallet_labels[coin].grid(row=idx + 3, column=18, padx=10, pady=4)

# Updated wallet label function:
def update_wallet_label_for_coin(coin):
    wallet_group = crypto_data.wallet_mapping.get(coin, "NA")

    # Set color based on the group
    if wallet_group == "NA":
        color = "gray"  # Default color for "NA"
    else:
        color = crypto_data.wallet_group_colors.get(wallet_group, "white")  # Fallback to white for unknown groups

    # Update wallet label text and color
    crypto_data.wallet_labels[coin].config(fg="black", bg=color, text=f"{wallet_group} Wallet")

# Call the function to create the boxes
create_value_boxes()
# Call the header creation function
create_headers()
# Call the function to set up the grid with coin labels and other elements
setup_grid()
# Start the price updates and layout adjustments
update_prices()
# Call the function to set up the exit button
setup_exit_button()
# Call the resize image function to make sure background is resized based on window size
resize_image()

root.mainloop()