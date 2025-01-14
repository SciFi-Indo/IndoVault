import tkinter as tk
import crypto_data
import requests
from PIL import Image, ImageTk
import utils


gst_price_label = None
gmt_price_label, stop_event, fetch_in_progress, scheduled_fetch, fetch_started, \
    should_stop_fetching = [None, False, False, None, False, False]

BUTTON_FONT, BUTTON_BG, BUTTON_FG, HOVER_COLOR_RED, HOVER_COLOR_BLUE, WHITE, \
    RED, DARK_RED, BACKGROUND_COLOR = ("Arial", 16, "bold"), "#00bcd4", "white", \
    "darkred", "darkblue", "white", "red", "darkred", "#2E3B4E"


def add_hover_effect(button, hover_bg, default_bg):
    button.bind("<Enter>", lambda e: button.config(bg=hover_bg))
    button.bind("<Leave>", lambda e: button.config(bg=default_bg))


def setup_gmt_price_label(root, price):
    global gmt_price_label
    if not gmt_price_label or not gmt_price_label.winfo_exists():
        gmt_price_label = tk.Label(root, text=f"GMT Price: ${price}", font=("Arial", 52, "bold"),
                                   bg="#333333", fg="white", padx=20, pady=10, relief="solid", bd=2,
                                   highlightbackground="black", highlightthickness=1)
    else:
        gmt_price_label.config(text=f"GMT Price: ${price}")
    gmt_price_label.grid(row=0, column=5, columnspan=3, padx=(0, 10), pady=10)

def setup_gst_price_label(root, price):
    global gst_price_label
    if not gst_price_label or not gst_price_label.winfo_exists():
        gst_price_label = tk.Label(root, text=f"GST Price: ${price}", font=("Arial", 52, "bold"),
                                   bg="#333333", fg="white", padx=20, pady=10, relief="solid", bd=2,
                                   highlightbackground="black", highlightthickness=1)
    else:
        gst_price_label.config(text=f"GST Price: ${price}")
    gst_price_label.grid(row=1, column=5, columnspan=3, padx=(0, 10), pady=10)


def fetch_gmt_price(root):
    global fetch_in_progress
    if fetch_in_progress:
        return
    fetch_in_progress = True
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": "GMTUSDT"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        price = response.json().get("price")
        if price is not None:
            update_gmt_price_on_ui(price, root)
    except requests.exceptions.RequestException:
        print("GMT price fetch failed")  # Simplified error message
    finally:
        fetch_in_progress = False
        root.after(10000, fetch_gmt_price, root)


def fetch_gst_price(root):
    global fetch_in_progress
    if fetch_in_progress:
        return
    fetch_in_progress = True
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "green-satoshi-token", "vs_currencies": "usd"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        price = response.json().get("green-satoshi-token", {}).get("usd")
        if price is not None:
            update_gst_price_on_ui(price, root)
    except requests.exceptions.RequestException:
        print("GST price fetch failed")  # Simpler error message
    finally:
        fetch_in_progress = False
        root.after(30000, fetch_gst_price, root)


def schedule_next_fetch(root):
    if not fetch_in_progress:
        root.after(10000, fetch_gmt_price, root)


def stop_fetching():
    global stop_event
    stop_event = True


def update_gmt_price_on_ui(price, root):
    global gmt_price_label
    if gmt_price_label is None or not gmt_price_label.winfo_exists():
        root.after(500, update_gmt_price_on_ui, price, root)
        return
    truncated_price = f"{float(price):.4f}"
    gmt_price_label.config(text=f"GMT Price: ${truncated_price}")
    root.gmt_price = float(price)


def update_gst_price_on_ui(price, root):
    global gst_price_label
    if gst_price_label is None or not gst_price_label.winfo_exists():
        root.after(500, update_gst_price_on_ui, price, root)
        return
    truncated_price = f"{float(price):.4f}"
    gst_price_label.config(text=f"GST Price: ${truncated_price}")
    root.gst_price = float(price)

    # Enable the submit button once GST price is available
    submit_button = next((w for w in root.winfo_children() if isinstance(w, tk.Button) and w.cget("text") == "Submit"), None)
    if submit_button:
        submit_button.config(state=tk.NORMAL)


def setup_blank_slate_button(root, create_value_boxes, create_net_value_box, update_prices, get_price):
    button = tk.Button(root, text="GMT MODE",
                       command=lambda: on_blank_slate_button_click(
                           root, create_value_boxes, create_net_value_box, update_prices, get_price),
                       font=("Helvetica", 32), bg=BUTTON_BG, fg=BUTTON_FG, relief="solid")
    add_hover_effect(button, HOVER_COLOR_RED, BUTTON_BG)
    button.grid(row=len(crypto_data.coins) + 3, column=6, columnspan=6, padx=10, pady=20)


def on_blank_slate_button_click(root, create_value_boxes, create_net_value_box, update_prices, get_price):
    setup_gmt_price_label(root, None)
    clear_window(root)
    configure_grid_layout(root)
    add_boxes_and_setup(root, create_value_boxes, create_net_value_box, update_prices, get_price)


def clear_window(root):
    crypto_data.stop_event.set()

    for widget in root.winfo_children():
        if widget != getattr(root, 'background_label', None):
            widget.destroy()

    update_background(root, r"assets\DSC00188.jpeg")

    fetched_gmt_price = fetch_gmt_price(root)
    setup_gmt_price_label(root, fetched_gmt_price)

    fetched_gst_price = fetch_gst_price(root)
    setup_gst_price_label(root, fetched_gst_price)

    # Call the create_input_entry_widget function here
    create_input_entry_widget(root)  # This will add the input entry widget to your window


def create_indovault_button(root, create_value_boxes, create_net_value_box, update_prices, get_price):
    bg_color = BUTTON_BG
    text_color = BUTTON_FG
    font_style = BUTTON_FONT

    box1 = tk.Button(root, text="IndoVault", font=font_style, width=15, fg=text_color,
                     bg=bg_color, bd=2, relief="solid", height=2,
                     command=lambda: on_indovault_box_click(root, create_value_boxes, create_net_value_box, update_prices, get_price))

    box1.grid(row=4, column=5, columnspan=3, padx=10, pady=10)
    add_hover_effect(box1, HOVER_COLOR_RED, BUTTON_BG)


def create_input_entry_widget(root):
    entry_label = tk.Label(root, text="Enter GST amount:", font=("Arial", 16), bg=BACKGROUND_COLOR, fg=WHITE)
    entry_label.grid(row=3, column=5, sticky="e")

    entry_widget = tk.Entry(root, font=("Arial", 16), width=20)
    entry_widget.grid(row=3, column=6)

    entry_widget.focus_set()

    # Result label with slightly darker green background
    global result_label
    result_label = tk.Label(root, text="Equivalent GMT: --\nEquivalent in USD: --", font=("Arial", 24, "bold"),
                            bg="#388E3C", fg="white", padx=20, pady=15, relief="solid", bd=2,
                            highlightbackground="black", highlightthickness=1)
    result_label.grid(row=2, column=5, columnspan=3, pady=10)

    submit_button = tk.Button(root, text="Submit", command=lambda: on_click(entry_widget, root), font=("Arial", 16), bg=BUTTON_BG, fg=BUTTON_FG)
    add_hover_effect(submit_button, HOVER_COLOR_RED, BUTTON_BG)
    submit_button.grid(row=3, column=7, sticky="w")

    # Disable the submit button initially if GST price is None
    submit_button.config(state=tk.DISABLED)

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


def rebuild_indovault(root, create_value_boxes, create_net_value_box, update_prices, get_price):
    clear_window_for_indovault(root, r"assets\DSC00188.jpeg")
    utils.setup_grid(root)
    utils.setup_exit_buttonIV(root)

    # Instantiate the HeaderCreator class and create all headers
    header_creator = utils.HeaderCreator(root, utils.header_style)
    header_creator.create_all_headers()

    setup_blank_slate_button(root, create_value_boxes, create_net_value_box, update_prices, get_price)
    stop_fetching()
    create_net_value_box()
    update_prices()
    create_value_boxes()
    for coin in crypto_data.coins:
        get_price(coin)



def on_indovault_box_click(root, create_value_boxes, create_net_value_box, update_prices, get_price):
    global should_stop_fetching
    should_stop_fetching = True
    clear_window_for_indovault(root, r"assets\DSC00188.jpeg")
    rebuild_indovault(root, create_value_boxes, create_net_value_box, update_prices, get_price)


def clear_widgets(window, widget_type=None):
    for widget in window.winfo_children():
        if widget_type is None or isinstance(widget, widget_type):
            widget.grid_forget()
            widget.pack_forget()
            widget.place_forget()


def remove_gmt_price_label(window):
    if hasattr(window, 'gmt_price_label') and window.gmt_price_label:
        try:
            window.gmt_price_label.grid_forget()
            window.gmt_price_label.destroy()
            del window.gmt_price_label
        except Exception as e:
            print(f"Error removing GMT price label: {e}")


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


def clear_window_for_indovault(root, background_image_path):
    global stop_event, fetch_in_progress
    stop_event = True
    fetch_in_progress = False

    for widget in root.winfo_children():
        if widget != getattr(root, 'background_label', None):
            widget.destroy()

    update_background(root, background_image_path)


def setup_exit_buttonGMT(root):
    exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 24, "bold"),
                            bg=RED, fg=WHITE, relief="solid", width=10, height=1)
    add_hover_effect(exit_button, DARK_RED, RED)
    exit_button.grid(row=5, column=5, columnspan=3, pady=5, padx=10)


def configure_grid_layout(root):
    for i in range(11):  # Loop to configure columns 0 to 4
        root.grid_columnconfigure(i, weight=1)

    for i in range(6):  # Loop to configure rows 0 to 4
        root.grid_rowconfigure(i, weight=1)


def add_boxes_and_setup(root, create_value_boxes, create_net_value_box, update_prices, get_price):
    create_indovault_button(root, create_value_boxes, create_net_value_box, update_prices, get_price)
    setup_exit_buttonGMT(root)

