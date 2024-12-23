IndoVault - Cryptocurrency Portfolio Tracker

IndoVault is a cryptocurrency portfolio tracker designed to help users monitor their holdings across multiple wallets. 
The app allows you to track real-time prices and manage your cryptocurrency investments by keeping tabs on net value, profit/loss, break-even prices, and more.

Key Features
Multi-wallet Support: Track your cryptocurrency holdings spread across several wallets.
Real-time Price Tracking: Fetches live coin prices from the Binance API and CoinGecko API.
Portfolio Overview:
Displays current price, amount held, balance, invested amount, profit/loss, and break-even prices for each coin.
Visual Wallet Grouping: Color-coded wallet labels help you organize and differentiate between various wallet groups.
Intuitive UI: Built with Tkinter for a dynamic, easy-to-use interface.
How It Works
IndoVault fetches real-time cryptocurrency prices through the Binance and CoinGecko APIs, providing a comprehensive overview of your holdings and portfolio. 
It calculates your net value by considering the amount you hold in each coin and its market value. 
Additionally, it calculates profit/loss based on your invested amount and displays your break-even price for each coin.

Installation
Clone the Repository
Clone the repository to your local machine:

bash
Copy code
git clone https://github.com/SciFi-Indo/IndoVault.git
Install Dependencies
Install the required Python libraries:

Copy code
pip install requests Pillow
Set Up API Access
Ensure you have access to the Binance API and CoinGecko API for fetching real-time prices.

Run the Application
Launch the app by running:

css
Copy code
python main.py
License
This project is licensed under the MIT License - see the LICENSE file for details.
