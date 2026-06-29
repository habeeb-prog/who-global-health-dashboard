import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

PROCESSED_PATH = Path("data/processed/health_clean.csv")

INDICATORS = [
    "life_expectancy", "adult_mortality", "alcohol",
    "hepatitis_b", "bmi", "polio", "total_expenditure",
    "diphtheria", "gdp_per_capita", "population",
    "thinness_1_19_years", "income_composition_of_resources",
    "schooling"
]


def load_clean_data(path=PROCESSED_PATH):
    return pd.read_csv(path)


def compute_trend(series):
    series = series.dropna()
    if len(series) < 3:
        return np.nan, np.nan
    x = np.arange(len(series))
    slope, _, r_value, p_value, _ = stats.linregress(x, series)
    return round(slope, 4), round(r_value ** 2, 4)


def country_trends(df):
    results = []
    for country in df["country"].unique():
        country_df = df[df["country"] == country].sort_values("year")
        for indicator in INDICATORS:
            if indicator not in country_df.columns:
                continue
            slope, r_squared = compute_trend(country_df[indicator])
            results.append({
                "country": country,
                "indicator": indicator,
                "slope": slope,
                "r_squared": r_squared,
                "direction": "improving" if slope > 0 else "declining",
                "latest_value": country_df[indicator].iloc[-1],
                "latest_year": country_df["year"].iloc[-1]
            })
    return pd.DataFrame(results)

def detect_anomalies(df, threshold=2.0):
    records = []
    for indicator in INDICATORS:
        if indicator not in df.columns:
            continue
        df["yoy_change"] = df.groupby("country")[indicator].diff()
        regional_stats = df.groupby(["year", "status"])["yoy_change"].agg(["mean", "std"]).reset_index()
        regional_stats.columns = ["year", "status", "regional_mean", "regional_std"]
        merged = df.merge(regional_stats, on=["year", "status"], how="left")
        merged["z_score"] = (
            (merged["yoy_change"] - merged["regional_mean"]) /
            merged["regional_std"].replace(0, np.nan)
        )
        anomalies = merged[merged["z_score"].abs() > threshold].copy()
        anomalies["indicator"] = indicator
        records.append(anomalies[["country", "year", "status", "indicator", "yoy_change", "z_score"]])

    if records:
        return pd.concat(records, ignore_index=True)
    return pd.DataFrame()


def correlation_matrix(df):
    available = [col for col in INDICATORS if col in df.columns]
    return df[available].corr().round(3)


def regional_benchmarks(df):
    available = [col for col in INDICATORS if col in df.columns]
    group_cols = ["status", "year"]
    agg = df.groupby(group_cols)[available].agg(["mean", "median", "min", "max"])
    agg.columns = ["_".join(col) for col in agg.columns]
    return agg.reset_index()


def run_analysis(path=PROCESSED_PATH):
    df = load_clean_data(path)

    trends = country_trends(df)
    anomalies = detect_anomalies(df)
    correlations = correlation_matrix(df)
    benchmarks = regional_benchmarks(df)

    trends.to_csv("data/processed/trends.csv", index=False)
    anomalies.to_csv("data/processed/anomalies.csv", index=False)
    correlations.to_csv("data/processed/correlations.csv")
    benchmarks.to_csv("data/processed/benchmarks.csv", index=False)

    print(f"Trends computed — {len(trends)} country-indicator pairs")
    print(f"Anomalies detected — {len(anomalies)} flagged records")
    print(f"Correlation matrix — {correlations.shape[0]} indicators")
    print(f"Regional benchmarks — {len(benchmarks)} group-year records")

    return trends, anomalies, correlations, benchmarks


if __name__ == "__main__":
    run_analysis()