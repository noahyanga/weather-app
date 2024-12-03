"""
Module to plot weather data.
"""

import matplotlib.pyplot as plt
class PlotOperations:
    """
    Class to plot weather data.
    """
    def __init__(self, data):
        self.data = data

    def plot_boxplot(self, start_year, end_year):
        """
        Create a boxplot of mean temperatures from start_year to end_year.
        """
        # Prepare data for boxplot
        boxplot_data = {month: [] for month in range(1, 13)}
        for year in range(start_year, end_year + 1):
            if year in self.data:
                for month, temps in self.data[year].items():
                    boxplot_data[month].extend(temps)

        # Create boxplot
        plt.figure(figsize=(12, 6))
        plt.boxplot([boxplot_data[month] for month in range(1, 13)], labels=[f'{month}' for month in range(1, 13)])
        plt.title(f'Monthly Temperature Distribution for {start_year} to {end_year}')
        plt.xlabel('Month')
        plt.ylabel('Temperature (°C)')
        plt.grid(True)
        plt.show()

    def plot_lineplot(self, year, month):
        """
        Create a line plot of mean temperatures for a specific month and year.
        """
        if year in self.data and month in self.data[year]:
            days = list(range(1, len(self.data[year][month]) + 1))
            temps = self.data[year][month]

            # Create line plot
            plt.figure(figsize=(10, 9))
            plt.plot(days, temps, marker='o', linestyle='-', color='b')
            plt.scatter(days, temps, color='r')
            plt.title(f'Daily Average Temperatures {year}-{month:02}')
            plt.xlabel('Day of Month')
            plt.ylabel('Mean Temperature')
            plt.xticks(days)
            plt.grid(True)
            plt.show()
        else:
            print(f"No data available for {year}-{month:02}")

# def organize_data_for_plotting(data):
#     organized_data = {}
#     for entry in data:
#         year, month, _ = map(int, entry['date'].split('-'))
#         if year not in organized_data:
#             organized_data[year] = {}
#         if month not in organized_data[year]:
#             organized_data[year][month] = []
#         organized_data[year][month].append(entry['avg_temp'])
#     return organized_data

# # Testing plotting functions
# if __name__ == "__main__":
#     db = DBOperations()
#     all_data = db.fetch_data()
#     organized_data = organize_data_for_plotting(all_data)

# #     #plotter = PlotOperations(organized_data)
# #     #plotter.plot_boxplot(2000, 2020)
# #     #plotter.plot_lineplot(2005, 6)
