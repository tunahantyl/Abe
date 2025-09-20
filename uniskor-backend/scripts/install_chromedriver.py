#!/usr/bin/env python3
"""
ChromeDriver kurulum scripti
macOS için otomatik ChromeDriver indirme ve kurulum
"""

import os
import sys
import platform
import subprocess
import requests
import zipfile
import shutil
from pathlib import Path

def get_chrome_version():
    """Chrome sürümünü al"""
    try:
        if platform.system() == "Darwin":  # macOS
            # Chrome sürümünü al
            result = subprocess.run([
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", 
                "--version"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                return version
        return None
    except Exception as e:
        print(f"Chrome sürümü alınamadı: {e}")
        return None

def download_chromedriver(version):
    """ChromeDriver indir"""
    try:
        # Chrome sürümüne uygun ChromeDriver sürümünü bul
        major_version = version.split('.')[0]
        
        # ChromeDriver API'den sürüm bilgisini al
        api_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            chromedriver_version = response.text.strip()
        else:
            print(f"ChromeDriver sürümü bulunamadı. Chrome {version} için uygun sürüm aranıyor...")
            # Fallback: son sürümü dene
            chromedriver_version = "114.0.5735.90"  # Son bilinen sürüm
        
        # ChromeDriver indir
        download_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_mac64.zip"
        
        print(f"ChromeDriver {chromedriver_version} indiriliyor...")
        response = requests.get(download_url)
        
        if response.status_code == 200:
            # Geçici dosyaya kaydet
            temp_zip = "chromedriver.zip"
            with open(temp_zip, "wb") as f:
                f.write(response.content)
            
            # ZIP'i aç
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            # ChromeDriver'ı /usr/local/bin'e taşı
            chromedriver_path = "chromedriver"
            if os.path.exists(chromedriver_path):
                # Çalıştırılabilir yap
                os.chmod(chromedriver_path, 0o755)
                
                # /usr/local/bin'e kopyala
                target_path = "/usr/local/bin/chromedriver"
                shutil.copy2(chromedriver_path, target_path)
                os.chmod(target_path, 0o755)
                
                print(f"✓ ChromeDriver başarıyla kuruldu: {target_path}")
                
                # Geçici dosyaları temizle
                os.remove(temp_zip)
                os.remove(chromedriver_path)
                
                return True
            else:
                print("❌ ChromeDriver dosyası bulunamadı")
                return False
        else:
            print(f"❌ ChromeDriver indirilemedi: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ChromeDriver kurulumu başarısız: {e}")
        return False

def check_chromedriver():
    """ChromeDriver'ın kurulu olup olmadığını kontrol et"""
    try:
        result = subprocess.run(["chromedriver", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ ChromeDriver zaten kurulu: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    return False

def main():
    """Ana fonksiyon"""
    print("=== ChromeDriver Kurulum Scripti ===\n")
    
    # ChromeDriver zaten kurulu mu?
    if check_chromedriver():
        print("ChromeDriver zaten kurulu!")
        return True
    
    # Chrome sürümünü al
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("❌ Chrome bulunamadı. Lütfen Google Chrome'u yükleyin.")
        return False
    
    print(f"Chrome sürümü: {chrome_version}")
    
    # ChromeDriver'ı indir ve kur
    if download_chromedriver(chrome_version):
        print("\n🎉 ChromeDriver başarıyla kuruldu!")
        print("Artık Selenium scriptlerini çalıştırabilirsiniz.")
        return True
    else:
        print("\n❌ ChromeDriver kurulumu başarısız!")
        print("Manuel kurulum için:")
        print("1. https://chromedriver.chromium.org/ adresine gidin")
        print("2. Chrome sürümünüze uygun ChromeDriver'ı indirin")
        print("3. /usr/local/bin/ dizinine kopyalayın")
        print("4. chmod +x /usr/local/bin/chromedriver komutunu çalıştırın")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
