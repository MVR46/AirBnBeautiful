"""Price Optimization Service using RandomForest feature importance."""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler


# Available amenities to consider
AVAILABLE_AMENITIES = [
    "WiFi", "Kitchen", "Air conditioning", "Washer", "TV", "Heating",
    "Parking", "Pool", "Elevator", "Dishwasher", "Dryer", "Iron",
    "Coffee maker", "Balcony", "Gym"
]

# Estimated costs for amenities (in EUR)
AMENITY_COSTS = {
    "Kitchen": 1500,
    "Washer": 400,
    "Air conditioning": 1200,
    "Heating": 800,
    "TV": 200,
    "WiFi": 200,
    "Parking": 0,  # Usually policy, not investment
    "Pool": 5000,
    "Elevator": 0,  # Structural, can't add
    "Dishwasher": 500,
    "Dryer": 400,
    "Iron": 50,
    "Coffee maker": 100,
    "Balcony": 0,  # Structural
    "Gym": 2000,
}

# Global model
price_model = None
feature_names = []
scaler = None
rf_importance = {}


def normalize_amenity_name(amenity: str) -> str:
    """Normalize amenity name to match our standard list."""
    amenity_lower = amenity.lower()
    
    # Mapping variations
    if any(x in amenity_lower for x in ["wifi", "wi-fi", "internet"]):
        return "WiFi"
    elif any(x in amenity_lower for x in ["kitchen"]):
        return "Kitchen"
    elif any(x in amenity_lower for x in ["air conditioning", "ac", "air conditioner"]):
        return "Air conditioning"
    elif any(x in amenity_lower for x in ["washer", "washing machine"]):
        return "Washer"
    elif any(x in amenity_lower for x in ["tv", "television"]):
        return "TV"
    elif any(x in amenity_lower for x in ["heating", "heater"]):
        return "Heating"
    elif any(x in amenity_lower for x in ["parking"]):
        return "Parking"
    elif any(x in amenity_lower for x in ["pool", "swimming"]):
        return "Pool"
    elif any(x in amenity_lower for x in ["elevator", "lift"]):
        return "Elevator"
    elif any(x in amenity_lower for x in ["dishwasher"]):
        return "Dishwasher"
    elif any(x in amenity_lower for x in ["dryer"]):
        return "Dryer"
    elif any(x in amenity_lower for x in ["iron"]):
        return "Iron"
    elif any(x in amenity_lower for x in ["coffee"]):
        return "Coffee maker"
    elif any(x in amenity_lower for x in ["balcony"]):
        return "Balcony"
    elif any(x in amenity_lower for x in ["gym", "fitness"]):
        return "Gym"
    
    return amenity


def train_price_model(df: pd.DataFrame):
    """Train RandomForest model on listings data."""
    global price_model, feature_names, scaler, rf_importance
    
    print("Training price optimization model...")
    
    # Prepare features
    df_model = df.copy()
    
    # Create amenity flags
    for amenity in AVAILABLE_AMENITIES:
        col_name = f"has_{amenity.lower().replace(' ', '_')}"
        df_model[col_name] = df_model['amenities'].apply(
            lambda amen_list: int(any(normalize_amenity_name(a) == amenity for a in amen_list))
            if isinstance(amen_list, list) else 0
        )
    
    # Feature columns
    amenity_cols = [f"has_{a.lower().replace(' ', '_')}" for a in AVAILABLE_AMENITIES]
    numeric_cols = ['accommodates', 'beds', 'bathrooms']
    
    # One-hot encode neighborhood
    neighborhood_dummies = pd.get_dummies(
        df_model['neighbourhood_group_cleansed'],
        prefix='neigh'
    )
    
    # Combine features
    X = pd.concat([
        df_model[amenity_cols + numeric_cols],
        neighborhood_dummies
    ], axis=1)
    
    y = df_model['price'].values
    
    # Store feature names
    feature_names = X.columns.tolist()
    
    # Train model
    price_model = RandomForestRegressor(
        n_estimators=400,
        max_depth=None,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    
    price_model.fit(X.values, y)
    
    # Extract feature importance for amenities only
    for i, col in enumerate(feature_names):
        if col.startswith('has_'):
            amenity_name = col.replace('has_', '').replace('_', ' ').title()
            # Find matching standard amenity
            for std_amenity in AVAILABLE_AMENITIES:
                if std_amenity.lower().replace(' ', '_') == col.replace('has_', ''):
                    rf_importance[std_amenity] = price_model.feature_importances_[i]
                    break
    
    print(f"Model trained on {len(df_model)} listings with R² score on training data")
    print(f"Top 5 important amenities: {sorted(rf_importance.items(), key=lambda x: -x[1])[:5]}")


def encode_listing_features(current_amenities: List[str], listing_meta: Dict,
                            neighborhoods: List[str]) -> np.ndarray:
    """Encode listing into feature vector."""
    # Create amenity flags
    amenity_flags = {}
    normalized_current = [normalize_amenity_name(a) for a in current_amenities]
    
    for amenity in AVAILABLE_AMENITIES:
        col_name = f"has_{amenity.lower().replace(' ', '_')}"
        amenity_flags[col_name] = 1 if amenity in normalized_current else 0
    
    # Numeric features
    numeric_features = {
        'accommodates': listing_meta.get('guests', 2),
        'beds': listing_meta.get('beds', 1),
        'bathrooms': listing_meta.get('baths', 1.0),
    }
    
    # Neighborhood one-hot
    neighborhood_features = {}
    for neigh in neighborhoods:
        col_name = f"neigh_{neigh}"
        neighborhood_features[col_name] = 1 if neigh == listing_meta.get('neighborhood', '') else 0
    
    # Combine into feature vector matching training order
    feature_vector = []
    for fname in feature_names:
        if fname in amenity_flags:
            feature_vector.append(amenity_flags[fname])
        elif fname in numeric_features:
            feature_vector.append(numeric_features[fname])
        elif fname in neighborhood_features:
            feature_vector.append(neighborhood_features[fname])
        else:
            feature_vector.append(0)  # Missing features default to 0
    
    return np.array(feature_vector).reshape(1, -1)


def predict_price(current_amenities: List[str], listing_meta: Dict,
                 neighborhoods: List[str]) -> float:
    """Predict price for a listing."""
    if price_model is None:
        raise ValueError("Price model not trained yet")
    
    X = encode_listing_features(current_amenities, listing_meta, neighborhoods)
    prediction = price_model.predict(X)[0]
    
    return float(prediction)


def get_price_suggestions(current_amenities: List[str], target_price: float,
                         listing_meta: Dict, neighborhoods: List[str]) -> Dict:
    """
    Generate price optimization suggestions.
    Based on Feature 3 notebook cell 15 (personalized recommendations).
    """
    if price_model is None:
        raise ValueError("Price model not trained yet")
    
    # Normalize current amenities
    normalized_current = [normalize_amenity_name(a) for a in current_amenities]
    current_set = set(normalized_current)
    
    # Predict current price
    current_estimate = predict_price(normalized_current, listing_meta, neighborhoods)
    
    # Find missing amenities
    missing_amenities = [a for a in AVAILABLE_AMENITIES if a not in current_set]
    
    if not missing_amenities:
        return {
            "currentPriceEstimate": round(current_estimate, 2),
            "targetPrice": target_price,
            "featureImportance": [],
            "recommendedAdditions": [],
            "notes": "Listing already has all tracked amenities."
        }
    
    # Calculate lift for each missing amenity
    recommendations = []
    
    for amenity in missing_amenities:
        # Create hypothetical listing with this amenity added
        test_amenities = normalized_current + [amenity]
        test_estimate = predict_price(test_amenities, listing_meta, neighborhoods)
        
        lift = test_estimate - current_estimate
        
        if lift > 0:  # Only recommend if positive impact
            recommendations.append({
                "amenity": amenity,
                "estimatedLift": round(float(lift), 2),
                "importance": rf_importance.get(amenity, 0.0),
                "cost": AMENITY_COSTS.get(amenity, 0)
            })
    
    # Sort by estimated lift (highest first)
    recommendations.sort(key=lambda x: -x["estimatedLift"])
    
    # Prepare feature importance list (top 10)
    importance_list = [
        {"feature": amenity, "importance": round(float(importance), 3)}
        for amenity, importance in sorted(rf_importance.items(), key=lambda x: -x[1])[:10]
    ]
    
    # Format recommended additions
    recommended_additions = [
        {"amenity": r["amenity"], "estimatedLift": r["estimatedLift"]}
        for r in recommendations[:5]  # Top 5
    ]
    
    # Calculate gap
    gap = target_price - current_estimate
    notes = f"Based on {len(neighborhoods)} Madrid neighborhoods. "
    
    if gap > 0:
        cumulative_lift = sum(r["estimatedLift"] for r in recommendations[:3])
        if cumulative_lift >= gap * 0.8:
            notes += f"Adding top 3 amenities could increase price by €{cumulative_lift:.0f}, approaching your target."
        else:
            notes += f"Target is €{gap:.0f} above current estimate. Top amenities may help bridge the gap."
    else:
        notes += "Current estimate already meets or exceeds target."
    
    return {
        "currentPriceEstimate": round(current_estimate, 2),
        "targetPrice": target_price,
        "featureImportance": importance_list,
        "recommendedAdditions": recommended_additions,
        "notes": notes
    }

