**Earthquake Alert Bot**

A Discord bot that sends earthquake alerts to servers based on user-configurable filters.

**Table of Contents**

1. [Introduction](#introduction)
2. [Features](#features)
3. [Setup](#setup)
4. [Usage](#usage)
5. [Commands](#commands)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

**Introduction**

This bot uses the Discord API to send earthquake alerts to servers based on user-configurable filters. The bot uses data from a JSON feed to retrieve earthquake information and sends alerts to servers that have opted-in to receive them.

**Features**

* Send earthquake alerts to servers based on user-configurable filters
* Support for multiple filter types (e.g. magnitude, location)
* Automatic updates every 10 seconds
* Customizable alert messages and embeds

**Setup**

1. Create a new Discord bot and obtain a token
2. Install the required dependencies using `pip install -r requirements.txt`
3. Create a new file named `config.py` and add your bot token and other configuration settings
4. Run the bot using `python main.py`

**Usage**

1. Invite the bot to your server
2. Use the `!eqplace` and `!eqmag` commands to set filters for your server
3. The bot will automatically send alerts to your server when an earthquake occurs that matches your filters

**Commands**

* `!eqplace <filter>`: Set a filter for earthquake locations
* `!eqmag <filter>`: Set a filter for earthquake magnitudes
* `!update`: Update the bot's configuration and filters

**Configuration**

* `config.py`: Contains the bot's configuration settings, including the token and filter settings
* `server_config.db`: A SQLite database that stores the bot's configuration and filter settings for each server

**Troubleshooting**

* If the bot is not sending alerts, check the console output for errors
* If the bot is sending duplicate alerts, check the `server_config.db` file for duplicate entries
* If you encounter any other issues, feel free to open an issue on this repository or contact the bot's author for support.

Note: This is just a sample README file, you should adjust it to fit your specific use case and needs.
