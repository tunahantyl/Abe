"""
Data Service Layer
Handles data loading, processing, and caching
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class DataService:
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.json_path = self.data_dir / "data.json"
        self._cache = None
        self._last_modified = None
    
    def load_data(self) -> Dict:
        """Load data from JSON file with caching"""
        if self._should_reload():
            self._load_from_file()
        return self._cache
    
    def _should_reload(self) -> bool:
        """Check if data should be reloaded"""
        if self._cache is None:
            return True
        
        if not self.json_path.exists():
            return True
        
        current_mtime = self.json_path.stat().st_mtime
        if self._last_modified != current_mtime:
            return True
        
        return False
    
    def _load_from_file(self):
        """Load data from JSON file"""
        if not self.json_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.json_path}")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self._cache = json.load(f)
        
        self._last_modified = self.json_path.stat().st_mtime
    
    def get_years(self) -> List[int]:
        """Get available years"""
        data = self.load_data()
        return data.get('years', [])
    
    def get_universities(self) -> List[Dict]:
        """Get all universities"""
        data = self.load_data()
        return data.get('universities', [])
    
    def get_university_by_slug(self, slug: str) -> Optional[Dict]:
        """Get university by slug"""
        universities = self.get_universities()
        for uni in universities:
            if uni.get('slug') == slug:
                return uni
        return None
    
    def get_ranking_for_year(self, year: int) -> List[Dict]:
        """Get ranking for specific year"""
        universities = self.get_universities()
        year_key = str(year)
        
        ranking = []
        for uni in universities:
            scores = uni.get('scores', {}).get(year_key)
            if scores and scores.get('ortalama') is not None:
                ranking.append({
                    'slug': uni['slug'],
                    'name': uni['name'],
                    'ortalama': scores['ortalama'],
                    'medyan': scores.get('medyan')
                })
        
        # Sort by ortalama score (descending)
        ranking.sort(key=lambda x: x['ortalama'], reverse=True)
        return ranking
    
    def search_universities(self, query: str) -> List[Dict]:
        """Search universities by name"""
        universities = self.get_universities()
        query_lower = query.lower()
        
        results = []
        for uni in universities:
            if query_lower in uni['name'].lower():
                results.append(uni)
        
        return results
    
    def get_latest_year(self) -> Optional[int]:
        """Get the latest available year"""
        years = self.get_years()
        return max(years) if years else None
    
    def get_data_info(self) -> Dict:
        """Get data metadata"""
        data = self.load_data()
        return {
            'lastUpdated': data.get('lastUpdated'),
            'years': data.get('years', []),
            'universityCount': len(data.get('universities', [])),
            'latestYear': self.get_latest_year()
        }

# Global instance
data_service = DataService()
