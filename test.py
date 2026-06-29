import pandas as pd

df = pd.read_csv('data/raw/Life Expectancy Data.csv')

print("=== SHAPE ===")
print(df.shape)

print("\n=== DATA TYPES ===")
print(df.dtypes)

print("\n=== MISSING VALUES ===")
print(df.isnull().sum())

print("\n=== UNIQUE COUNTRIES ===")
print(df['Country'].nunique())

print("\n=== YEAR RANGE ===")
print(df['Year'].min(), "to", df['Year'].max())

print("\n=== STATUS VALUES ===")
print(df['Status'].value_counts())

print("\n=== LIFE EXPECTANCY RANGE ===")
print(df['Life expectancy '].min(), "to", df['Life expectancy '].max())