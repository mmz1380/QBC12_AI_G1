import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import jdatetime

# --- STEP 1: Load Data ---
try:
    df = pd.read_csv('Divar.csv', low_memory=False)
except FileNotFoundError:
    exit()

# --- STEP 2: Preprocessing ---

# A) Convert to Datetime
df['created_at_month'] = pd.to_datetime(df['created_at_month'], errors='coerce')
df = df.dropna(subset=['created_at_month'])

# B) Categorize Sales and Rentals
def categorize_market(slug):
    slug = str(slug).lower()
    if 'sell' in slug: return 'Sale'
    elif 'rent' in slug: return 'Rent'
    else: return 'Other'

df['market_type'] = df['cat2_slug'].apply(categorize_market)
df_analysis = df[df['market_type'].isin(['Sale', 'Rent'])].copy()

# C) Extract Persian Month Name
# Mapping numbers to Persian month names for a beautiful plot
persian_months_map = {
    1: 'Farvardin', 2: 'Ordibehesht', 3: 'Khordad',
    4: 'Tir', 5: 'Mordad', 6: 'Shahrivar',
    7: 'Mehr', 8: 'Aban', 9: 'Azar',
    10: 'Dey', 11: 'Bahman', 12: 'Esfand'
}

def get_persian_month(dt):
    """Converts Gregorian datetime to Persian month name."""
    try:
        # Convert to Jalali
        jalali = jdatetime.date.fromgregorian(day=dt.day, month=dt.month, year=dt.year)
        return persian_months_map.get(jalali.month)
    except:
        return None

df_analysis['persian_month'] = df_analysis['created_at_month'].apply(get_persian_month)
df_analysis = df_analysis.dropna(subset=['persian_month'])

print("Preprocessing with seasonal month extraction completed.")

# --- STEP 3: Aggregation (Merging Years) ---

# 1. First, we count ads per specific Month-Year (to get monthly counts)
df_analysis['year_month_temp'] = df_analysis['created_at_month'].dt.to_period('M')
monthly_counts = df_analysis.groupby(['year_month_temp', 'persian_month', 'market_type']).size().reset_index(name='count')

# 2. Now, we group by 'persian_month' only to merge all years together
# We take the MEAN so that the trend represents the "typical" behavior of that month
seasonal_trends = monthly_counts.groupby(['persian_month', 'market_type'])['count'].mean().reset_index()

# 3. Define the correct order for months (from Farvardin to Esfand)
month_order = list(persian_months_map.values())
seasonal_trends['persian_month'] = pd.Categorical(seasonal_trends['persian_month'], categories=month_order, ordered=True)
seasonal_trends = seasonal_trends.sort_values('persian_month')

# --- STEP 4: Visualization ---

plt.figure(figsize=(14, 7))
sns.set_style("whitegrid")

# Line plot showing the seasonal trend
sns.lineplot(
    data=seasonal_trends, 
    x='persian_month', 
    y='count', 
    hue='market_type', 
    marker='s', # Square marker
    linewidth=4,
    palette={'Sale': '#27ae60', 'Rent': '#2980b9'}
)

plt.title('Seasonal Trend Analysis: Average Monthly Volume (All Years Merged)', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Average Number of Ads', fontsize=12)
plt.xticks(rotation=45)
plt.legend(title='Market Type')

plt.tight_layout()
plt.show()

# --- STEP 5: Summary Report ---

print("SEASONAL SUMMARY (Average per Month)")

# Find the highest and lowest months for each type
for m_type in ['Sale', 'Rent']:
    type_data = seasonal_trends[seasonal_trends['market_type'] == m_type]
    if not type_data.empty:
        top_month = type_data.loc[type_data['count'].idxmax()]
        low_month = type_data.loc[type_data['count'].idxmin()]
        
        print(f"\nMarket Segment: {m_type}")
        print(f"   - Peak Month: {top_month['persian_month']} (Avg: {top_month['count']:.0f} ads)")
        print(f"   - Slowest Month: {low_month['persian_month']} (Avg: {low_month['count']:.0f} ads)")
    else:
        print(f"\nNo data found for {m_type}")
