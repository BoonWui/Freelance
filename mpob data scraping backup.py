# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 10:41:20 2026

@author: BWLAU
"""

import json
import csv
import requests

# Proxy settings
proxies = {
    "http": 
    "https": 
}

# Month list
months = [
    "jan", "feb", "mac", "apr", "mei", "jun",
    "jul", "ogo", "sep", "okt", "nov", "dis"
]

# Loop through 2024 and 2025
for year in range(2025, 2026):  # 2024 and 2025 included
    for month in months:
        url = f'https://prestasisawit.mpob.gov.my/api/bts?year={year}&month={month}'
        r = requests.get(url, proxies=proxies, timeout=30)
        r.raise_for_status()  # stop if API fails

        data = r.json()
        district_data = data['district_data']

        # open CSV file for writing
        file_path = f'Z:\\MPOB Data\\BTS_district\\{year}{month}.csv'
        with open(file_path, 'w', newline='', encoding='utf-8') as data_file:
            csv_writer = csv.writer(data_file)

            # write header + rows
            for i, row in enumerate(district_data):
                if i == 0:
                    csv_writer.writerow(row.keys())  # header
                csv_writer.writerow(row.values())   # data

        print(f"Saved: {year}{month}.csv")
