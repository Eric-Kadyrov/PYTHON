
import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = 'path_to_your_csv_file.csv'
data = pd.read_csv(file_path, index_col='Quarters')

# Converting the index to datetime for easier processing
data.index = pd.to_datetime(data.index)

# Assuming specific rows correspond to Revenue, Cost, and EBIT
# Replace 'Your_Revenue_Row', 'Your_Cost_Row', and 'Your_EBIT_Row' with the actual row names
revenue = data.loc['Your_Revenue_Row']
costs = data.loc['Your_Cost_Row']
ebit = data.loc['Your_EBIT_Row']

# Group by year and calculate average and standard deviation
yearly_stats = data.groupby(data.index.year).agg(['mean', 'std'])

average_revenue = yearly_stats.loc['Your_Revenue_Row', 'mean']
std_dev_revenue = yearly_stats.loc['Your_Revenue_Row', 'std']
average_costs = yearly_stats.loc['Your_Cost_Row', 'mean']
std_dev_costs = yearly_stats.loc['Your_Cost_Row', 'std']
average_ebit = yearly_stats.loc['Your_EBIT_Row', 'mean']
std_dev_ebit = yearly_stats.loc['Your_EBIT_Row', 'std']

# Plotting Cost Structure
plt.figure(figsize=(10, 6))
costs.plot(kind='bar')
plt.title('Cost Structure per Quarter')
plt.ylabel('Costs')
plt.xlabel('Quarters')

# Plotting Revenue Structure
plt.figure(figsize=(10, 6))
revenue.plot(kind='bar', color='green')
plt.title('Revenue Structure per Quarter')
plt.ylabel('Revenue')
plt.xlabel('Quarters')

# Plotting Revenue and EBIT vs Year
plt.figure(figsize=(10, 6))
plt.plot(revenue, label='Revenue', color='green')
plt.plot(ebit, label='EBIT', color='blue')
plt.title('Revenue and EBIT per Quarter')
plt.ylabel('Amount')
plt.xlabel('Quarters')
plt.legend()

plt.show()
