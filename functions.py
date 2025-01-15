import os, requests, threading
from PIL import Image, ImageTk
import crypto_data


class CryptoTracker:
    def __init__(self, root):
        self.root = root
        self.sorted_once = False
        self.fetch_in_progress = False

    def brighten_color(self, hex_color, factor=1.5):
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i + 2], 16) for i in range(0, 6, 2)]
        r, g, b = [min(255, int(c * factor)) for c in (r, g, b)]
        return f'#{r:02x}{g:02x}{b:02x}'

    def fetch_excluded_coin_prices(self, prices_dict):
        for excluded_coin_name in crypto_data.excluded_coins:
            coin_id = crypto_data.coin_id_map.get(f"{excluded_coin_name}USDT")
            if coin_id:
                try:
                    response = requests.get(f"{crypto_data.COINGECKO_API_URL}{coin_id}", timeout=10)
                    response.raise_for_status()
                    coin_data = response.json()
                    price = coin_data.get('market_data', {}).get('current_price', {}).get('usd')
                    if price:
                        prices_dict[f"{excluded_coin_name}USDT"] = str(price)
                except requests.exceptions.RequestException:
                    pass

    def sort_prices(self, prices_dict, update_wallet_label_for_coin, update_icon_for_coin, update_net_value):
        if self.sorted_once:
            return

        self.sorted_once = True

        def sort_worker():
            if crypto_data.stop_event.is_set():
                return

            sorted_coins = self.sort_coins_by_balance(prices_dict)
            self.root.after(0, self.hide_labels)
            self.root.after(0, self.regrid_labels, sorted_coins, update_wallet_label_for_coin, update_icon_for_coin)
            self.root.after(0, update_net_value)

        thread = threading.Thread(target=sort_worker)
        crypto_data.active_threads.append(thread)
        thread.start()

    def sort_coins_by_balance(self, prices_dict):
        return sorted(
            crypto_data.holdings.items(),
            key=lambda x: (crypto_data.holdings[x[0]] * float(prices_dict.get(x[0], 0)) - crypto_data.invested[x[0]]),
            reverse=True
        )

    def hide_labels(self):
        for coin in crypto_data.coins:
            for label in [crypto_data.wallet_labels, crypto_data.label_labels, crypto_data.price_labels,
                          crypto_data.amount_labels, crypto_data.balance_labels, crypto_data.invested_labels,
                          crypto_data.profit_labels, crypto_data.break_even_labels, crypto_data.icon_labels]:
                label[coin].grid_forget()

    def regrid_labels(self, sorted_coins, update_wallet_label_for_coin, update_icon_for_coin):
        for idx, (coin, _) in enumerate(sorted_coins):
            row_idx = idx + 3
            update_icon_for_coin(coin)
            update_wallet_label_for_coin(coin)
            self.grid_labels_for_coin(coin, row_idx)

    def grid_labels_for_coin(self, coin, row_idx):
        grid_data = [
            (crypto_data.icon_labels, 1), (crypto_data.label_labels, 0),
            (crypto_data.price_labels, 2), (crypto_data.amount_labels, 12),
            (crypto_data.balance_labels, 6), (crypto_data.invested_labels, 8),
            (crypto_data.profit_labels, 10), (crypto_data.break_even_labels, 4),
            (crypto_data.wallet_labels, 18)
        ]

        for label, col, *sticky in grid_data:
            label[coin].grid(row=row_idx, column=col, padx=10, pady=4, sticky=sticky[0] if sticky else "")

    def load_and_update_icon(self, coin: str):
        coin_name = crypto_data.coin_id_map.get(coin, "default")
        icon_path = os.path.join("assets", "coin_icons", f"{coin_name}.png")
        img = Image.open(icon_path).resize((30, 30))
        icon_tk = ImageTk.PhotoImage(img)

        if coin in crypto_data.icon_labels:
            crypto_data.icon_labels[coin].config(image=icon_tk)
            crypto_data.icon_labels[coin].image = icon_tk