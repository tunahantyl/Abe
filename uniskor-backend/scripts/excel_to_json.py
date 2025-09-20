#!/usr/bin/env python3
"""
Excel to JSON converter for UniSkor data
Converts R output Excel files to the JSON format expected by the frontend
"""

import pandas as pd
import json
import os
from datetime import datetime
import re

def clean_university_name(name):
    """Clean university name for slug generation"""
    if pd.isna(name):
        return "unknown"
    # Remove extra spaces and special characters
    cleaned = re.sub(r'[^\w\s-]', '', str(name).strip())
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[-\s]+', '-', cleaned.lower())
    return slug

def examine_excel_structure(file_path):
    """Examine Excel file structure"""
    print(f"\n=== Examining {file_path} ===")
    
    # Read all sheet names
    xl_file = pd.ExcelFile(file_path)
    print(f"Sheet names: {xl_file.sheet_names}")
    
    # Examine each sheet
    for sheet_name in xl_file.sheet_names:
        print(f"\n--- Sheet: {sheet_name} ---")
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:")
        print(df.head(3))
        print(f"Data types:")
        print(df.dtypes)

def convert_sfa_scores_to_json(excel_path, output_path):
    """Convert SFA scores Excel to JSON format"""
    print(f"\n=== Converting {excel_path} to JSON ===")
    
    xl_file = pd.ExcelFile(excel_path)
    years = []
    universities = []
    
    # Process each year sheet
    for sheet_name in xl_file.sheet_names:
        if sheet_name.isdigit():  # Year sheets
            year = int(sheet_name)
            years.append(year)
            
            print(f"Processing year {year}...")
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # Find university name column (usually first column)
            uni_col = df.columns[0]
            ortalama_col = None
            medyan_col = None
            
            # Find score columns
            for col in df.columns:
                if 'Ortalama' in str(col) and 'Skor' in str(col):
                    ortalama_col = col
                elif 'Medyan' in str(col) and 'Skor' in str(col):
                    medyan_col = col
            
            print(f"University column: {uni_col}")
            print(f"Ortalama column: {ortalama_col}")
            print(f"Medyan column: {medyan_col}")
            
            # Process each university
            for _, row in df.iterrows():
                uni_name = row[uni_col]
                if pd.isna(uni_name):
                    continue
                    
                slug = clean_university_name(uni_name)
                
                # Find or create university entry
                uni_entry = None
                for u in universities:
                    if u['slug'] == slug:
                        uni_entry = u
                        break
                
                if uni_entry is None:
                    uni_entry = {
                        'slug': slug,
                        'name': str(uni_name).strip(),
                        'scores': {}
                    }
                    universities.append(uni_entry)
                
                # Add scores for this year
                ortalama = row[ortalama_col] if ortalama_col and not pd.isna(row[ortalama_col]) else None
                medyan = row[medyan_col] if medyan_col and not pd.isna(row[medyan_col]) else None
                
                uni_entry['scores'][str(year)] = {
                    'ortalama': float(ortalama) if ortalama is not None else None,
                    'medyan': float(medyan) if medyan is not None else None
                }
    
    # Sort years
    years.sort()
    
    # Create final JSON structure
    result = {
        'years': years,
        'universities': universities,
        'lastUpdated': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Conversion Complete ===")
    print(f"Years: {years}")
    print(f"Universities: {len(universities)}")
    print(f"Output saved to: {output_path}")
    
    return result

def main():
    # Examine both Excel files
    print("Examining Excel files...")
    examine_excel_structure("data/Hamveri 26102024.xlsx")
    examine_excel_structure("data/SFA Skorlar 26102024.xlsx")
    
    # Convert SFA scores to JSON
    result = convert_sfa_scores_to_json("data/SFA Skorlar 26102024.xlsx", "data/data.json")
    
    # Show sample data
    print(f"\n=== Sample Data ===")
    if result['universities']:
        sample_uni = result['universities'][0]
        print(f"Sample university: {sample_uni['name']}")
        print(f"Sample scores: {sample_uni['scores']}")

if __name__ == "__main__":
    main()
