#!/usr/bin/env python3
"""
Скрипт для автоматичного оновлення даних з Google Таблиці
ФІНАЛЬНА ВЕРСІЯ — коректна обробка відсотків з Google Sheets
"""

import pandas as pd
import json
import sys
import traceback

# URL CSV з Google Sheets
BASE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRxPqHp5lwwhjdDTaJdiwWYbhqZmeALG5dVhSZ6rHx2W8KGrcNWaa5-7qiVB87KKbQEXjtF1WVwmBzp/pub?gid=50416606&single=true&output=csv"

# Колонки, що містять відсотки
PERCENT_COLUMNS = ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС']

# Функція очищення чисел та відсотків
def clean_number(value):
    if pd.isna(value):
        return 0.0
    s = str(value).strip().replace(' ', '').replace('\xa0', '')
    if not s or s.lower() in ['nan', 'none']:
        return 0.0
    if '%' in s:
        s = s.replace('%', '').replace(',', '.')
        try:
            return float(s)
        except:
            return 0.0
    if ',' in s and '.' in s:
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s:
        if len(s.split(',')[-1]) == 3:
            s = s.replace(',', '')
        else:
            s = s.replace(',', '.')
    try:
        return float(s)
    except:
        return 0.0

# Завантаження CSV
def fetch_csv_data(url):
    try:
        df = pd.read_csv(url, dtype=str)
        df = df.dropna(how='all').reset_index(drop=True)
        print(f"✅ CSV завантажено: {df.shape[0]} рядків, {df.shape[1]} колонок")
        return df
    except Exception as e:
        print(f"❌ Помилка завантаження CSV: {e}")
        traceback.print_exc()
        sys.exit(1)

# Обробка даних
def process_data(df):
    gradients = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
    ]
    sales_data = []
    for idx, row in df.iterrows():
        name = str(row.get('ПК', '')).strip()
        if not name:
            continue
        initials = ''.join([w[0] for w in name.split()[:2]]).upper() if len(name.split()) >= 2 else name[:2].upper()
        position = str(row.get('Посада', 'Менеджер'))
        metrics = {}
        for col in df.columns:
            raw = row.get(col)
            val = clean_number(raw)
            if col in PERCENT_COLUMNS:
                if 0 < val <= 1:
                    val *= 100
                metrics[col] = {'value': round(val, 2), 'unit': '%'}
            elif col in ['Шт.', 'Чеки', 'ПЧ']:
                metrics[col] = {'value': int(val), 'unit': 'шт'}
            else:
                metrics[col] = {'value': round(val, 2), 'unit': 'грн'}
        sales_data.append({
            'name': name,
            'position': position,
            'initials': initials,
            'gradient': gradients[len(sales_data) % len(gradients)],
            'metrics': metrics
        })
    return sales_data

# Загальні підсумки
def compute_store_totals(df, sales_data):
    store_totals = {
        'name': 'Загальні показники магазину',
        'position': 'Всі продавці',
        'initials': 'МАГ',
        'metrics': {}
    }
    for col in df.columns:
        vals = [s['metrics'][col]['value'] for s in sales_data if col in s['metrics']]
        if col in PERCENT_COLUMNS:
            store_totals['metrics'][col] = {'value': round(sum(vals)/len(vals),2) if vals else 0, 'unit':'%'}
        elif col in ['Шт.', 'Чеки', 'ПЧ']:
            store_totals['metrics'][col] = {'value': sum(vals), 'unit':'шт'}
        else:
            store_totals['metrics'][col] = {'value': round(sum(vals),2), 'unit':'грн'}
    return store_totals

# Збереження JSON
def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📄 JSON збережено: {filename}")

# Головна функція
def main():
    df = fetch_csv_data(BASE_CSV_URL)
    sales_data = process_data(df)
    store_totals = compute_store_totals(df, sales_data)
    all_data = [store_totals] + sales_data
    save_json(all_data, 'sales-data.json')

if __name__ == "__main__":
    main()
