import seaborn as sns
import matplotlib.pyplot as plt

# Given data
generation_times = [28.5911, 43.3895, 85.8666, 203.0134, 292.0702, 345.3897, 351.2555, 425.9430, 471.1977, 618.8104, 653.2501, 725.4100, 946.5122, 985.4487]
merge_times = [54.5645, 271.9981, 796.4312, 3271.1274, 7305.9255, 9364.7933, 10168.6133, 13985.4473, 17998.7573, 36033.2221, 40280.3219, 49672.9035, 83279.5927, 89345.9882]
total_times = [84.6282, 319.2490, 891.2487, 3499.9316, 7647.3605, 9774.1838, 10588.3748, 14501.9894, 18582.8343, 36865.2208, 41170.7769, 50685.0497, 84705.7145, 90844.2980]

# Create a DataFrame for Seaborn
import pandas as pd
df = pd.DataFrame({'File Number': range(1, len(total_times) + 1),
                   'Generation Time': generation_times,
                   'Merge Time': merge_times,
                   'Total Time': total_times})

# Plotting
sns.set(style="whitegrid")
plt.figure(figsize=(12, 8))

# Plot bars for each time category
bar_width = 0.2
bar_positions_gen = df['File Number'] - bar_width
bar_positions_merge = df['File Number']
bar_positions_total = df['File Number'] + bar_width

plt.bar(bar_positions_gen, df['Generation Time'], width=bar_width, color='blue', label='Generation Time', alpha=0.5)
plt.bar(bar_positions_merge, df['Merge Time'], width=bar_width, color='orange', label='Merge Time', alpha=0.5)
plt.bar(bar_positions_total, df['Total Time'], width=bar_width, color='green', label='Total Time', alpha=0.5)

sns.lineplot(data=df, x='File Number', y='Generation Time', color="blue", linestyle='--')
sns.lineplot(data=df, x='File Number', y='Merge Time', color="orange", linestyle='--')
sns.lineplot(data=df, x='File Number', y='Total Time', color="green"    , linestyle='--')

plt.title('Evolution of Generation, Merge, and Total Times After Each File')
plt.xlabel('Number of Files')
plt.yscale('log')
plt.ylabel('Time (seconds)- log scaled')
plt.legend()
plt.savefig("plot_times.png")
