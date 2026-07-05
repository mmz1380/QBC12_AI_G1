import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

try:
    df = pd.read_csv('Divar.csv')
except FileNotFoundError:
    exit()

#DATA PREPARATION 

# 1. Duplicate Check
initial_rows = len(df)
df = df.drop_duplicates()
final_rows = len(df)
print(initial_rows - final_rows)

# 2. Clean category slugs by stripping whitespace and converting to lowercase
cols = ['cat2_slug', 'cat3_slug']

for col in cols:
    # Convert to string to prevent errors with mixed types, then strip and lowercase
    df[col] = df[col].astype(str).str.strip().str.lower()
    
    # 3. Handle 'Unknown' or 'N/A' values as strings
    # Replace common string representations of missing values with 'null'
    df[col] = df[col].replace(['nan', 'none', 'unknown', 'null', '-'], 'null')

print("✅ Text cleaning (Strip, Lower, Unspecified) completed.")

# 4. Filter for Visualization (Handling Long-Tail Categories)
# To prevent cluttered charts, we select only the Top 15 categories
def get_top_n_categories(series, n=15):
    top_cats = series.value_counts().nlargest(n).index
    return top_cats

top_cat2 = get_top_n_categories(df['cat2_slug'])
top_cat3 = get_top_n_categories(df['cat3_slug'])

# Create temporary DataFrames for plotting to keep the original 'df' intact for further analysis
df_cat2_plot = df[df['cat2_slug'].isin(top_cat2)]
df_cat3_plot = df[df['cat3_slug'].isin(top_cat3)]

print(f"📊 Preparation complete: Displaying Top {len(top_cat2)} categories for Level 2 and Top {len(top_cat3)} for Level 3.")


# VISUALIZATION 

sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)
fig, axes = plt.subplots(2, 1, figsize=(16, 14))

# Plot 1: Distribution of Category Level 2
sns.countplot(data=df_cat2_plot, y='cat2_slug', ax=axes[0], palette='viridis', order=df_cat2_plot['cat2_slug'].value_counts().index)
axes[0].set_title('Distribution of Ads by Category Level 2 (Top Categories)', fontsize=16, fontweight='bold')
axes[0].set_xlabel('Number of Ads', fontsize=12)
axes[0].set_ylabel('Category Level 2', fontsize=12)

# Plot 2: Distribution of Category Level 3
sns.countplot(data=df_cat3_plot, y='cat3_slug', ax=axes[1], palette='magma', order=df_cat3_plot['cat3_slug'].value_counts().index)
axes[1].set_title('Distribution of Ads by Category Level 3 (Top Categories)', fontsize=16, fontweight='bold')
axes[1].set_xlabel('Number of Ads', fontsize=12)
axes[1].set_ylabel('Category Level 3', fontsize=12)

plt.tight_layout()
plt.show()


