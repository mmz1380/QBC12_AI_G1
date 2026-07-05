import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# 1. Load Dataset
try:
    df = pd.read_csv('./Divar.csv', low_memory=False)
    print("✅ File loaded successfully.")
except FileNotFoundError:
    print("❌ Error: 'Divar.csv' not found.")
    exit()

# Define the target column name
target_col = 'construction_year' 

def clean_persian_year(val):
    """
    Cleans Persian year strings, handles 'Before [Year]' text, 
    and converts Persian digits to English integers.
    """
    if pd.isna(val):
        return None
    
    val_str = str(val).strip()
    
    # Mapping Persian digits to English digits
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    translation_table = str.maketrans(persian_digits, english_digits)
    val_str = val_str.translate(translation_table)
    
    # Handle descriptive strings like 'قبل از ۱۳۷۰' (Before 1370)
    # We extract the number and subtract 1 to represent it on the timeline
    if 'قبل از' in val_str or 'قبل' in val_str:
        numbers = re.findall(r'\d+', val_str)
        if numbers:
            return int(numbers[0]) - 1
        return None
    
    # Extract numbers from any other string formatting (e.g., 'Year 1395')
    try:
        numbers = re.findall(r'\d+', val_str)
        if numbers:
            return int(numbers[0])
        return None
    except:
        return None

# --- Start Data Cleaning Process ---

print("🔄 Cleaning data... please wait.")

# Apply the cleaning function to the target column
df[target_col] = df[target_col].apply(clean_persian_year)

# Convert the column to numeric type (invalid entries become NaN)
df[target_col] = pd.to_numeric(df[target_col], errors='coerce')

# Drop NaN values specifically for the visualization step
df_clean = df.dropna(subset=[target_col])

# Verify results
if not df_clean.empty:
    print(f"✅ Success! Cleaned data range: {int(df_clean[target_col].min())} to {int(df_clean[target_col].max())}")
    print(f"🧬 New Data Type: {df_clean[target_col].dtype}")

    # --- Visualization ---
    plt.figure(figsize=(14, 7))
    sns.histplot(df_clean[target_col], discrete=True, color='teal') 
    plt.title('Exact Year Distribution')
    plt.show()

