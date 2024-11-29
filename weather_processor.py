import tkinter as tk
from tkinter import ttk
from datetime import datetime
from db_operations import DBOperations
from scrape_weather import WeatherScraper
from plot_operations import PlotOperations

class WeatherProcessor:
    def __init__(self):
        self.db = DBOperations()
        self.scraper = WeatherScraper()
        self.db.initialize_db()

    def download_full_data(self, start_year, start_month):
        self.scraper.scrape_backwards(start_year, start_month)

    def update_data(self):
        latest_date = self.get_latest_date_from_db()
        if (latest_date):
            latest_year, latest_month, _ = map(int, latest_date.split('-'))
            now = datetime.now()
            self.scraper.scrape_backwards(latest_year, latest_month + 1)
        else:
            print("No data found in the database. Please download the full data first.")

    def get_latest_date_from_db(self):
        data = self.db.fetch_data()
        if data:
            latest_date = max(entry['date'] for entry in data)
            return latest_date
        return None

    def generate_box_plot(self, start_year, end_year):
        data = self.db.fetch_data()
        weather_data = self.organize_data_for_plotting(data)
        plotter = PlotOperations(weather_data)
        plotter.plot_boxplot(start_year, end_year)

    def generate_line_plot(self, year, month):
        data = self.db.fetch_data()
        weather_data = self.organize_data_for_plotting(data)
        plotter = PlotOperations(weather_data)
        plotter.plot_lineplot(year, month)

    def organize_data_for_plotting(self, data):
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
                    print(f"Skipping invalid date entry: {date} - Error: {e}")
            else:
                print(f"Skipping entry with empty date: {entry}")
        return organized_data

class WeatherProcessorUI:
    def __init__(self, root, processor):
        self.processor = processor
        self.root = root
        self.root.title("Weather Data Processor")

        self.create_widgets()

    def create_widgets(self):
        # Create style
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
        start_year = int(self.start_year_entry.get())
        start_month = 1  # Assuming starting from January
        self.processor.download_full_data(start_year, start_month)

    def update_data(self):
        self.processor.update_data()

    def generate_box_plot(self):
        start_year = int(self.start_year_entry.get())
        end_year = int(self.end_year_entry.get())
        self.processor.generate_box_plot(start_year, end_year)

    def generate_line_plot(self):
        year = int(self.year_entry.get())
        month = int(self.month_entry.get())
        self.processor.generate_line_plot(year, month)

if __name__ == "__main__":
    processor = WeatherProcessor()
    root = tk.Tk()
    app = WeatherProcessorUI(root, processor)
    root.mainloop()