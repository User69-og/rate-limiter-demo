import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Load and prep the data
df = pd.read_csv('results.csv')
df['Time_Seconds'] = df['Timestamp'] - df['Timestamp'].min()

# Create 1-second bins for the throughput chart
df['Second'] = np.floor(df['Time_Seconds']).astype(int)
throughput = df.groupby(['Second', 'Status']).size().unstack(fill_value=0)

# Ensure both status columns exist even if one is missing in a short test
if 200 not in throughput: throughput[200] = 0
if 429 not in throughput: throughput[429] = 0

success = df[df['Status'] == 200]
blocked = df[df['Status'] == 429]

# 2. Setup the Dashboard Layout (1 row, 3 columns)
plt.style.use('seaborn-v0_8-darkgrid') # Professional styling
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Token Bucket Rate Limiter Performance Analysis', fontsize=18, fontweight='bold', y=1.05)

# --- CHART 1: Timeline (Scatter) ---
axes[0].scatter(success['Time_Seconds'], success['Status'], color='#2ca02c', label='Allowed (200)', alpha=0.7)
axes[0].scatter(blocked['Time_Seconds'], blocked['Status'], color='#d62728', label='Blocked (429)', alpha=0.5)
axes[0].set_title('Request Timeline', fontsize=14)
axes[0].set_xlabel('Time (Seconds)')
axes[0].set_ylabel('HTTP Status')
axes[0].set_yticks([200, 429])
axes[0].legend(loc='center right')

# --- CHART 2: Throughput per Second (Stacked Bar) ---
axes[1].bar(throughput.index, throughput[200], color='#2ca02c', label='Allowed (200)')
axes[1].bar(throughput.index, throughput[429], bottom=throughput[200], color='#d62728', label='Blocked (429)')
axes[1].set_title('Throughput per Second', fontsize=14)
axes[1].set_xlabel('Time Window (Second)')
axes[1].set_ylabel('Number of Requests')
axes[1].set_xticks(throughput.index)
axes[1].legend()

# --- CHART 3: Total Distribution (Pie) ---
total_allowed = len(success)
total_blocked = len(blocked)
axes[2].pie([total_allowed, total_blocked], labels=['Allowed\n(200 OK)', 'Blocked\n(429 Too Many)'], 
            colors=['#2ca02c', '#d62728'], autopct='%1.1f%%', startangle=90, explode=(0.05, 0), shadow=True)
axes[2].set_title('Total Traffic Distribution', fontsize=14)

# 3. Finalize and Save
plt.tight_layout()
plt.savefig('rate_limit_dashboard.png', dpi=300, bbox_inches='tight')
print("Upgraded dashboard generated and saved as 'rate_limit_dashboard.png'")