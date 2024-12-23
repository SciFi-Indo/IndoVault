import tkinter as tk
import requests
import crypto_data
import functions
import time
from PIL import Image, ImageTk

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
                crypto_data.price_labels[coin].config(text=f"${price}", fg="green")
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
            # Directly call sort_prices without lambda
            functions.sort_prices(
                prices_dict,
                functions.load_and_update_icon,  # Correct reference to the function
                update_wallet_label_for_coin,
                functions.load_and_update_icon,
                update_net_value,
                root,
                label_style
            )

        root.after(300000, update_prices)  # Ensure it keeps updating every minute
        return

    coin = crypto_data.coins[idx]
    price = get_price(coin)
    prices_dict[coin] = price
    crypto_data.price_labels[coin].config(text="Loading...", fg="red")

    root.after(300, update_price_for_coin, coin, price, idx)
    time.sleep(0.1)  # Add a small delay to spread out the load

# Function to update the price, balance, and change the text color to green
def update_price_for_coin(coin, price, idx):
    crypto_data.price_labels[coin].config(text=f"${price}", fg="green")
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
        crypto_data.profit_labels[coin].config(text=f"${profit:.2f}", fg="green", font=("Arial", 16, "bold"))
    else:
        crypto_data.profit_labels[coin].config(text=f"${profit:.2f}", fg="red", font=("Arial", 16))

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
            crypto_data.break_even_labels[coin].config(text=f"${break_even_price_formatted}",
                                           fg="green")  # Green if above or equal to break-even
        else:
            crypto_data.break_even_labels[coin].config(text=f"${break_even_price_formatted}", fg="red")
    else:
        # Display 5 decimal places for break-even price when current price is not available
        break_even_price_formatted = f"{break_even_price:.5f}"
        crypto_data.break_even_labels[coin].config(text=f"${break_even_price_formatted}",
                                       fg="yellow")  # Default color (yellow) if price is not available

# Function to exit the program
def exit_program(event=None):
    root.quit()

# Update the net value box
def update_net_value():
    total_net_value = 0
    for coin, holdings_amount in crypto_data.holdings.items():
        price = prices_dict.get(coin, 0)
        if price != 0:
            total_net_value += holdings_amount * float(price)

    invested_amount = 9600
    actual_net_value = total_net_value - invested_amount
    text_color = "#32CD32" if actual_net_value >= 0 else "#FF4500"
    # Clear the existing text and redraw the oval
    net_value_box.delete("all")
    net_value_box.create_oval(10, 10, 200, 80, fill="darkblue", outline="darkblue", width=0)
    net_value_box.create_text(105, 30, text="NET VALUE", font=("Arial", 14, "bold"), fill="white", justify="center")
    net_value_box.create_text(105, 60, text=f"${actual_net_value:.2f}", font=("Arial", 18, "bold"), fill=text_color,
                              justify="center")

# Set up the GUI window
root = tk.Tk()
root.title("IndoVault - Cryptocurrency Tracker")
root.configure(bg="black")
root.attributes('-fullscreen', True)


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
        crypto_data.wallet_labels[coin] = tk.Label(root, text=wallet_name, font=("Arial", 16), fg="black", bg="lightgray")

    crypto_data.wallet_labels[coin].grid_forget()  # Reset grid position
    crypto_data.wallet_labels[coin].grid(row=idx + 3, column=16, padx=10, pady=4, sticky="e")

# Updating wallet label color and group
def update_wallet_label_for_coin(coin):
    wallet_group = crypto_data.wallet_mapping.get(coin, "NA")
    wallet_color = crypto_data.wallet_group_colors.get(wallet_group, "white")  # Default to white if group is not found
    crypto_data.wallet_labels[coin].config(text=wallet_group, fg="black", bg=wallet_color)

# Styling and padding values
header_style = {"font": ("Arial", 20, "bold"), "fill": "white"}
label_style = {"font": ("Arial", 16, "bold"), "fg": "purple", "bg": "black"}
price_style = {"font": ("Arial", 16, "bold"), "fg": "red", "bg": "black"}
amount_style = {"font": ("Arial", 16), "fg": "green", "bg": "black"}
balance_style = {"font": ("Arial", 16), "fg": "purple", "bg": "black"}
invested_style = {"font": ("Arial", 16), "fg": "purple", "bg": "black"}
profit_style = {"font": ("Arial", 16), "fg": "green", "bg": "black"}
break_even_style = {"font": ("Arial", 16), "fg": "yellow", "bg": "black"}

# Foreground image setup (image will be on top of the grid but transparent)
image_path = r"C:\Users\lette\PycharmProjects\IndoVault\DSC00188.jpeg"
image = Image.open(image_path)

if image.mode != "RGBA":
    image = image.convert("RGBA")

def resize_image():
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    image_resized = image.resize((window_width, window_height), Image.Resampling.LANCZOS)
    background_photo = ImageTk.PhotoImage(image_resized)
    background_label.config(image=background_photo)
    background_label.image = background_photo

# Create a Label to hold the image and place it in the window (foreground layer)
background_label = tk.Label(root)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
background_label.lift()
root.update_idletasks()
root.after(100, resize_image)

# Create headers for each column with rounded blue boxes and white text
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
header_holdings.grid(row=2, column=12, padx=10, pady=(10, 5))  # Swap columns (12 -> 4)

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
header_break_even.grid(row=2, column=4, padx=10, pady=(10, 5))  # Swap columns (4 -> 12)

# Create the wallet header and move it to the farthest right column
header_wallet = tk.Canvas(root, width=200, height=60, bg="black", bd=0, highlightthickness=0)
header_wallet.create_oval(5, 5, 195, 55, fill="blue", outline="blue", width=0)
header_wallet.create_text(100, 30, text="WALLET", **header_style)
header_wallet.grid(row=2, column=16, padx=10, pady=(10, 5), sticky="e")  # Place in column 16 (farthest right)

# Adjusted net_value_box to fix large black box issue
net_value_box = tk.Canvas(root, width=220, height=90, bg="black", bd=0, highlightthickness=0)
net_value_box.create_oval(10, 10, 210, 80, fill="darkblue", outline="darkblue", width=0)
net_value_box.create_text(110, 30, text="NET VALUE", font=("Arial", 14, "bold"), fill="white", justify="center")
net_value_box.create_text(110, 60, text="$0.00", font=("Arial", 18, "bold"), fill="green", justify="center")
net_value_box.grid(row=len(crypto_data.coins) + 3, column=0, columnspan=5, pady=20)

# Adjusted deposited_box to fix large black box issue
deposited_box = tk.Canvas(root, width=220, height=90, bg="black", bd=0, highlightthickness=0)
deposited_box.create_oval(10, 10, 210, 80, fill="darkblue", outline="darkblue", width=0)
deposited_box.create_text(110, 30, text="DEPOSITED", font=("Arial", 14, "bold"), fill="white", justify="center")
deposited_box.create_text(110, 60, text="$9160", font=("Arial", 18, "bold"), fill="red", justify="center")
deposited_box.grid(row=len(crypto_data.coins) + 3, column=12, columnspan=2, padx=10, pady=20)

exit_button = tk.Button(root, text="Exit", command=exit_program, font=("Arial", 20, "bold"), bg="red", fg="white", relief="solid")
exit_button.grid(row=len(crypto_data.coins) + 3, column=5, columnspan=5, padx=10, pady=20)

# Hover effect for "Exit" button
def on_enter(e):
    exit_button.config(bg="darkred")

def on_leave(e):
    exit_button.config(bg="red")

exit_button.bind("<Enter>", on_enter)
exit_button.bind("<Leave>", on_leave)

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
    crypto_data.wallet_labels[coin] = tk.Label(root, text=wallet_name, font=("Arial", 16), fg="black", bg="red")
    crypto_data.wallet_labels[coin].grid(row=idx + 3, column=16, padx=10, pady=4, sticky="e")


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


# Start the price updates and layout adjustments
update_prices()

root.mainloop()
