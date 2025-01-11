IndoVault - Cryptocurrency Portfolio Tracker
IndoVault is a cryptocurrency portfolio tracker designed to help users monitor their holdings across multiple wallets.
The app allows you to track real-time prices and manage your cryptocurrency investments by keeping tabs on net value, profit/loss, break-even prices, and more.

Key Features
Multi-Wallet Support: Track your cryptocurrency holdings across several wallets.
Real-Time Price Tracking: Fetch live coin prices from the Binance API and CoinGecko API.
Portfolio Overview: Displays current price, amount held, balance, invested amount, profit/loss, and break-even prices for each coin.
Visual Wallet Grouping: Color-coded wallet labels help you organize and differentiate between various wallet groups.
Intuitive UI: Built with Tkinter for a dynamic, easy-to-use interface.

How It Works
IndoVault fetches real-time cryptocurrency prices through the Binance and CoinGecko APIs, providing a comprehensive overview of your holdings and portfolio.
It calculates your net value based on the amount held in each coin and its market value. Additionally, it calculates profit/loss and displays your break-even price for each coin.

Installation
Clone the Repository
Clone the repository to your local machine:

bash
Copy code
git clone https://github.com/SciFi-Indo/IndoVault.git
Install Dependencies
Install the required Python libraries:

bash
Copy code
pip install requests Pillow
Coin Icons
The app uses coin icons for visual representation of each cryptocurrency.
Make sure the coin icons are placed in a folder named coin_icons in the same directory as your main.py file.
You can download the icons from the coin_icons folder in this repository.

Run the Application
Launch the app by running:

bash
Copy code
python main.py
License
This project is licensed under the MIT License - see the LICENSE file for details.
