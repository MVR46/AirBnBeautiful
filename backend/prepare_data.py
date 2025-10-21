"""
Data preparation script: Load Madrid dataset, clean, select 50 representative listings.
Based on Feature 1 notebook cleaning pipeline (cells 5-11).
"""

import pandas as pd
import numpy as np
import re
import sqlite3
import os
from pathlib import Path

# Dataset URL from MVR46/airbnb-data-madrid
DATASET_URL = 'https://raw.githubusercontent.com/MVR46/airbnb-data-madrid/main/listings.csv'


def parse_currency(x):
    """Convert currency-like strings to float (e.g., '$1,234.00' -> 1234.00)."""
    if pd.isna(x):
        return np.nan
    s = re.sub(r'[^\d,.\-]', '', str(x))
    s = s.replace(',', '')
    try:
        return float(s)
    except Exception:
        return np.nan


def parse_percent(s):
    return (pd.Series(s)
            .astype(str)
            .str.replace('%', '', regex=False)
            .replace(['nan', 'None', 'NaN'], np.nan)
            .astype(float))


def bathrooms_from_text(txt):
    """Extract numeric bathrooms from bathrooms_text."""
    if pd.isna(txt):
        return np.nan
    t = str(txt).lower()
    if 'half-bath' in t or 'half bath' in t:
        m = re.search(r'(\d+(\.\d+)?)', t)
        return float(m.group(1)) if m else 0.5
    m = re.search(r'(\d+(\.\d+)?)', t)
    return float(m.group(1)) if m else np.nan


def tf_to_bool(values, default=False):
    """Convert truthy/falsey tokens to python bool."""
    mapping = {
        True: True, False: False,
        't': True, 'true': True, '1': True, 'y': True, 'yes': True,
        'f': False, 'false': False, '0': False, 'n': False, 'no': False
    }
    ser = pd.Series(values, dtype='object')
    norm = np.where(ser.isin([True, False]), ser, ser.astype(str).str.strip().str.lower())
    mapped = pd.Series(norm, dtype='object').map(mapping)
    if default is not None:
        mapped = mapped.where(pd.notna(mapped), default)
    return mapped.astype(bool)


def clean_categorical(series):
    """Clean categorical text fields."""
    if series.dtype == 'O':
        return (series.astype(str)
                .str.strip()
                .str.replace(r'\s+', ' ', regex=True))
    return series


def prepare_dataset():
    """Load, clean, and prepare the Madrid dataset."""
    
    print("Loading Madrid dataset...")
    df = pd.read_csv(DATASET_URL)
    print(f"Loaded {len(df)} listings with {len(df.columns)} columns")
    
    # Keep essential columns
    KEEP_COLS = [
        'id', 'listing_url', 'picture_url',
        'neighbourhood_group_cleansed', 'neighbourhood_cleansed', 'latitude', 'longitude',
        'room_type', 'property_type', 'accommodates', 'bathrooms', 'bathrooms_text', 'bedrooms', 'beds',
        'amenities', 'instant_bookable', 'has_availability',
        'price', 'minimum_nights', 'maximum_nights',
        'availability_30', 'availability_60', 'availability_90', 'availability_365',
        'review_scores_rating', 'number_of_reviews',
        'host_is_superhost', 'host_response_rate', 'host_acceptance_rate',
        'name', 'description', 'neighborhood_overview',
        'first_review', 'last_review'
    ]
    
    keep_existing = [c for c in KEEP_COLS if c in df.columns]
    df = df[keep_existing].copy()
    print(f"Kept {len(keep_existing)} relevant columns")
    
    # Parse price
    if 'price' in df.columns:
        df['price'] = df['price'].apply(parse_currency)
    
    # Parse dates
    for c in ['first_review', 'last_review']:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')
    
    # Parse percentages
    for c in ['host_response_rate', 'host_acceptance_rate']:
        if c in df.columns:
            df[c] = parse_percent(df[c])
    
    # Convert booleans
    for c in ['instant_bookable', 'host_is_superhost', 'has_availability']:
        if c in df.columns:
            df[c] = tf_to_bool(df[c], default=False)
    
    # Derive bathrooms from text where missing
    if {'bathrooms', 'bathrooms_text'}.issubset(df.columns):
        mask_missing_bath = df['bathrooms'].isna()
        df.loc[mask_missing_bath, 'bathrooms'] = df.loc[mask_missing_bath, 'bathrooms_text'].apply(bathrooms_from_text)
    
    print("Data types converted")
    
    # Remove rows with missing critical features
    CRITICAL_MUST_HAVE = [
        'price', 'room_type', 'property_type', 'accommodates',
        'neighbourhood_cleansed', 'latitude', 'longitude',
        'bathrooms_text', 'bedrooms', 'beds'
    ]
    critical_existing = [c for c in CRITICAL_MUST_HAVE if c in df.columns]
    
    before_rows = df.shape[0]
    df = df.dropna(subset=critical_existing)
    
    # Drop if no picture
    if 'picture_url' in df.columns:
        df = df.dropna(subset=['picture_url'])
    
    print(f"Dropped {before_rows - df.shape[0]} rows with missing critical values")
    
    # Clean categorical fields
    for c in ['room_type', 'property_type', 'neighbourhood_group_cleansed', 'neighbourhood_cleansed']:
        if c in df.columns:
            df[c] = clean_categorical(df[c])
    
    # Clean text fields
    for c in ['name', 'description', 'neighborhood_overview']:
        if c in df.columns:
            df[c] = (df[c].astype(str)
                     .str.replace(r'\s+', ' ', regex=True)
                     .str.strip())
    
    # Deduplicate by id
    before = len(df)
    if 'id' in df.columns:
        df = df.drop_duplicates(subset=['id']).copy()
    print(f"Deduplicated: dropped {before - len(df)} duplicate rows")
    
    # Basic validity filters
    valid_mask = (
        (df['price'] > 0) &
        (df['accommodates'] >= 1) &
        (df['bathrooms'] >= 0.5) &
        (df['bedrooms'] >= 0) &
        (df['beds'] >= 0)
    )
    before = len(df)
    df = df.loc[valid_mask].copy()
    print(f"Validity filtering: dropped {before - len(df)} invalid rows")
    
    # Min/max nights sanity
    if {'minimum_nights', 'maximum_nights'}.issubset(df.columns):
        swap_mask = df['minimum_nights'] > df['maximum_nights']
        if swap_mask.any():
            mn = df.loc[swap_mask, 'maximum_nights']
            mx = df.loc[swap_mask, 'minimum_nights']
            df.loc[swap_mask, 'minimum_nights'] = mn.values
            df.loc[swap_mask, 'maximum_nights'] = mx.values
        df['minimum_nights'] = df['minimum_nights'].clip(lower=1, upper=365)
        df['maximum_nights'] = df['maximum_nights'].clip(lower=1, upper=999)
    
    # Price-derived helpers
    if {'price', 'accommodates'}.issubset(df.columns):
        df['price_per_guest'] = (df['price'] / df['accommodates']).replace([np.inf, -np.inf], np.nan)
    
    # Type-casting
    if 'accommodates' in df.columns:
        df['accommodates'] = pd.to_numeric(df['accommodates'], errors='coerce').astype('Int64')
    for c in ['bedrooms', 'beds', 'number_of_reviews']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
            if c in ['bedrooms', 'beds']:
                df[c] = df[c].round(0).astype('Int64')
            else:
                df[c] = df[c].round(0).clip(lower=0).astype('Int64')
    if 'bathrooms' in df.columns:
        df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce').astype(float)
    
    df = df.reset_index(drop=True)
    print(f"Final cleaned dataset: {len(df)} listings")
    
    return df


def select_representative_listings(df, n=1000):
    """Select ~1000 diverse listings for production."""
    
    # Stratify by neighborhood group and price quartiles for diversity
    df['price_quartile'] = pd.qcut(df['price'], q=4, labels=['budget', 'mid', 'upscale', 'luxury'], duplicates='drop')
    
    # Sample proportionally from each neighborhood group
    sampled = []
    for group in df['neighbourhood_group_cleansed'].unique():
        group_df = df[df['neighbourhood_group_cleansed'] == group]
        # Take proportional sample
        n_samples = max(1, int(n * len(group_df) / len(df)))
        if len(group_df) >= n_samples:
            sample = group_df.sample(n=n_samples, random_state=42)
        else:
            sample = group_df
        sampled.append(sample)
    
    result = pd.concat(sampled, ignore_index=True)
    
    # If we have too many, sample randomly
    if len(result) > n:
        result = result.sample(n=n, random_state=42)
    # If we have too few, add more randomly
    elif len(result) < n:
        remaining = df[~df['id'].isin(result['id'])]
        additional = remaining.sample(n=min(n - len(result), len(remaining)), random_state=42)
        result = pd.concat([result, additional], ignore_index=True)
    
    result = result.drop(columns=['price_quartile'], errors='ignore')
    print(f"Selected {len(result)} representative listings")
    return result


def create_sqlite_db(df, db_path='data/airbnb.db'):
    """Create SQLite database with listings."""
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # Prepare DataFrame for SQL
    df_sql = df.copy()
    
    # Convert lists/arrays to JSON strings for amenities
    if 'amenities' in df_sql.columns:
        df_sql['amenities'] = df_sql['amenities'].astype(str)
    
    # Convert Int64 to regular int for SQLite
    for col in df_sql.columns:
        if df_sql[col].dtype == 'Int64':
            df_sql[col] = df_sql[col].astype('float').where(df_sql[col].notna(), None)
    
    # Write to SQLite
    df_sql.to_sql('listings', conn, if_exists='replace', index=False)
    
    # Create indexes for common queries
    conn.execute('CREATE INDEX IF NOT EXISTS idx_neighborhood ON listings(neighbourhood_cleansed)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_price ON listings(price)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_guests ON listings(accommodates)')
    
    conn.commit()
    conn.close()
    
    print(f"Created SQLite database at {db_path} with {len(df)} listings")


def main():
    """Main data preparation pipeline."""
    
    print("=" * 60)
    print("Madrid Airbnb Dataset Preparation")
    print("=" * 60)
    
    # Load and clean
    df_clean = prepare_dataset()
    
    # Select representative subset
    df_mvp = select_representative_listings(df_clean, n=1000)
    
    # Save to SQLite
    create_sqlite_db(df_mvp)
    
    # Save raw CSV for inspection
    os.makedirs('data', exist_ok=True)
    df_mvp.to_csv('data/listings_1000.csv', index=False)
    print(f"Saved listings to data/listings_1000.csv")
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("Dataset Summary")
    print("=" * 60)
    print(f"Total listings: {len(df_mvp)}")
    print(f"Neighborhoods: {df_mvp['neighbourhood_cleansed'].nunique()}")
    print(f"Neighborhood groups: {df_mvp['neighbourhood_group_cleansed'].nunique()}")
    print(f"Price range: €{df_mvp['price'].min():.0f} - €{df_mvp['price'].max():.0f}")
    print(f"Avg price: €{df_mvp['price'].mean():.0f}")
    print(f"Avg rating: {df_mvp['review_scores_rating'].mean():.1f}")
    print("\nTop neighborhoods:")
    print(df_mvp['neighbourhood_cleansed'].value_counts().head(10))


if __name__ == '__main__':
    main()

