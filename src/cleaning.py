import pandas as pd
import numpy as np
from pathlib import Path


RAW_PATH = Path("data/raw/Life Expectancy Data.csv")
PROCESSED_PATH = Path("data/processed/health_clean.csv")

NUMERIC_COLS = [
    "life_expectancy", "adult_mortality", "alcohol",
    "hepatitis_b", "bmi", "polio", "total_expenditure",
    "diphtheria", "gdp", "population",
    "thinness_1_19_years", "thinness_5_9_years",
    "income_composition_of_resources", "schooling"
]


def load_data(path):
    return pd.read_csv(path)


def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[\s\-/]+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )
    return df


def fill_missing(df):
    for col in NUMERIC_COLS:
        if col not in df.columns:
            continue
        df[col] = df.groupby("country")[col].transform(
            lambda x: x.fillna(x.median())
        )
        df[col] = df.groupby("status")[col].transform(
            lambda x: x.fillna(x.median())
        )
        df[col] = df[col].fillna(df[col].median())
    return df


def fix_types(df):
    df["year"] = df["year"].astype(int)
    df["population"] = df["population"].astype(int)
    return df


def remove_duplicates(df):
    return df.drop_duplicates(subset=["country", "year"])


def validate(df):
    df = df[df["life_expectancy"].between(1, 100)]
    df = df[df["gdp"] >= 0]
    df = df[df["population"] > 0]
    return df


def add_features(df):
    df["gdp_per_capita"] = (df["gdp"] / df["population"] * 1000).round(2)
    df["decade"] = ((df["year"] // 10) * 10).astype(str) + "s"
    return df


def run_pipeline(raw_path=RAW_PATH, output_path=PROCESSED_PATH):
    df = load_data(raw_path)
    df = clean_columns(df)
    df = remove_duplicates(df)
    df = fill_missing(df)
    df = fix_types(df)
    df = validate(df)
    df = add_features(df)
    df.to_csv(output_path, index=False)
    print(f"Done — {df.shape[0]} rows, {df.shape[1]} columns saved to {output_path}")
    return df


if __name__ == "__main__":
    run_pipeline()