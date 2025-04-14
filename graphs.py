import seaborn as sns
import matplotlib.pyplot as plt

# Load the penguins dataset
penguins = sns.load_dataset('penguins')

# Histogram of flipper length
plt.figure(figsize=(10, 6))
plt.hist(penguins['flipper_length_mm'].dropna(), bins=20, color='skyblue')
plt.title('Histogram of Flipper Length')
plt.xlabel('Flipper Length (mm)')
plt.ylabel('Frequency')
plt.show()

# Box Plot of body mass by species
plt.figure(figsize=(10, 6))
sns.boxplot(x='species', y='body_mass_g', data=penguins)
plt.title('Box Plot of Body Mass by Species')
plt.xlabel('Species')
plt.ylabel('Body Mass (g)')
plt.show()

# Scatter Plot of culmen length vs culmen depth
plt.figure(figsize=(10, 6))
plt.scatter(penguins['culmen_length_mm'], penguins['culmen_depth_mm'], alpha=0.5)
plt.title('Scatter Plot of Culmen Length vs Culmen Depth')
plt.xlabel('Culmen Length (mm)')
plt.ylabel('Culmen Depth (mm)')
plt.show()

# Bar Plot of average body mass by island
plt.figure(figsize=(10, 6))
sns.barplot(x='island', y='body_mass_g', data=penguins, estimator=sum)
plt.title('Total Body Mass by Island')
plt.xlabel('Island')
plt.ylabel('Total Body Mass (g)')
plt.show()

# Violin Plot of flipper length by species
plt.figure(figsize=(10, 6))
sns.violinplot(x='species', y='flipper_length_mm', data=penguins)
plt.title('Violin Plot of Flipper Length by Species')
plt.xlabel('Species')
plt.ylabel('Flipper Length (mm)')
plt.show()

# Pair Plot of the dataset colored by species
sns.pairplot(penguins, hue='species')
plt.show()

# Heatmap of the correlation matrix
correlation = penguins.corr()
plt.figure(figsize=(10, 8))
sns.heatmap(correlation, annot=True, cmap='coolwarm', linewidths=.5)
plt.title('Heatmap of Penguins Dataset Correlation')
plt.show()