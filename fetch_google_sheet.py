#!/usr/bin/env python3
"""
Скрипт для автоматичного оновлення даних з Google Таблиці
ФІНАЛЬНА ВЕРСІЯ — коректна обробка відсотків з Google Sheets
"""

import pandas as pd
import json
import sys
import traceback

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQOxz-ozH9yNLW3IAzlkMlbRqOTrR4sIUO1__KpAMBFEvvpMXr4LWTnRvzYGb_y6za7WBxOUhl2DV84/pub?output=csv"

PERCENT_COLUMNS = ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС']

def clean_number(value):
    if pd.isna(value):
        return 0.0

    str_val = str(value).strip().replace(' ', '').replace('\xa0', '')

    if not str_val or str_val.lower() in ['nan', 'none']:
        return 0.0

    # ✅ ОБРОБКА ВІДСОТКІВ ЯК ТЕКСТУ: "14.41%" або "14,41%"
    if '%' in str_val:
        str_val = str_val.replace('%', '').replace(',', '.')
        try:
            return float(str_val)
        except:
            return 0.0

    # Європейський / американський формат чисел
    if ',' in str_val and '.' in str_val:
        if str_val.rfind(',') > str_val.rfind('.'):
            str_val = str_val.replace('.', '').replace(',', '.')
        else:
            str_val = str_val.replace(',', '')

    elif ',' in str_val:
        if len(str_val.split(',')[-1]) == 3:
            str_val = str_val.replace(',', '')
        else:
            str_val = str_val.replace(',', '.')

    elif '.' in str_val:
        if len(str_val.split('.')[-1]) == 3:
            str_val = str_val.replace('.', '')

    try:
        return float(str_val)
    except:
        return 0.0


def fetch_and_convert():
    df = pd.read_csv(GOOGLE_SHEET_URL, dtype=str)
    df = df.dropna(how='all').reset_index(drop=True)

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

        initials = ''.join(x[0] for x in name.split()[:2]).upper()
        position = str(row.get('Посада', 'Менеджер'))

        metrics = {}

        for col in df.columns[2:]:
            raw = row.get(col)
            num = clean_number(raw)

            if col in PERCENT_COLUMNS:
                # ✅ якщо прийшло 0.1441 → робимо 14.41
                if num <= 1:
                    num = num * 100
                value = round(num, 2)
                unit = '%'

            elif col in ['Шт.', 'Чеки', 'ПЧ']:
                value = int(num)
                unit = 'шт'

            elif col in ['ТО', 'ASP', 'Ср. Чек', 'ACC', 'Послуги грн', 'УДС']:
                value = round(num, 2)
                unit = 'грн'

            else:
                value = round(num, 2)
                unit = ''

            metrics[col] = {
                'value': value,
                'label': col,
                'unit': unit
            }

        sales_data.append({
            'id': len(sales_data) + 1,
            'name': name,
            'position': position,
            'initials': initials,
            'gradient': gradients[len(sales_data) % len(gradients)],
            'metrics': metrics
        })

    store_totals = {
        'id': 0,
        'name': 'Загальні показники магазину',
        'position': 'Всі продавці',
        'initials': 'МАГ',
        'gradient': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
        'metrics': {}
    }

    for col in df.columns[2:]:
        values = [p['metrics'][col]['value'] for p in sales_data]

        if col in PERCENT_COLUMNS:
            avg = round(sum(values) / len(values), 2)
            store_totals['metrics'][col] = {'value': avg, 'label': col, 'unit': '%'}
        elif col in ['Шт.', 'Чеки', 'ПЧ']:
            store_totals['metrics'][col] = {'value': int(sum(values)), 'label': col, 'unit': 'шт'}
        else:
            store_totals['metrics'][col] = {'value': round(sum(values), 2), 'label': col, 'unit': 'грн'}

    all_data = [store_totals] + sales_data

    with open('sales-data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("✅ JSON оновлено правильно (відсотки працюють коректно)")


if __name__ == "__main__":
    try:
        fetch_and_convert()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
