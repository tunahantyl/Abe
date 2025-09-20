#!/usr/bin/env python3
"""
Complete data update workflow for UniSkor
1. Run YÖKAK scraping (yokak3.py)
2. Run R analysis (Etkinlik_skorlari.R)
3. Convert Excel to JSON (excel_to_json.py)
4. Update frontend data
"""

import subprocess
import os
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        print("✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main workflow"""
    print("=== UniSkor Data Update Workflow ===\n")
    
    # Get current directory
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    # Step 1: Run YÖKAK scraping (Selenium version)
    print("Step 1: Running YÖKAK scraping with Selenium...")
    if not run_command([sys.executable, "yokak3_selenium.py"]):
        print("❌ YÖKAK scraping failed. Check if ChromeDriver is installed.")
        return False
    
    # Step 2: Run R analysis
    print("\nStep 2: Running R analysis...")
    r_script = "Etkinlik_skorlari.R"
    if not os.path.exists(r_script):
        print(f"❌ R script not found: {r_script}")
        return False
    
    # Try to find Rscript
    rscript_cmd = None
    for cmd in ["Rscript", "Rscript.exe", "/usr/bin/Rscript"]:
        try:
            subprocess.run([cmd, "--version"], check=True, capture_output=True)
            rscript_cmd = cmd
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    if not rscript_cmd:
        print("❌ Rscript not found. Please install R or add it to PATH.")
        return False
    
    if not run_command([rscript_cmd, r_script, "0"]):
        print("❌ R analysis failed.")
        return False
    
    # Step 3: Convert Excel to JSON
    print("\nStep 3: Converting Excel to JSON...")
    if not run_command([sys.executable, "excel_to_json.py"]):
        print("❌ Excel to JSON conversion failed.")
        return False
    
    # Step 4: Verify output
    print("\nStep 4: Verifying output...")
    json_path = "../data/data.json"
    if not os.path.exists(json_path):
        print(f"❌ JSON output not found: {json_path}")
        return False
    
    # Check file size
    size = os.path.getsize(json_path)
    print(f"✓ JSON file created: {json_path} ({size:,} bytes)")
    
    print("\n🎉 Data update completed successfully!")
    print("You can now run the frontend with: cd uniskor-web && npm run dev")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
