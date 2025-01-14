import threading
# Labels for each coin (initialized later)
price_labels, balance_labels, amount_labels = {}, {}, {}
invested_labels, profit_labels, break_even_labels = {}, {}, {}
icon_labels, holdings_labels, wallet_labels = {}, {}, {}
label_labels = {}

stop_event = threading.Event()  # This event will be used to signal threads to stop

# Define the Binance API URL for fetching the price of coins
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/"
excluded_coins = ["ETI", "EGAZ", "HEX"]

coins = [
    "ETIUSDT", "EGAZUSDT", "HEXUSDT", "ETHUSDT", "BTCUSDT", "CFXUSDT",
    "GALAUSDT", "AMPUSDT", "GLMUSDT", "QTUMUSDT", "ALTUSDT", "XAIUSDT",
    "XNOUSDT", "CELRUSDT", "PONDUSDT", "AIUSDT", "VETUSDT", "ONTUSDT",
    "NEOUSDT", "NULSUSDT", "ALGOUSDT", "GRTUSDT", "LTCUSDT", "GASUSDT",
    "BNBUSDT", "ICPUSDT", "SOLUSDT", "FETUSDT", "NEARUSDT", "HBARUSDT"
]

wallet_mapping = {
    **{coin: "TREZOR" for coin in ["ETHUSDT", "AMPUSDT", "FETUSDT", "PONDUSDT", "NEARUSDT", "GRTUSDT",
                                  "GLMUSDT", "LTCUSDT", "GALAUSDT", "AIUSDT", "ALTUSDT", "BNBUSDT"]},
    **{coin: "ETICA" for coin in ["ETIUSDT", "EGAZUSDT"]},
    **{coin: "EXODUS" for coin in ["ALGOUSDT", "QTUMUSDT", "HBARUSDT"]},
    "XNOUSDT": "NAUTILUS", "ICPUSDT": "STOICWALLET",
    **{coin: "RABBY" for coin in ["CELRUSDT", "CFXUSDT", "XAIUSDT", "HEXUSDT", "VETUSDT", "ONTUSDT", "NULSUSDT"]},
    "NEOUSDT": "NEON", "GASUSDT": "NEON", "SOLUSDT": "BINANCE", "BTCUSDT": "NA"
}

wallet_group_colors = {
    "TREZOR": "green", "ETICA": "light blue", "EXODUS": "purple", "NAUTILUS": "orange",
    "STOICWALLET": "pink", "RABBY": "brown", "NEON": "cyan", "BINANCE": "red"
}

coin_id_map = {
    "ETIUSDT": "etica", "EGAZUSDT": "egaz", "HEXUSDT": "hex-pulsechain", "ETHUSDT": "ethereum", "BTCUSDT": "bitcoin",
    "CFXUSDT": "conflux-token", "GALAUSDT": "gala", "AMPUSDT": "amp-token", "GLMUSDT": "golem", "QTUMUSDT": "qtum",
    "ALTUSDT": "altlayer", "XAIUSDT": "xai-blockchain", "XNOUSDT": "nano", "CELRUSDT": "celer-network", "PONDUSDT": "marlin",
    "AIUSDT": "sleepless-ai", "VETUSDT": "vechain", "ONTUSDT": "ontology", "NEOUSDT": "neo", "NULSUSDT": "nuls",
    "ALGOUSDT": "algorand", "GRTUSDT": "the-graph", "LTCUSDT": "litecoin", "GASUSDT": "gas", "BNBUSDT": "binancecoin",
    "ICPUSDT": "internet-computer", "SOLUSDT": "solana", "FETUSDT": "fetch-ai", "NEARUSDT": "near", "HBARUSDT": "hedera-hashgraph"
}

holdings = {
    "ETIUSDT": 1680.2799, "EGAZUSDT": 24857.23, "HEXUSDT": 15696.20, "ETHUSDT": 2.01829, "BTCUSDT": 0,
    "CFXUSDT": 5471.7679, "GALAUSDT": 3761.11598, "AMPUSDT": 27985.72388, "GLMUSDT": 453.57698, "QTUMUSDT": 59.8285,
    "ALTUSDT": 1135.51000, "XAIUSDT": 549.4697, "XNOUSDT": 163.94709, "CELRUSDT": 11197.71, "PONDUSDT": 11090.34603,
    "AIUSDT": 292.41665, "VETUSDT": 1786.2001, "ONTUSDT": 356.0277, "NEOUSDT": 6, "NULSUSDT": 205.3841,
    "ALGOUSDT": 689.389, "GRTUSDT": 885.44702, "LTCUSDT": 2.29795, "GASUSDT": 1.35000, "BNBUSDT": 0.0186,
    "ICPUSDT": 17.82928, "SOLUSDT": 0.06195, "FETUSDT": 147.36293, "NEARUSDT": 33.74919, "HBARUSDT": 763.178
}

invested = {
    "ETIUSDT": 600, "EGAZUSDT": 300, "HEXUSDT": 455, "PONDUSDT": 222, "NEARUSDT": 222, "GRTUSDT": 222,
    "ALGOUSDT": 222, "CELRUSDT": 222, "CFXUSDT": 1010, "XNOUSDT": 225, "GLMUSDT": 225, "LTCUSDT": 225,
    "QTUMUSDT": 225, "ICPUSDT": 224, "GALAUSDT": 223, "HBARUSDT": 223, "AIUSDT": 224, "XAIUSDT": 224,
    "ALTUSDT": 225, "NEOUSDT": 100, "VETUSDT": 100, "ONTUSDT": 100, "NULSUSDT": 100, "BNBUSDT": 25,
    "SOLUSDT": 13, "GASUSDT": 6.5, "ETHUSDT": 3800, "AMPUSDT": 222, "FETUSDT": 222
}

# Default invested amount for coins not specified in the invested dictionary
for coin in coins:
    if coin not in invested:
        invested[coin] = 0

