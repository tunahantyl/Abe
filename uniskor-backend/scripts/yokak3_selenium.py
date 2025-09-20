import time
import pandas as pd
import numpy as np
import subprocess
import shutil
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_driver():
    """Chrome WebDriver'ı ayarla"""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Debug için headless'i kapat
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Chrome WebDriver kurulumu başarısız: {e}")
        logger.info("ChromeDriver'ı manuel olarak indirmeniz gerekebilir")
        return None

def wait_for_element(driver, by, value, timeout=10):
    """Element görünene kadar bekle"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        logger.warning(f"Element bulunamadı: {value}")
        return None

def scrape_university_data(driver, university_name, university_id):
    """Tek bir üniversite için veri çek"""
    try:
        logger.info(f"Üniversite işleniyor: {university_name}")
        
        # Üniversite kutucuğuna tıkla
        university_selector = f"div[data-university-id='{university_id}']"
        university_element = wait_for_element(driver, By.CSS_SELECTOR, university_selector)
        
        if not university_element:
            logger.warning(f"Üniversite kutucuğu bulunamadı: {university_name}")
            return None
            
        # Tıklama işlemi
        driver.execute_script("arguments[0].click();", university_element)
        time.sleep(2)  # AJAX yüklenmesi için bekle
        
        # Veri tablosunu bekle
        table_selector = "table.table"  # Tablo CSS selector'ı
        table_element = wait_for_element(driver, By.CSS_SELECTOR, table_selector, timeout=15)
        
        if not table_element:
            logger.warning(f"Veri tablosu bulunamadı: {university_name}")
            return None
            
        # Tabloyu pandas DataFrame'e çevir
        html_content = table_element.get_attribute('outerHTML')
        tables = pd.read_html(html_content, thousands='.', decimal=',')
        
        if not tables:
            logger.warning(f"Tablo verisi okunamadı: {university_name}")
            return None
            
        table = tables[0]
        logger.info(f"Veri başarıyla çekildi: {university_name} - {len(table)} satır")
        return table
        
    except Exception as e:
        logger.error(f"Üniversite verisi çekilirken hata: {university_name} - {e}")
        return None

def get_university_list(driver):
    """Üniversite listesini al - API çağrısını yakala"""
    try:
        logger.info("Üniversite listesi alınıyor...")
        
        # Ana sayfaya git
        driver.get("https://mis.yokak.gov.tr/Perf")
        
        # Sayfa yüklenmesini bekle
        time.sleep(5)
        
        # Üniversite kutucuğunu bul ve tıkla
        logger.info("Üniversite kutucuğu aranıyor...")
        
        # Farklı selector'ları dene - daha geniş arama
        selectors = [
            "div[onclick*='university']",
            "div[onclick*='uni']", 
            "div[class*='university']",
            "div[class*='uni']",
            "div[data-university-id]",
            "div[data-universityid]",
            "div[onclick]",
            "div[class*='click']",
            "div[class*='select']",
            "div",  # Tüm div'ler
            "span", # Tüm span'ler
            "a",    # Tüm linkler
            "button", # Tüm butonlar
            "*[onclick]", # Tüm tıklanabilir elementler
            "*[class*='university']",
            "*[class*='uni']"
        ]
        
        university_element = None
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            logger.info(f"Selector '{selector}': {len(elements)} element bulundu")
            if elements and len(elements) > 0:
                # İlk elementin özelliklerini kontrol et
                first_element = elements[0]
                text = first_element.text.strip()
                onclick = first_element.get_attribute('onclick')
                class_name = first_element.get_attribute('class')
                logger.info(f"  İlk element: text='{text[:50]}...', onclick='{onclick}', class='{class_name}'")
                
                # Eğer üniversite ile ilgili bir element ise
                if ('üniversite' in text.lower() or 'university' in text.lower() or 
                    'uni' in onclick.lower() if onclick else False or
                    'university' in onclick.lower() if onclick else False or
                    'fa-university' in class_name.lower()):
                    logger.info(f"Üniversite elementi bulundu: {selector}")
                    university_element = first_element
                    break
        
        if not university_element:
            logger.error("Üniversite kutucuğu bulunamadı!")
            return []
        
        # Kutucuğa tıkla
        logger.info("Üniversite kutucuğuna tıklanıyor...")
        driver.execute_script("arguments[0].click();", university_element)
        time.sleep(5)  # Daha uzun bekle
        
        # Sayfa kaynağını kontrol et - üniversite listesi yüklendi mi?
        logger.info("Üniversite listesi yüklenmesi bekleniyor...")
        page_source = driver.page_source
        
        # Üniversite isimlerini sayfa kaynağından bul
        universities = []
        
        # JSON formatında üniversite listesi ara
        import json
        try:
            # Sayfa kaynağında JSON data ara
            json_pattern = r'\{[^{}]*"items"[^{}]*\[[^\]]*\][^{}]*\}'
            json_matches = re.findall(json_pattern, page_source, re.DOTALL)
            
            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    if 'items' in data and isinstance(data['items'], list):
                        logger.info(f"JSON data bulundu: {len(data['items'])} üniversite")
                        for item in data['items']:
                            universities.append({
                                'id': str(item.get('yoksisId', '')),
                                'name': item.get('name', ''),
                                'sno': item.get('sno', 0)
                            })
                        break
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.warning(f"JSON parsing hatası: {e}")
        
        # Eğer JSON bulunamadıysa, HTML'den arama yap
        if not universities:
            logger.info("JSON bulunamadı, HTML'den arama yapılıyor...")
            # Üniversite isimlerini HTML'den çıkar
            lines = page_source.split('\n')
            for line in lines:
                if 'üniversitesi' in line.lower() and len(line) > 10:
                    clean_line = re.sub(r'<[^>]+>', '', line).strip()
                    if clean_line and 10 < len(clean_line) < 100:
                        universities.append({
                            'id': f"html_{len(universities)}",
                            'name': clean_line,
                            'sno': len(universities) + 1
                        })
        
        if universities:
            logger.info(f"Toplam {len(universities)} üniversite bulundu")
            return universities
        else:
            logger.warning("Hiçbir yöntemle üniversite bulunamadı!")
            return []
        
    except Exception as e:
        logger.error(f"Üniversite listesi alınamadı: {e}")
        return []

def process_university_data(table, university_name, year_names):
    """Üniversite verisini işle"""
    try:
        if table is None or table.empty:
            return None
            
        # Sütun isimleri
        column_names = ["Uni"] + ["y" + str(x) for x in range(1, 14)] + ["x" + str(x) for x in range(1, 6)] + ["t" + str(x) for x in range(2)]
        column_names0 = ["Uni"] + ["y" + str(x) for x in range(1, 14)] + ["x" + str(x) for x in range(1, 6)]
        
        processed_data = {}
        
        for yy in range(len(year_names)):
            try:
                # Veri işleme (orijinal koddan)
                tab00 = [university_name] + table[year_names[yy]].iloc[[10, 57, 58, 61, 63, 70, 72, 74, 76, 12, 68, 82, 66, 48, 7, 38, 31, 83, 78, 5]].to_list()
                tab00 = pd.DataFrame(tab00).T
                tab00.columns = column_names
                tab0 = tab00[tab00.columns[:-2]].copy()
                
                # Veri dönüşümleri
                if len(tab00) > 0:
                    tab0["y3"].iloc[0] = float(tab00["y3"]) / float(tab00["t1"]) if not pd.isna(tab00["t1"].iloc[0]) else np.nan
                    tab0["x5"].iloc[0] = float(tab00["x5"]) / float(tab00["t1"]) if not pd.isna(tab00["t1"].iloc[0]) else np.nan
                    
                    # y9 hesaplama
                    if pd.isna(tab00["y9"].iloc[0]) and not pd.isna(tab00["t0"].iloc[0]):
                        tab0["y9"].iloc[0] = float(tab00["t0"])
                    elif not pd.isna(tab00["y9"].iloc[0]) and pd.isna(tab00["t0"].iloc[0]):
                        tab0["y9"].iloc[0] = float(tab00["y9"])
                    elif not pd.isna(tab00["y9"].iloc[0]) and not pd.isna(tab00["t0"].iloc[0]):
                        tab0["y9"].iloc[0] = float(tab00["t0"]) + float(tab00["y9"])
                    
                    # x4 hesaplama
                    if not pd.isna(tab00["x4"].iloc[0]):
                        if float(tab00["x4"]) > 1:
                            tab0["x4"] = float(tab00["x4"]) / 100
                        if float(tab00["x4"]) / 100 > 1:
                            tab0["x4"] = np.nan
                
                processed_data[year_names[yy]] = tab0
                
            except Exception as e:
                logger.warning(f"Yıl verisi işlenemedi {year_names[yy]}: {e}")
                continue
                
        return processed_data
        
    except Exception as e:
        logger.error(f"Üniversite verisi işlenirken hata: {e}")
        return None

def main():
    """Ana fonksiyon"""
    logger.info("YÖKAK Selenium Scraper başlatılıyor...")
    
    # WebDriver'ı başlat
    driver = setup_driver()
    if not driver:
        logger.error("WebDriver başlatılamadı!")
        return
    
    try:
        # Üniversite listesini al
        universities = get_university_list(driver)
        if not universities:
            logger.error("Üniversite listesi alınamadı!")
            return
        
        # İlk üniversiteden yıl bilgilerini al
        logger.info("Yıl bilgileri alınıyor...")
        first_uni = universities[0]
        first_table = scrape_university_data(driver, first_uni['name'], first_uni['id'])
        
        if first_table is None:
            logger.error("İlk üniversite verisi alınamadı!")
            return
            
        year_names = first_table.columns[1:]  # İlk sütun üniversite adı
        logger.info(f"Bulunan yıllar: {list(year_names)}")
        
        # Tüm üniversiteler için veri toplama
        all_data = {}
        for year in year_names:
            all_data[year] = pd.DataFrame()
        
        # İlk üniversiteyi işle
        first_data = process_university_data(first_table, first_uni['name'], year_names)
        if first_data:
            for year, data in first_data.items():
                all_data[year] = pd.concat([all_data[year], data], ignore_index=True)
        
        # Diğer üniversiteleri işle
        for i, uni in enumerate(universities[1:], 1):
            logger.info(f"İşleniyor: {i}/{len(universities)} - {uni['name']}")
            
            table = scrape_university_data(driver, uni['name'], uni['id'])
            if table is not None:
                processed_data = process_university_data(table, uni['name'], year_names)
                if processed_data:
                    for year, data in processed_data.items():
                        all_data[year] = pd.concat([all_data[year], data], ignore_index=True)
            
            # Rate limiting
            time.sleep(1)
        
        # Excel dosyalarına kaydet
        logger.info("Excel dosyaları oluşturuluyor...")
        
        column_names0 = ["Uni"] + ["y" + str(x) for x in range(1, 14)] + ["x" + str(x) for x in range(1, 6)]
        
        with pd.ExcelWriter('Hamveri 26102024.xlsx') as writer:
            for year, df in all_data.items():
                if not df.empty:
                    df[column_names0[1:]] = df[column_names0[1:]].apply(pd.to_numeric, errors='coerce')
                    df.to_excel(writer, sheet_name=str(year), engine='openpyxl', index=False)
        
        with pd.ExcelWriter('Hamveri Translog 26102024.xlsx') as writer:
            for year, df in all_data.items():
                if not df.empty:
                    df[column_names0[1:]] = df[column_names0[1:]].apply(pd.to_numeric, errors='coerce')
                    for zz in range(1, 19):
                        if zz < len(column_names0):
                            df[column_names0[zz]] = df[column_names0[zz]].div(df[column_names0[zz]].mean())
                    df.to_excel(writer, sheet_name=str(year), engine='openpyxl', index=False)
        
        logger.info("Excel dosyaları başarıyla oluşturuldu!")
        
        # R script'ini çalıştır
        logger.info("R analizi başlatılıyor...")
        r_path = shutil.which("Rscript") or shutil.which("Rscript.exe")
        script_path = "Etkinlik_skorlari.R"
        arg = '0'
        
        if r_path:
            cmd = [r_path, script_path, arg]
            result = subprocess.run(cmd, universal_newlines=True)
            logger.info("R analizi tamamlandı")
        else:
            logger.warning("Rscript bulunamadı. R analizi atlandı.")
        
    except Exception as e:
        logger.error(f"Ana işlem sırasında hata: {e}")
    finally:
        driver.quit()
        logger.info("WebDriver kapatıldı")

if __name__ == "__main__":
    main()
