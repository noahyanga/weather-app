"""
Module to process weather data.
"""

import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime
from db_operations import DBOperations
from scrape_weather import WeatherScraper
from plot_operations import PlotOperations

# Configure logging
logging.basicConfig(filename='weather_processor.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class WeatherProcessor:
    """
    Class to process weather data.
    """
    def __init__(self):
        self.db = None
        self.scraper = WeatherScraper()

    def initialize_db(self):
        self.db = DBOperations()
        self.db.initialize_db()

    def download_full_data(self, start_year, start_month):
        """
        Download full weather data starting from the given year and month.
        """
        if self.db is None:
            self.initialize_db()
        self.scraper.scrape_backwards(start_year, start_month)

    def get_latest_date_from_db(self):
        """
        Get the latest date from the database. 
        """
        try:
            data = self.db.fetch_data()
            if data:
                latest_date = max(entry['date'] for entry in data)
                return latest_date
            return None
        except Exception as e:
            logging.error("Error getting latest date from database: %s", e)
            print("Error getting latest date from database. Check the log file for details.")
            return None

    def update_data(self):
        """
        Update the data in the database with the latest data.
        """
        if self.db is None:
            print("No data found in the database. Please download the full data first.")
            logging.error("Attempted to update data without downloading full data first.")
            return
        latest_date = self.get_latest_date_from_db()
        if latest_date:
            latest_year, latest_month, _ = map(int, latest_date.split('-'))
            now = datetime.now()
            if latest_year == now.year and latest_month == now.month:
                print("The data is up to date.")
                return
            self.scraper.scrape_backwards(latest_year, latest_month + 1)
        else:
            print("No data found in the database. Please download the full data first.")

    def generate_box_plot(self, start_year, end_year):
        """
        Generate a box plot for the given range of years.
        """
        if self.db is None:
            print("No data found in the database. Please download the full data first.")
            logging.error("Attempted to generate box plot without downloading full data first.")
            return
        try:
            data = self.db.fetch_data()
            weather_data = self.organize_data_for_plotting(data)
            plotter = PlotOperations(weather_data)
            plotter.plot_boxplot(start_year, end_year)
        except Exception as e:
            logging.error("Error generating box plot: %s", e)
            print("Error generating box plot. Check the log file for details.")

    def generate_line_plot(self, year, month):
        """
        Generate a line plot for the given year and month.
        """
        if self.db is None:
            print("No data found in the database. Please download the full data first.")
            logging.error("Attempted to generate line plot without downloading full data first.")
            return
        try:
            data = self.db.fetch_data()
            weather_data = self.organize_data_for_plotting(data)
            plotter = PlotOperations(weather_data)
            plotter.plot_lineplot(year, month)
        except Exception as e:
            logging.error("Error generating line plot: %s", e)
            print("Error generating line plot. Check the log file for details.")

    def organize_data_for_plotting(self, data):
        """
        Organize the data in a format suitable for plotting.
        """
        organized_data = {}
        for entry in data:
            date = entry['date']
            if date:
                try:
                    year, month, day = map(int, date.split('-'))
                    if year not in organized_data:
                        organized_data[year] = {}
                    if month not in organized_data[year]:
                        organized_data[year][month] = []
                    organized_data[year][month].append(entry['avg_temp'])
                except ValueError as e:
                    logging.error("Skipping invalid date entry: %s - Error: %s", date, e)
                    print(f"Skipping invalid date entry: {date} - Error: {e}")
            else:
                logging.error("Skipping entry with empty date: %s", entry)
                print(f"Skipping entry with empty date: {entry}")
        return organized_data

class WeatherProcessorUI:
    """
    Class to create the user interface for the weather data processor.
    """
    def __init__(self, root, processor):
        self.processor = processor
        self.root = root
        self.root.title("Weather Data Processor")

        self.create_widgets()

    def create_widgets(self):
        """
        Create the widgets for the user interface.
        """
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12))
        style.configure("TEntry", font=("Helvetica", 12))

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Title label
        self.label = ttk.Label(main_frame, text="Weather Data Processor Menu", font=("Helvetica", 16))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        # Download button
        self.download_button = ttk.Button(main_frame, text="Download Full Weather Data", command=self.download_data)
        self.download_button.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        # Update button
        self.update_button = ttk.Button(main_frame, text="Update Weather Data", command=self.update_data)
        self.update_button.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        # Box plot section
        boxplot_frame = ttk.LabelFrame(main_frame, text="Generate Box Plot", padding="10 10 10 10")
        boxplot_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        self.start_year_label = ttk.Label(boxplot_frame, text="Start Year:")
        self.start_year_label.grid(row=0, column=0, sticky="e")
        self.start_year_entry = ttk.Entry(boxplot_frame)
        self.start_year_entry.grid(row=0, column=1, sticky="w")

        self.end_year_label = ttk.Label(boxplot_frame, text="End Year:")
        self.end_year_label.grid(row=1, column=0, sticky="e")
        self.end_year_entry = ttk.Entry(boxplot_frame)
        self.end_year_entry.grid(row=1, column=1, sticky="w")

        self.boxplot_button = ttk.Button(boxplot_frame, text="Generate Box Plot", command=self.generate_box_plot)
        self.boxplot_button.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        # Line plot section
        lineplot_frame = ttk.LabelFrame(main_frame, text="Generate Line Plot", padding="10 10 10 10")
        lineplot_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        self.year_label = ttk.Label(lineplot_frame, text="Year:")
        self.year_label.grid(row=0, column=0, sticky="e")
        self.year_entry = ttk.Entry(lineplot_frame)
        self.year_entry.grid(row=0, column=1, sticky="w")

        self.month_label = ttk.Label(lineplot_frame, text="Month:")
        self.month_label.grid(row=1, column=0, sticky="e")
        self.month_entry = ttk.Entry(lineplot_frame)
        self.month_entry.grid(row=1, column=1, sticky="w")

        self.lineplot_button = ttk.Button(lineplot_frame, text="Generate Line Plot", command=self.generate_line_plot)
        self.lineplot_button.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        # Exit button
        self.exit_button = ttk.Button(main_frame, text="Exit", command=self.root.quit)
        self.exit_button.grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")

        # Configure grid to scale properly
        for i in range(6):
            main_frame.grid_rowconfigure(i, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

    def download_data(self):
        """Download full weather data."""
        try:
            now = datetime.now()
            start_year= now.year
            start_month = now.month
            self.processor.download_full_data(start_year, start_month)
        except ValueError as e:
            logging.error("Error parsing start year: %s", e)
            print("Error parsing start year. Check the log file for details.")
        except Exception as e:
            logging.error("Error downloading data: %s", e)
            print("Error downloading data. Check the log file for details.")

    def update_data(self):
        """Update the weather data."""
        try:
            self.processor.update_data()
        except Exception as e:
            logging.error("Error updating data: %s", e)
            print("Error updating data. Check the log file for details.")

    def generate_box_plot(self):
        """Generate a box plot."""
        try:
            start_year = self.validate_year(self.start_year_entry.get())
            end_year = self.validate_year(self.end_year_entry.get())
            self.processor.generate_box_plot(start_year, end_year)
        except ValueError as e:
            logging.error("Error parsing years for box plot: %s", e)
            print("Error parsing years for box plot. Check the log file for details.")
        except Exception as e:
            logging.error("Error generating box plot: %s", e)
            print("Error generating box plot. Check the log file for details.")

    def generate_line_plot(self):
        """Generate a line plot."""
        try:
            year = self.validate_year(self.year_entry.get())
            month = self.validate_month(self.month_entry.get())
            self.processor.generate_line_plot(year, month)
        except ValueError as e:
            logging.error("Error parsing year or month for line plot: %s", e)
            print("Error parsing year or month for line plot. Check the log file for details.")
        except Exception as e:
            logging.error("Error generating line plot: %s", e)
            print("Error generating line plot. Check the log file for details.")

    def validate_year(self, year_str):
        """Validate the year input."""
        if not year_str.isdigit():
            raise ValueError(f"Invalid year: {year_str}")
        year = int(year_str)
        if year < 1900 or year > datetime.now().year:
            raise ValueError(f"Year out of range: {year}")
        return year

    def validate_month(self, month_str):
        """Validate the month input."""
        if not month_str.isdigit():
            raise ValueError(f"Invalid month: {month_str}")
        month = int(month_str)
        if month < 1 or month > 12:
            raise ValueError(f"Month out of range: {month}")
        return month

if __name__ == "__main__":
    processor = WeatherProcessor()
    root = tk.Tk()
    app = WeatherProcessorUI(root, processor)
    root.mainloop()