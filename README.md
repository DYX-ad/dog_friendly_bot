## Dog-Friendly Places Bot 🐾

Hi! This is my Telegram bot that helps dog owners find friendly places like parks, cafes, or shops where dogs are welcome.
🐕 It's a **demo version**, created for testing and feedback.
📍 In the future, I plan to integrate it with **Google Maps** for better location-based search and recommendations.
Feel free to test it and share your thoughts!



## Installation

Follow the instructions below to install and run the project:
Prerequisites

Make sure you have Python 3.7 or higher installed on your machine. If not, download and install it from python.org.
Step-by-Step Installation

Clone the repository:

Create and activate a virtual environment:

For Linux/macOS:

           python3 -m venv .venv
           source .venv/bin/activate

For Windows:

          python -m venv .venv
          .venv\Scripts\activate

Install the dependencies:

          pip install -r requirements.txt

Set up your configuration:

Make sure to add your own API token and any required configuration to the config.py file or environment variables.

Run the bot:

          python bot.py

The bot will now be running and should respond to the user in Telegram.



## Technologies Used

Programming Language: Python 3.x

Frameworks & Libraries:

  python-telegram-bot: A Python wrapper for the Telegram Bot API to create and manage the bot.

  SQLAlchemy: A SQL toolkit for Python, used to interact with the database and manage user data.

  Nest Asyncio: A library that allows asyncio to work in environments where there is already a running event loop (like in some web servers).

  Requests: A simple HTTP library used to make requests to external APIs (for fetching nearby places from OpenStreetMap).

Database: PostgreSQL (for storing user data)

API: Overpass API (for querying OpenStreetMap data about nearby cafes, hotels, and pet shops)

## Developed by

  Andrey
        
        /DYX-ad/
