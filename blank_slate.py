import tkinter as tk
import crypto_data
import requests
from PIL import Image, ImageTk


gst_price_label = None
gmt_price_label = None

BUTTON_FONT, BUTTON_BG, BUTTON_FG, HOVER_COLOR_RED, HOVER_COLOR_BLUE, WHITE, \
    RED, DARK_RED, BACKGROUND_COLOR = ("Arial", 16, "bold"), "#00bcd4", "white", \
    "darkred", "darkblue", "white", "red", "darkred", "#2E3B4E"

def configure_grid_layout(root):
    # Adjust column weights to ensure centering of content
    for i in range(11):  # Loop to configure columns 0 to 10
        root.grid_columnconfigure(i, weight=1, minsize=100)  # Set minimum size to ensure proper distribution

    for i in range(6):  # Loop to configure rows 0 to 5
        root.grid_rowconfigure(i, weight=1, minsize=50)


def add_hover_effect(button, hover_bg, default_bg):
    button.bind("<Enter>", lambda e: button.config(bg=hover_bg))
    button.bind("<Leave>", lambda e: button.config(bg=default_bg))


def setup_gmt_price_label(root, price):
    global gmt_price_label
    if gmt_price_label is None or not gmt_price_label.winfo_exists():
        gmt_price_label = tk.Label(root, text=f"GMT Price: ${price}", font=("Arial", 52, "bold"),
                                   bg="#333333", fg="#D66DE1", padx=20, pady=10, relief="solid", bd=2,
                                   highlightbackground="black", highlightthickness=1)
    else:
        gmt_price_label.config(text=f"GMT Price: ${price}")
    gmt_price_label.grid(row=0, column=5, columnspan=3, padx=(0, 10), pady=10)


def setup_gst_price_label(root, price):
    global gst_price_label
    if gst_price_label is None or not gst_price_label.winfo_exists():
        gst_price_label = tk.Label(root, text=f"GST Price: ${price}", font=("Arial", 52, "bold"),
                                   bg="#333333", fg="#D66DE1", padx=20, pady=10, relief="solid", bd=2,
                                   highlightbackground="black", highlightthickness=1)
    else:
        gst_price_label.config(text=f"GST Price: ${price}")
    gst_price_label.grid(row=1, column=5, columnspan=3, padx=(0, 10), pady=10)


def fetch_gmt_price(root):
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": "GMTUSDT"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        price = response.json().get("price")
        if price is not None:
            update_gmt_price_on_ui(price, root)
    except requests.exceptions.RequestException:
        print("GMT price fetch failed")

    root.after(10000, fetch_gmt_price, root)


def fetch_gst_price(root):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "green-satoshi-token", "vs_currencies": "usd"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        price = response.json().get("green-satoshi-token", {}).get("usd")
        if price is not None:
            update_gst_price_on_ui(price, root)
    except requests.exceptions.RequestException:
        print("GST price fetch failed")

    root.after(30000, fetch_gst_price, root)


def update_gmt_price_on_ui(price, root):
    global gmt_price_label
    if gmt_price_label and gmt_price_label.winfo_exists():
        truncated_price = f"{float(price):.4f}"
        gmt_price_label.config(text=f"GMT Price: ${truncated_price}")
        root.gmt_price = float(price)

def update_gst_price_on_ui(price, root):
    global gst_price_label
    if gst_price_label and gst_price_label.winfo_exists():
        truncated_price = f"{float(price):.4f}"
        gst_price_label.config(text=f"GST Price: ${truncated_price}")
        root.gst_price = float(price)

        submit_button = next((w for w in root.winfo_children() if isinstance(w, tk.Button) and w.cget("text") == "Submit"), None)
        if submit_button:
            submit_button.config(state=tk.NORMAL)


def setup_blank_slate_button(root):
    button = tk.Button(root, text="GMT MODE",
                       command=lambda: on_blank_slate_button_click(root),
                       font=("Helvetica", 32), bg=BUTTON_BG, fg=BUTTON_FG, relief="solid")
    add_hover_effect(button, HOVER_COLOR_RED, BUTTON_BG)
    button.grid(row=len(crypto_data.coins) + 3, column=6, columnspan=6, padx=10, pady=20)


def on_blank_slate_button_click(root):
    # Stop any active threads immediately
    crypto_data.stop_event.set()

    # Check if all threads are done
    if all(not thread.is_alive() for thread in crypto_data.active_threads):
        clear_window_build_gmt_mode(root)
        configure_grid_layout(root)
    else:
        # If threads are still active, check again in 100ms
        root.after(100, on_blank_slate_button_click, root)


def clear_window_build_gmt_mode(root):
    if all(not thread.is_alive() for thread in crypto_data.active_threads):
        # Clear existing widgets except the background label
        for widget in root.winfo_children():
            if widget != getattr(root, 'background_label', None):
                widget.destroy()

        # Update UI with the new GMT mode content
        update_background(root, r"assets\DSC00199.jpeg")
        setup_gmt_price_label(root, fetch_gmt_price(root))
        setup_gst_price_label(root, fetch_gst_price(root))
        create_input_entry_widget(root)
        create_indovault_button(root)
        setup_exit_buttonGMT(root)
    else:
        # If threads are still active, check again in 100ms
        root.after(100, clear_window_build_gmt_mode, root)


def create_indovault_button(root):
    button = tk.Button(root, text="IndoVault", font=BUTTON_FONT, width=15, fg=BUTTON_FG, bg=BUTTON_BG, bd=2, relief="solid", height=2)
    button.grid(row=4, column=5, columnspan=3, padx=10, pady=10)
    add_hover_effect(button, HOVER_COLOR_RED, BUTTON_BG)


def create_input_entry_widget(root):
    # Create the "Enter GST amount" label to look like the Submit button
    entry_label = tk.Label(root, text="Enter GST amount:", font=("Arial", 24, "bold"), bg="#FFA500", fg="white",
                           width=20, height=1, relief="solid", padx=10, pady=10, anchor="center")
    entry_label.grid(row=3, column=5, columnspan=1, sticky="e", padx=(0, 10))  # Slight adjustment for spacing

    entry_widget = tk.Entry(root, font=("Arial", 16), width=20)
    entry_widget.grid(row=3, column=6, columnspan=1)  # Centered in the middle column

    entry_widget.focus_set()

    global result_label
    result_label = tk.Label(root, text="Equivalent GMT: --\nEquivalent in USD: --", font=("Arial", 24, "bold"),
                            bg="#388E3C", fg="white", padx=20, pady=15, relief="solid", bd=2,
                            highlightbackground="black", highlightthickness=1)
    result_label.grid(row=2, column=5, columnspan=3, pady=10)

    # Create the submit button with white font and orange background
    submit_button = tk.Button(root, text="Submit", command=lambda: on_click(entry_widget, root),
                              font=("Arial", 24, "bold"), bg="#FFA500", fg="white", width=20, relief="solid",
                              highlightbackground="black", highlightcolor="black")

    add_hover_effect(submit_button, HOVER_COLOR_RED, "#FFA500")  # Hover effect for background color
    submit_button.grid(row=3, column=7, columnspan=2, sticky="w", padx=(10, 0))  # Adjust for proper alignment

    submit_button.config(state=tk.NORMAL)  # Enable the button again for testing purposes

    def refocus_entry(event):
        entry_widget.focus_set()

    entry_widget.bind("<FocusIn>", refocus_entry)


def on_click(entry_widget, root):
    user_input = entry_widget.get()
    try:
        gst_amount = float(user_input)

        gst_price = root.gst_price
        gmt_price = root.gmt_price

        if gst_price is None or gmt_price is None:
            print("Error: Prices are not available.")
            return

        gmt_value = (gst_amount * gst_price) / gmt_price

        result_label.config(text=f"Equivalent GMT: {gmt_value:.4f} GMT\nEquivalent in USD: ${(gmt_value * gmt_price):.2f}")

    except ValueError:
        print("Invalid input, please enter a valid number.")


def update_background(window, image_path):
    if not hasattr(window, 'background_label'):
        window.background_label = tk.Label(window)
        window.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        window.background_label.lift()

    try:
        image = Image.open(image_path).convert("RGBA")
        image_resized = image.resize((window.winfo_width(), window.winfo_height()), Image.Resampling.LANCZOS)
        background_photo = ImageTk.PhotoImage(image_resized)

        window.background_label.config(image=background_photo)
        window.background_label.image = background_photo
    except Exception as e:
        print(f"Error updating background image: {e}")


def setup_exit_buttonGMT(root):
    exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 24, "bold"),
                            bg=RED, fg=WHITE, relief="solid", width=10, height=1)
    add_hover_effect(exit_button, DARK_RED, RED)
    exit_button.grid(row=5, column=5, columnspan=3, pady=5, padx=10)

