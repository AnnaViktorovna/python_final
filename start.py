import os
import csv
import time
import pandas as pd
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

scraped_cities = set()
if os.path.exists("weather_data.csv"):
    try:
        df_old = pd.read_csv("weather_data.csv")
        scraped_cities = set(df_old['City'].tolist())
        print(f"Find {len(scraped_cities)} cities")
    except Exception as e:
        print(f"Error reading CSV: {e}")

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
options.page_load_strategy = 'eager'

driver = None
data = []

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)

    driver.get("https://www.timeanddate.com/weather/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.zebra.fw.tb-theme"))
    )
    time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, "table.zebra.fw.tb-theme tbody tr")

    for row in rows:
        try:
            city = row.find_element(By.TAG_NAME, "a").text.strip()

            if city in scraped_cities:
                continue

            link = row.find_element(By.TAG_NAME, "a").get_attribute("href")

            try:
                temp = row.find_element(By.CSS_SELECTOR, "td.rbi").text.strip()
            except:
                temp = "N/A"

            try:
                condition = row.find_element(By.TAG_NAME, "img").get_attribute("alt")
            except:
                condition = "N/A"

            data.append({
                "City": city,
                "Temperature": temp,
                "Condition": condition,
                "Link": link
            })

        except Exception as e:
            print(f"Error processing row: {e}")
            continue

except KeyboardInterrupt:
    print("\nInterrupted by user")
except Exception as e:
    print(f"\nError: {e}")
finally:
    if driver:
        driver.quit()


if data:
    df_new = pd.DataFrame(data)

    if os.path.exists("weather_data.csv"):
        df_new.to_csv("weather_data.csv", mode='a', header=False, index=False)
        print(f"Add {len(data)} new data")
    else:
        df_new.to_csv("weather_data.csv", index=False)
        print(f"Save {len(data)} data")

    print(df_new)
else:
    print("No new data")