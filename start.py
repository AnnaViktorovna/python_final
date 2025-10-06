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

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.timeanddate.com/weather/")
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "table.zebra.fw.tb-theme"))
)

rows = driver.find_elements(By.CSS_SELECTOR, "table.zebra.fw.tb-theme tbody tr")

data = []

for row in rows:
    try:
        link = row.find_element(By.TAG_NAME, "a")
        city = link.text.strip()
        url_city = link.get_attribute("href")

        temp_td = row.find_element(By.CSS_SELECTOR, "td.rbi")
        temp = temp_td.text.strip()


        img = row.find_element(By.TAG_NAME, "img")
        condition = img.get_attribute("alt")


        data.append({
            "City": city,
            "Temperature": temp,
            "Condition": condition,
            "Link": url_city
        })
    except Exception:
        continue

driver.quit()

df = pd.DataFrame(data)
df.to_csv("weather_data.csv", index=False)

print(df.head())