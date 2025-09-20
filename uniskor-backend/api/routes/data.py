"""
Data API Routes
Endpoints for data operations
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from data.service import data_service

router = APIRouter()

@router.get("/")
async def get_data_info():
    """Get data metadata"""
    try:
        return data_service.get_data_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/years")
async def get_years():
    """Get available years"""
    try:
        return {"years": data_service.get_years()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest")
async def get_latest_data():
    """Get latest year data"""
    try:
        latest_year = data_service.get_latest_year()
        if not latest_year:
            raise HTTPException(status_code=404, detail="No data available")
        
        ranking = data_service.get_ranking_for_year(latest_year)
        return {
            "year": latest_year,
            "ranking": ranking
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/year/{year}")
async def get_year_data(year: int):
    """Get data for specific year"""
    try:
        years = data_service.get_years()
        if year not in years:
            raise HTTPException(status_code=404, detail=f"Year {year} not available")
        
        ranking = data_service.get_ranking_for_year(year)
        return {
            "year": year,
            "ranking": ranking
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_universities(q: str = Query(..., min_length=1)):
    """Search universities"""
    try:
        results = data_service.search_universities(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
