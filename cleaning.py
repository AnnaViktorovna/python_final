import pandas as pd
import numpy as np

print("WEATHER DATA CLEANING PIPELINE")
print("\n[1] LOADING DATA")

df = pd.read_csv("weather_data.csv")

print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst 5 rows:")
print(df.head())
print(f"\nData types:")
print(df.dtypes)

print("[2] BEFORE CLEANING - DATA QUALITY ANALYSIS")
print(f"\n✗ Missing values (NaN):")
missing = df.isnull().sum()
if missing.sum() > 0:
    print(missing[missing > 0])
else:
    print("  None")

print(f"\n✗ 'N/A' string values:")
for col in df.columns:
    na_count = (df[col] == 'N/A').sum()
    if na_count > 0:
        print(f"  {col}: {na_count}")

print(f"\n✗ Duplicate rows (full): {df.duplicated().sum()}")
print(f"✗ Duplicate cities: {df['City'].duplicated().sum()}")

print(f"\n✗ Empty strings:")
for col in ['City', 'Temperature', 'Condition']:
    if col in df.columns:
        empty = (df[col].astype(str).str.strip() == '').sum()
        if empty > 0:
            print(f"  {col}: {empty}")

print(f"\n✗ Temperature values sample:")
print(df['Temperature'].value_counts().head(10))

print("[3] CLEANING DATA")

df_clean = df.copy()
print(f"\nStarting with {len(df_clean)} rows")

before = len(df_clean)
df_clean = df_clean.drop_duplicates()
removed = before - len(df_clean)
print(f"✓ Removed {removed} full duplicates")

before = len(df_clean)
df_clean = df_clean.drop_duplicates(subset=['City'], keep='first')
removed = before - len(df_clean)
print(f"✓ Removed {removed} duplicate cities")

df_clean = df_clean.replace('N/A', np.nan)
df_clean = df_clean.replace('', np.nan)
print(f"✓ Replaced 'N/A' and empty strings with NaN")

before = len(df_clean)
df_clean = df_clean.dropna(subset=['City'])
removed = before - len(df_clean)
print(f"✓ Removed {removed} rows without city")

df_clean['City'] = df_clean['City'].str.strip()
df_clean['Condition'] = df_clean['Condition'].fillna('Unknown').str.strip()
print(f"✓ Trimmed whitespace from text fields")

df_clean['Temp_Raw'] = df_clean['Temperature']
df_clean['Temp_Value'] = df_clean['Temperature'].str.extract(r'(-?\d+\.?\d*)')[0]
df_clean['Temp_Numeric'] = pd.to_numeric(df_clean['Temp_Value'], errors='coerce')

df_clean['Temp_Unit'] = 'F'
df_clean.loc[df_clean['Temperature'].str.contains('°C|C', case=False, na=False), 'Temp_Unit'] = 'C'

print(f"✓ Parsed temperature values")

before = len(df_clean)
df_clean = df_clean.dropna(subset=['Temp_Numeric'])
removed = before - len(df_clean)
print(f"✓ Removed {removed} rows with invalid temperature")

mask_celsius = df_clean['Temp_Unit'] == 'C'
df_clean.loc[mask_celsius, 'Temp_Numeric'] = (df_clean.loc[mask_celsius, 'Temp_Numeric'] * 9/5) + 32
df_clean['Temp_Unit'] = 'F'
print(f"✓ Converted all temperatures to Fahrenheit")

print(f"\nFinal row count: {len(df_clean)}")

print("[4] TRANSFORMING DATA")

def temp_category(temp):
    if temp < 32:
        return 'Freezing'
    elif temp < 50:
        return 'Cold'
    elif temp < 68:
        return 'Cool'
    elif temp < 86:
        return 'Warm'
    else:
        return 'Hot'

df_clean['Temp_Category'] = df_clean['Temp_Numeric'].apply(temp_category)
print(f"✓ Added temperature category")

df_clean['Country'] = df_clean['Link'].str.extract(r'/weather/([^/]+)/')
print(f"✓ Extracted country/region from URL")

condition_map = {
    'Passing clouds': 'Cloudy',
    'Partly cloudy': 'Cloudy',
    'Mostly cloudy': 'Cloudy',
    'Overcast': 'Cloudy',
    'Sunny': 'Clear',
    'Clear': 'Clear',
    'Fair': 'Clear'
}

df_clean['Condition_Normalized'] = df_clean['Condition'].replace(condition_map)
print(f"✓ Normalized weather conditions")

df_clean = df_clean.sort_values('Temp_Numeric', ascending=False).reset_index(drop=True)
print(f"✓ Sorted by temperature (descending)")

print("[5] AFTER CLEANING - SUMMARY")

print(f"\nRows before: {len(df)}")
print(f"Rows after: {len(df_clean)}")
print(f"Rows removed: {len(df) - len(df_clean)} ({100 * (len(df) - len(df_clean)) / len(df):.1f}%)")

print(f"\nCleaned data preview:")
display_cols = ['City', 'Temp_Raw', 'Temp_Numeric', 'Temp_Category', 'Condition_Normalized']
print(df_clean[display_cols].head(10).to_string(index=False))

print(f"\nMissing values after cleaning:")
missing_after = df_clean.isnull().sum()
if missing_after.sum() > 0:
    print(missing_after[missing_after > 0])
else:
    print("  None ✓")

print("[6] DATA ANALYSIS")

print(f"\nTemperature statistics (°F):")
print(df_clean['Temp_Numeric'].describe().round(1))

print(f"\nDistribution by temperature category:")
print(df_clean['Temp_Category'].value_counts())

print(f"\nTop 10 hottest cities:")
hot_cities = df_clean[['City', 'Temp_Numeric', 'Condition_Normalized']].head(10)
print(hot_cities.to_string(index=False))

print(f"\nTop 10 coldest cities:")
cold_cities = df_clean[['City', 'Temp_Numeric', 'Condition_Normalized']].tail(10)
print(cold_cities.to_string(index=False))

print(f"\nWeather condition distribution:")
print(df_clean['Condition_Normalized'].value_counts())

print(f"\nAverage temperature by condition:")
temp_by_condition = df_clean.groupby('Condition_Normalized')['Temp_Numeric'].agg(['count', 'mean', 'min', 'max']).round(1)
print(temp_by_condition)

print("[7] SAVING CLEANED DATA")

final_columns = [
    'City',
    'Temp_Raw',
    'Temp_Numeric',
    'Temp_Unit',
    'Temp_Category',
    'Condition',
    'Condition_Normalized',
    'Country',
    'Link'
]

df_final = df_clean[final_columns]
df_final.to_csv("weather_data_cleaned.csv", index=False)

print(f" Saved {len(df_final)} rows to 'weather_data_cleaned.csv'")
print(f" Columns: {list(df_final.columns)}")

print("CLEANING COMPLETE")