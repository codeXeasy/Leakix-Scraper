Laravel URL Scraper
Welcome to the Laravel URL Scraper! This is a Python-based scraper designed to search for URLs based on keywords and countries, storing the results in a file while ensuring no duplicates or blacklisted domains are included.

This tool uses Selenium and ChromeDriver to interact with web pages and gather URLs, handling captchas and rate-limiting to ensure smooth operation.

Features
Keyword-based Search: Search for URLs using specified keywords and filter by countries.
Multithreaded Scraping: Efficient scraping with multiple threads to handle large datasets.
Blacklist Filtering: Avoid saving blacklisted domains.
Dynamic Handling: Capable of dealing with CAPTCHAs, rate-limiting, and IP bans.
Real-time URL Saving: Automatically saves unique URLs to a file during the scraping process.
Prerequisites
Ensure you have the following installed:

Python 3.6+
Selenium: For automating the browser and scraping data.
webdriver_manager: Automatically handles ChromeDriver installations.
colorama: For colored terminal output.
You can install the required libraries by running:

Usage
Clone the repository:
Prepare a file named country.txt with the list of countries you want to scrape.

Prepare a file containing keywords or domains you want to search for.

Run the script:

python leakix.py
The script will:

Read keywords from the specified file.
Read countries from country.txt.
Search for URLs based on the keyword and country.
Save unique, non-blacklisted URLs to leakix-new.txt.
Configuration
User-Agent Rotation: The script uses a predefined list of user agents to avoid detection and blocking.
Blacklist: Domains like twitter.com, github.com, etc., are blacklisted and not saved.
Rate Limiting: The script handles rate limits by pausing for 7 seconds if it reaches the limit.
File Structure
scraper.py: The main script responsible for scraping and saving URLs.
country.txt: A text file containing the list of countries.
leakix-new.txt: The output file where unique URLs are stored.
requirements.txt: A file containing the necessary dependencies.
Troubleshooting
Captcha Detected: If a captcha is encountered, the script will pause and prompt you to solve it manually. After solving, press Enter to continue.
Rate Limiting: The script will automatically wait if rate limits are detected to prevent blocking.
IP Bans: If an IP ban is detected, the script will suggest changing your IP address and pause for 30 seconds.

Feel free to contribute to the project or open issues if you encounter problems.

Let me know if you need any more details or further modifications!
