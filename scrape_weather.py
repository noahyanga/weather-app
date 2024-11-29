from html.parser import HTMLParser
import urllib.request
from datetime import datetime
from db_operations import DBOperations
from concurrent.futures import ThreadPoolExecutor, as_completed

class WeatherScraper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.weather = {}  # store the scraped weather data for the month
        self.recording_row = False
        self.recording_cell = False
        self.current_date = None
        self.current_temp = []
        self.col_index = 0
        self.year = None
        self.month = None
        self.tr_found = False  # detect if there are any <tr> tags
        self.has_previous_month = False  # check for the "Previous Month" link

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':  # Start of a table row
            self.recording_row = True
            self.current_date = None
            self.current_temp = []
            self.col_index = 0
            self.tr_found = True  # Found a <tr> tag, set the flag to True
        elif tag == 'td' and self.recording_row: 
            self.recording_cell = True
            self.col_index += 1
        elif tag == 'th' and self.recording_row and self.col_index == 0:  # Date column
            self.recording_cell = True
        elif tag == 'ul' and ('pager' in str(attrs) or 'pagination' in str(attrs)):
            # Look for the 'Previous Month' link
            for attr in attrs:
                if 'Previous Month' in str(attr):
                    self.has_previous_month = True

    def handle_data(self, data):
        if self.recording_row and self.recording_cell:
            clean_data = data.strip()

            # skip rows with these values
            if clean_data in ["Sum", "Avg", "Xtrm"]:
                self.recording_row = False
                return

            try:
                if self.col_index == 0 and not self.current_date:
                    # Ensure the date is correctly formatted
                    day = int(clean_data)
                    self.current_date = f"{self.year}-{self.month:02}-{day:02}"
                elif self.col_index in [1, 2, 3]:
                    self.current_temp.append(float(clean_data))
            except ValueError:
                self.current_temp.append(None) # missing or invalid data

    def handle_endtag(self, tag):
        if tag == 'td' or tag == 'th':
            self.recording_cell = False
        elif tag == 'tr':  # End of row
            if self.current_date and len(self.current_temp) == 3:
                self.weather[self.current_date] = {
                    "Max": self.current_temp[0],
                    "Min": self.current_temp[1],
                    "Mean": self.current_temp[2],
                }
            self.recording_row = False

    def scrape_all_days(self, year, month):
        """Scrape data for all days in a specific month."""
        weather = {}  # Clear previous month's data
        self.year = year
        self.month = month
        url = f"http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&Year={year}&Month={month}"
        print(f"Scraping data for {year}-{month:02}...")
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read().decode('utf-8')

            # Check if there is a link to the "Previous Month" page
            if 'Previous Month' not in html:
                self.has_previous_month = False
                print(f"No 'Previous Month' link found for {year}-{month:02}. No more data to scrape.")
            else:
                self.has_previous_month = True

            self.feed(html)

            # Copy the scraped data to the local dictionary
            weather.update(self.weather)
            self.weather.clear()  # Clear the shared dictionary for the next use

            # Return all days of scraped data in dictionary format
            return weather

        except Exception as e:
            print(f"Error fetching data for {year}-{month:02}: {e}")
            return {}

    def scrape_backwards(self, start_year, start_month):
        """
        Scrapes data backwards from the current date.
        """
        current_month = start_month
        current_year = start_year
        db = DBOperations()
        tasks = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            while True:
                # Check if the date is earlier than the earliest available data
                if current_year < 1996 or (current_year == 1996 and current_month < 9):
                    print("No more data available. Earliest date reached.")
                    break

                tasks.append(executor.submit(self.scrape_and_save, current_year, current_month, db))

                # Move to the previous month
                current_month -= 1
                if current_month == 0:
                    current_month = 12
                    current_year -= 1

            for task in as_completed(tasks):
                task.result()

    def scrape_and_save(self, year, month, db):
        scraped_weather = self.scrape_all_days(year, month)

        # Check if data is available
        if scraped_weather:
            print(f"\nScraped Weather Data for {year}-{month:02}:")
            for date, temps in scraped_weather.items():
                print(f"Day: {date} -> Max: {temps['Max']}, Min: {temps['Min']}, Mean: {temps['Mean']}°C")
            print(f"Total days scraped for {year}-{month:02}: {len(scraped_weather)}\n")

            # Save the scraped data to the database
            db.save_data(scraped_weather)
        else:
            print(f"No data available for {year}-{month:02}. Moving to the next month.")

if __name__ == "__main__":
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # Testing to see auto stopping of no more data (not working yet)
    scraper = WeatherScraper()
    scraper.scrape_backwards(current_year, current_month)