#!/usr/bin/env python3
"""
Скрипт для автоматичного оновлення даних з Google Таблиці
"""

import pandas as pd
import json
import sys

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQOxz-ozH9yNLW3IAzlkMlbRqOTrR4sIUO1__KpAMBFEvvpMXr4LWTnRvzYGb_y6za7WBxOUhl2DV84/pub?output=csv"

def fetch_and_convert():
    """Завантажує дані з Google Таблиці та конвертує в JSON"""
    
    print(f"📥 Завантажую дані з Google Таблиці...")
    print(f"🔗 URL: {GOOGLE_SHEET_URL}")
    
    try:
        # Читаємо таблицю — заголовки в першому рядку
        df = pd.read_csv(GOOGLE_SHEET_URL, header=0)
        
        # Діагностика — обов'язково подивіться цей рядок у логах
        print("Колонки в таблиці:", df.columns.tolist())
        
        # Замінюємо кому на крапку та перетворюємо на числа всі колонки після перших двох
        for col in df.columns[2:]:
            # Заміна коми на крапку (український формат чисел)
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            # Перетворюємо на числа, помилки → NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"✅ Завантажено {len(df)} рядків, {len(df.columns)} стовпців")
        
        # Градієнти для карток
        gradients = [
            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
            'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
            'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)'
        ]
        
        sales_data = []
        
        for idx, row in df.iterrows():
            # Перевіряємо, чи є ім'я і чи воно не порожнє
            if pd.notna(row['ПК']) and str(row['ПК']).strip():
                name = str(row['ПК']).strip()
                
                # Генеруємо ініціали
                name_parts = name.split()
                if len(name_parts) >= 2:
                    initials = ''.join([p[0] for p in name_parts[:2]]).upper()
                else:
                    initials = name[0].upper() if name else '?'
                
                # Посада — колонка називається 'ПОСАДА' (великими)
                position = str(row['ПОСАДА']) if pd.notna(row['ПОСАДА']) else 'Менеджер з продажу'
                position = position.strip()
                
                # Метрики
                metrics = {}
                for col in df.columns[2:]:
                    val = row[col]
                    if pd.isna(val):
                        val = 0
                    
                    # Визначення формату
                    col_name = col.strip()
                    if col_name in ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС']:
                        value = round(float(val) * 100, 2) if pd.notna(val) else 0
                        unit = '%'
                    elif col_name in ['Шт.', 'Чеки', 'ПЧ']:
                        value = int(val) if pd.notna(val) else 0
                        unit = 'шт'
                    elif col_name in ['ТО', 'ASP', 'Ср. Чек', 'ACC', 'Послуги грн', 'УДС']:
                        value = round(float(val), 2) if pd.notna(val) else 0
                        unit = 'грн'
                    else:
                        value = round(float(val), 2) if pd.notna(val) else 0
                        unit = ''
                    
                    metrics[col_name] = {
                        'value': value,
                        'label': col_name,
                        'unit': unit
                    }
                
                person = {
                    'id': len(sales_data) + 1,
                    'name': name,
                    'position': position,
                    'initials': initials,
                    'gradient': gradients[len(sales_data) % len(gradients)],
                    'metrics': metrics
                }
                sales_data.append(person)
        
        # Загальні показники магазину
        store_totals = {
            'id': 0,
            'name': 'Загальні показники магазину',
            'position': 'Всі продавці',
            'initials': 'МАГ',
            'gradient': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
            'metrics': {}
        }

        for col in df.columns[2:]:
            col_name = col.strip()
            values = 
