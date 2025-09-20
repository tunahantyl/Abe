"""
Universities API Routes
Endpoints for university-specific operations
"""

from fastapi import APIRouter, HTTPException
from typing import List
from data.service import data_service

router = APIRouter()

@router.get("/")
async def get_all_universities():
    """Get all universities"""
    try:
        universities = data_service.get_universities()
        return {"universities": universities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{slug}")
async def get_university(slug: str):
    """Get university by slug"""
    try:
        university = data_service.get_university_by_slug(slug)
        if not university:
            raise HTTPException(status_code=404, detail="University not found")
        
        return university
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{slug}/scores")
async def get_university_scores(slug: str):
    """Get university scores across all years"""
    try:
        university = data_service.get_university_by_slug(slug)
        if not university:
            raise HTTPException(status_code=404, detail="University not found")
        
        years = data_service.get_years()
        scores = []
        
        for year in sorted(years):
            year_scores = university.get('scores', {}).get(str(year))
            if year_scores:
                scores.append({
                    'year': year,
                    'ortalama': year_scores.get('ortalama'),
                    'medyan': year_scores.get('medyan')
                })
        
        return {
            'university': university['name'],
            'slug': slug,
            'scores': scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
