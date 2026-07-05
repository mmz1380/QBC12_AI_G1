import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import jdatetime  # Required for Persian date conversion

# --- STEP 1: Load Data ---
try:
    df = pd.read_csv('Divar.csv', low_memory=False)
except FileNotFoundError:
    exit()

# --- STEP 2: Preprocessing ---

# A) Convert string column to actual Datetime format (Gregorian)
df['created_at_month'] = pd.to_datetime(df['created_at_month'], errors='coerce')
df = df.dropna(subset=['created_at_month'])

# B) Categorize Sales and Rentals based on cat2_slug
def categorize_market(slug):
    slug = str(slug).lower()
    if 'sell' in slug:
        return 'Sale'
    elif 'rent' in slug:
        return 'Rent'
    else:
        return 'Other'

df['market_type'] = df['cat2_slug'].apply(categorize_market)
df_analysis = df[df['market_type'].isin(['Sale', 'Rent'])].copy()

# C) Conversion to Persian (Jalali) Date
# This is the crucial part to meet your request
def convert_to_persian_period(dt):
    """Converts a datetime object to a 'YYYY-MM' Persian string."""
    try:
        # Convert Gregorian to Jalali
        jalali_date = jdatetime.date.fromgregorian(day=dt.day, month=dt.month, year=dt.year)
        # Return in YYYY-MM format
        return f"{jalali_date.year}-{jalali_date.month:02d}"
    except:
        return None

# Apply the conversion
df_analysis['persian_period'] = df_analysis['created_at_month'].apply(convert_to_persian_period)

# Remove any rows that failed conversion
df_analysis = df_analysis.dropna(subset=['persian_period'])

print("Preprocessing with Persian date conversion completed.")

# --- STEP 3: Aggregation ---

# Group by the new Persian period column
monthly_trends = df_analysis.groupby(['persian_period', 'market_type']).size().reset_index(name='ad_count')

# IMPORTANT: Since Persian periods are strings, we must sort them carefully.
# We'll sort by the original datetime to ensure the line plot is chronological.
# First, we create a temporary sorting column
sort_map = df_analysis[['created_at_month', 'persian_period']].drop_duplicates().sort_values('created_at_month')
period_order = sort_map['persian_period'].tolist()

# Reindex/Sort monthly_trends using the correct chronological order
monthly_trends['persian_period'] = pd.Categorical(monthly_trends['persian_period'], categories=period_order, ordered=True)
monthly_trends = monthly_trends.sort_values(['persian_period', 'market_type'])
monthly_trends['ad_count'] = monthly_trends['ad_count'].apply(lambda x: np.log10(x+1))

# --- STEP 4: Visualization ---

plt.figure(figsize=(15, 7))
sns.set_style("whitegrid")

# Plotting using Persian periods on X-axis
line_plot = sns.lineplot(
    data=monthly_trends, 
    x='persian_period', 
    y='ad_count', 
    hue='market_type', 
    marker='o', 
    linewidth=3,
    palette={'Sale': '#27ae60', 'Rent': '#2980b9'}
)

plt.title('Monthly Trend Analysis (Persian Calendar): Sales vs Rentals', fontsize=18, fontweight='bold', pad=20)
plt.xlabel('Month (Jalali Year-Month)', fontsize=14)
plt.ylabel('Number of Advertisements - log10(y+1)', fontsize=14)
plt.xticks(rotation=45)
plt.legend(title='Market Type', fontsize=12)
plt.grid(True, which='both', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

# --- STEP 5: Statistical Insight (Spike Detection) ---

print("DETAILED ANALYSIS REPORT (JALALI)")

for m_type in ['Sale', 'Rent']:
    type_data = monthly_trends[monthly_trends['market_type'] == m_type]
    if not type_data.empty:
        max_row = type_data.loc[type_data['ad_count'].idxmax()]
        avg_count = type_data['ad_count'].mean()
        
        print(f"\nMarket Segment: {m_type}")
        print(f"   - Peak Month (Persian): {max_row['persian_period']} ({max_row['ad_count']:,} ads)")
        print(f"   - Average Monthly Volume: {avg_count:,.0f}")
        
        if max_row['ad_count'] > avg_count * 1.5:
            print(f"   - ALERT: Significant spike detected in {max_row['persian_period']}!")
        else:
            print(f"   - Trend: Relatively stable.")
    else:
        print(f"\n No data found for {m_type}")
