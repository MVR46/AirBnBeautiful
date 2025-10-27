"""Data service: Load listings from SQLite and provide query methods."""

import sqlite3
import pandas as pd
import ast
from typing import List, Dict, Optional
from pathlib import Path


class DataService:
    def __init__(self, db_path='data/airbnb.db', auto_prepare=True):
        self.db_path = db_path
        self.conn = None
        self.auto_prepare = auto_prepare
        self._connect()
        
    def _connect(self):
        """Connect to SQLite database."""
        if not Path(self.db_path).exists():
            if self.auto_prepare:
                print(f"\n⚠️  Database not found at {self.db_path}")
                print("📦 Running data preparation automatically...")
                self._prepare_data()
            else:
                raise FileNotFoundError(f"Database not found: {self.db_path}. Run prepare_data.py first.")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
    
    def _prepare_data(self):
        """Run data preparation if database doesn't exist."""
        try:
            import prepare_data
            prepare_data.main()
            print("✅ Data preparation completed successfully!")
        except Exception as e:
            print(f"❌ Error during data preparation: {e}")
            raise RuntimeError(f"Failed to prepare database: {e}")
        
    def get_all_listings(self) -> pd.DataFrame:
        """Load all listings as DataFrame."""
        df = pd.read_sql('SELECT * FROM listings', self.conn)
        # Parse amenities from string representation
        if 'amenities' in df.columns:
            df['amenities'] = df['amenities'].apply(self._parse_amenities)
        return df
    
    def get_listing_by_id(self, listing_id: str) -> Optional[Dict]:
        """Get single listing by ID."""
        query = 'SELECT * FROM listings WHERE id = ?'
        df = pd.read_sql(query, self.conn, params=(listing_id,))
        if df.empty:
            return None
        
        # Parse amenities
        if 'amenities' in df.columns:
            df['amenities'] = df['amenities'].apply(self._parse_amenities)
        
        return df.iloc[0].to_dict()
    
    def filter_listings(self, filters: Dict) -> pd.DataFrame:
        """Apply filters to listings."""
        df = self.get_all_listings()
        
        # Apply filters programmatically
        if filters.get('neighbourhood_group'):
            df = df[df['neighbourhood_group_cleansed'].isin(filters['neighbourhood_group'])]
        
        if filters.get('neighbourhood'):
            df = df[df['neighbourhood_cleansed'].isin(filters['neighbourhood'])]
        
        if filters.get('min_price'):
            df = df[df['price'] >= filters['min_price']]
        
        if filters.get('max_price'):
            df = df[df['price'] <= filters['max_price']]
        
        if filters.get('min_guests'):
            df = df[df['accommodates'] >= filters['min_guests']]
        
        if filters.get('room_type'):
            df = df[df['room_type'] == filters['room_type']]
        
        if filters.get('property_type'):
            df = df[df['property_type'].str.contains(filters['property_type'], case=False, na=False)]
        
        return df
    
    @staticmethod
    def _parse_amenities(amenities_str):
        """Parse amenities from string representation to list."""
        if pd.isna(amenities_str):
            return []
        try:
            # Try parsing as Python literal
            result = ast.literal_eval(str(amenities_str))
            if isinstance(result, list):
                return result
            return []
        except:
            # Fallback: split by comma
            return [a.strip() for a in str(amenities_str).strip('[]').split(',') if a.strip()]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# General Madrid city information
MADRID_GENERAL_INFO = {
    "description": "Madrid is Spain's vibrant capital, known for world-class museums (Prado, Reina Sofía), beautiful parks (Retiro), incredible food culture, and energetic nightlife. The city blends historic charm with modern amenities.",
    "getting_around": "Madrid has excellent public transport: Metro (12 lines, runs 6am-1:30am), buses (24/7 service available), Cercanías trains, and affordable taxis/Uber. The city center is very walkable.",
    "food_culture": "Madrid is famous for tapas, cocido madrileño (chickpea stew), bocadillo de calamares (squid sandwich), and churros with chocolate. Lunch is typically 2-4pm, dinner after 9pm. Sunday vermouth culture is iconic.",
    "weather": "Hot summers (30-40°C/86-104°F in July-August), mild winters (5-15°C/41-59°F). Spring and fall are ideal for visiting. Little rain except in spring/fall.",
    "language": "Spanish is the main language. English is spoken in tourist areas, hotels, and many restaurants, but less common in local neighborhoods.",
    "culture": "Madrid comes alive at night - dinner starts late, nightlife peaks after midnight. Siestas are less common than stereotyped, but many shops close 2-5pm. Sundays are for family, vermouth, and El Rastro market."
}

# Neighborhood data for RAG
NEIGHBORHOOD_DATA = {
    "Centro": {
        "description": "Centro is the historic heart of Madrid, home to iconic landmarks like Plaza Mayor, Puerta del Sol, and the Royal Palace. This bustling district blends centuries-old architecture with modern shops, restaurants, and nightlife.",
        "safety": "Generally safe, especially in well-lit tourist areas. Gran Vía and Sol have good police presence. Be mindful of pickpockets in crowded areas, particularly around Sol and Callao metro stations after midnight.",
        "nightlife": "Vibrant nightlife with countless bars, clubs, and late-night eateries. The area around Huertas and Chueca (adjacent) stays lively until 3-4 AM on weekends.",
        "transport": "Excellent metro connectivity with Sol as a major hub (Lines 1, 2, 3). Buses run frequently. Walking is the best way to explore.",
        "cafes_restaurants": "Endless dining options from traditional tapas bars to modern fusion restaurants. Mercado de San Miguel is a must-visit food hall. Coffee culture thrives around Malasaña and Chueca borders.",
        "noise_level": "High, especially on weekends and holidays. Expect street noise until late."
    },
    "Salamanca": {
        "description": "Salamanca is Madrid's most upscale neighborhood, known for designer boutiques along Calle Serrano, Michelin-starred restaurants, and elegant 19th-century architecture. It's quieter and more residential than Centro.",
        "safety": "One of the safest districts in Madrid. Well-policed, well-lit, with low crime rates even at night.",
        "nightlife": "More subdued than Centro. Upscale cocktail bars and wine lounges rather than loud clubs. Popular with professionals and older crowds.",
        "transport": "Great metro access (Lines 4, 5, 9). Bus routes connect to all major areas. Less walkable to Centro but taxis/metro are quick.",
        "cafes_restaurants": "High-end dining scene. Famous for gourmet tapas, seafood, and international cuisine. Café culture is sophisticated—expect quality over quantity.",
        "noise_level": "Low to moderate. Residential streets are quiet; main avenues (Serrano, Goya) have daytime traffic noise."
    },
    "Chamberí": {
        "description": "Chamberí is a charming, residential neighborhood with a village-like feel. Known for local markets like Mercado de Vallehermoso, tree-lined streets, and authentic madrileño life away from tourist crowds.",
        "safety": "Very safe. Family-friendly with a strong local community. Evening strolls are common and safe.",
        "nightlife": "Laid-back. Local bars and small music venues cater to residents. Fewer clubs, more neighborhood taverns.",
        "transport": "Well-connected via metro (Lines 1, 2, 5, 6, 10 at various points). Buses are reliable. Bilbao and Quevedo stations are key hubs.",
        "cafes_restaurants": "Excellent local eateries. Ponzano Street is famous for gourmet tapas. Markets offer fresh produce and casual dining.",
        "noise_level": "Low. Mostly residential; quiet nights except near major streets."
    },
    "Retiro": {
        "description": "Named after the famous Retiro Park, this elegant district combines green spaces with upscale residential areas. Close to museums (Prado, Reina Sofía) and peaceful avenues.",
        "safety": "Very safe. Park is patrolled; surrounding streets are well-maintained and secure.",
        "nightlife": "Quiet. A few wine bars and cafés, but most nightlife is in adjacent Centro or Salamanca.",
        "transport": "Good metro coverage (Lines 1, 2, 9). Retiro and Ibiza stations are central. Easy access to Atocha train station.",
        "cafes_restaurants": "Moderate selection. Park-adjacent cafés are lovely for brunch. Fewer dinner options than Centro, but quality is high.",
        "noise_level": "Very low. Peaceful, especially near the park."
    },
    "Tetuán": {
        "description": "Tetuán is a multicultural, working-class neighborhood north of Centro. It's rapidly gentrifying, with new restaurants and art spaces opening alongside traditional shops and markets.",
        "safety": "Generally safe, though some areas are less polished. Stick to main streets at night. Bravo Murillo and Alvarado are well-traveled.",
        "nightlife": "Emerging scene. Local bars, live music venues, and affordable eateries. Less touristy, more authentic.",
        "transport": "Excellent metro access (Lines 1, 9, 10). Direct line to Sol and Gran Vía. Buses are frequent.",
        "cafes_restaurants": "Diverse food scene—Peruvian, Chinese, Moroccan, and Spanish mix. Great value for money.",
        "noise_level": "Moderate. Main avenues are busy; side streets quieter."
    },
    "Arganzuela": {
        "description": "South of Centro, Arganzuela is a residential district with parks (Madrid Río), modern developments, and proximity to Atocha train station. Quieter than central areas but well-connected.",
        "safety": "Safe overall. Parks are well-used and monitored. Some industrial pockets are less active at night.",
        "nightlife": "Limited. A few local bars and restaurants. Most residents head to Centro or Lavapiés for nightlife.",
        "transport": "Great connectivity via Atocha (trains, metro Lines 1, 3). Buses along the river. Walkable to Centro.",
        "cafes_restaurants": "Improving. Madrid Río area has trendy cafés. Local markets offer authentic dining.",
        "noise_level": "Low to moderate. Quieter than Centro; some traffic noise near Atocha."
    },
    "Moncloa - Aravaca": {
        "description": "A large district stretching from university areas near Moncloa to upscale residential Aravaca. Home to students, families, and parks like Casa de Campo.",
        "safety": "Safe, especially in residential zones. University area is lively and well-policed. Parks are safe during the day.",
        "nightlife": "Student-driven near Moncloa (cheap bars, clubs). Aravaca is quiet and family-oriented.",
        "transport": "Moncloa is a major metro/bus hub (Lines 3, 6). Aravaca has metro (Line 10) and trains.",
        "cafes_restaurants": "Student-friendly cafés and budget eateries near Moncloa. Aravaca has upscale dining.",
        "noise_level": "Moderate near Moncloa (student activity); low in Aravaca."
    },
    "Latina": {
        "description": "Latina is a traditional, working-class neighborhood southwest of Centro. Known for Sunday El Rastro flea market, tapas bars, and strong local identity.",
        "safety": "Generally safe. El Rastro area gets crowded (watch belongings). Residential streets are quiet and secure.",
        "nightlife": "Authentic local bars and small clubs. La Latina area (border with Centro) is famous for Sunday vermouth culture.",
        "transport": "Well-connected via metro (Lines 5, 6). Buses run frequently. Walkable to Centro.",
        "cafes_restaurants": "Excellent tapas scene. Cava Baja street is iconic. Local markets offer fresh, affordable food.",
        "noise_level": "Moderate. Lively on weekends (El Rastro); quieter weekdays."
    },
    "Carabanchel": {
        "description": "A southern, working-class district with a mix of old and new Madrid. Affordable, multicultural, and increasingly connected to the city center.",
        "safety": "Safe in most areas, though less polished than central districts. Stick to well-lit streets at night.",
        "nightlife": "Local bars and small venues. Not a nightlife destination; most action is in Centro.",
        "transport": "Good metro coverage (Lines 5, 6, 11). Buses connect to Centro in 20-30 minutes.",
        "cafes_restaurants": "Diverse, affordable dining. Local markets and family-run restaurants dominate.",
        "noise_level": "Low to moderate. Residential feel; some traffic on main roads."
    },
    "Fuencarral - El Pardo": {
        "description": "A vast northern district ranging from urban Fuencarral to rural El Pardo. Includes shopping areas, parks, and suburban zones.",
        "safety": "Very safe. Well-policed, family-friendly, with low crime rates.",
        "nightlife": "Limited. La Vaguada shopping area has some bars; otherwise quiet and residential.",
        "transport": "Metro Lines 1, 7, 9, 10 serve different areas. Buses are essential for reaching El Pardo.",
        "cafes_restaurants": "Shopping mall dining and local cafés. Less variety than central districts.",
        "noise_level": "Low. Suburban and peaceful."
    },
    "Chamartín": {
        "description": "A business and residential district north of Centro, home to Chamartín train station, modern office towers, and upscale neighborhoods like El Viso.",
        "safety": "Very safe. Well-maintained, with good lighting and police presence.",
        "nightlife": "Limited. Business-focused; most nightlife is in Centro. A few upscale bars and restaurants.",
        "transport": "Excellent. Chamartín station (trains, metro Lines 1, 10). Buses connect to all areas.",
        "cafes_restaurants": "Business lunch spots and upscale dining. Less variety than Centro or Salamanca.",
        "noise_level": "Low to moderate. Quiet residential streets; traffic near the station."
    }
}

