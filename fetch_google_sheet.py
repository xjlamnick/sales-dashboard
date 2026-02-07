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
        # Важливо: header=0, бо заголовки знаходяться в першому рядку
        df = pd.read_csv(GOOGLE_SHEET_URL, header=0)
        
        # Друк колонок для перевірки (можна видалити після тестування)
        print("Колонки в таблиці:", df.columns.tolist())
        
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
            # Перевіряємо, чи є значення в колонці 'ПК' і чи воно не порожнє
            if pd.notna(row.get('ПК')) and str(row.get('ПК')).strip():
                name = str(row['ПК']).strip()
                
                # Генеруємо ініціали
                name_parts = name.split()
                if len(name_parts) >= 2:
                    initials = ''.join([p[0] for p in name_parts[:2]]).upper()
                else:
                    initials = name[0].upper() if name else '?'
                
                # Створюємо метрики
                metrics = {}
                for col in df.columns[2:]:  # починаємо з третьої колонки (після ПК і Посада)
                    val = row.get(col)
                    
                    if pd.isna(val):
                        val = 0
                    
                    # Визначаємо тип даних і формат
                    if col in ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС']:
                        value = round(float(val) * 100, 2) if pd.notna(val) else 0
                        unit = '%'
                    elif col in ['Шт.', 'Чеки', 'ПЧ']:
                        value = int(float(val)) if pd.notna(val) else 0
                        unit = 'шт'
                    elif col in ['ТО', 'ASP', 'Ср. Чек', 'ACC', 'Послуги грн', 'УДС']:
                        value = round(float(val), 2) if pd.notna(val) else 0
                        unit = 'грн'
                    else:
                        value = round(float(val), 2) if pd.notna(val) else 0
                        unit = ''
                    
                    metrics[col] = {
                        'value': value,
                        'label': col,
                        'unit': unit
                    }
                
                person = {
                    'id': len(sales_data) + 1,
                    'name': name,
                    'position': str(row.get('Посада', 'Менеджер з продажу')),
                    'initials': initials,
                    'gradient': gradients[len(sales_data) % len(gradients)],
                    'metrics': metrics
                }
                sales_data.append(person)
        
        # Рахуємо загальні показники магазину
        store_totals = {
            'id': 0,
            'name': 'Загальні показники магазину',
            'position': 'Всі продавці',
            'initials': 'МАГ',
            'gradient': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
            'metrics': {}
        }

        # Підсумовуємо / середні значення
        for col in df.columns[2:]:
            if col in ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС']:
                values = [p['metrics'][col]['value'] for p in sales_data if col in p['metrics']]
                avg_value = round(sum(values) / len(values), 2) if values else 0
                store_totals['metrics'][col] = {'value': avg_value, 'label': col, 'unit': '%'}
            elif col in ['Шт.', 'Чеки', 'ПЧ']:
                total = sum([p['metrics'][col]['value'] for p in sales_data if col in p['metrics']])
                store_totals['metrics'][col] = {'value': int(total), 'label': col, 'unit': 'шт'}
            elif col in ['ТО', 'ASP', 'Ср. Чек', 'ACC', 'Послуги грн', 'УДС']:
                if col in ['ASP', 'Ср. Чек']:
                    values = [p['metrics'][col]['value'] for p in sales_data if col in p['metrics']]
                    avg_value = round(sum(values) / len(values), 2) if values else 0
                    store_totals['metrics'][col] = {'value': avg_value, 'label': col, 'unit': 'грн'}
                else:
                    total = sum([p['metrics'][col]['value'] for p in sales_data if col in p['metrics']])
                    store_totals['metrics'][col] = {'value': round(total, 2), 'label': col, 'unit': 'грн'}
            else:
                values = [p['metrics'][col]['value'] for p in sales_data if col in p['metrics']]
                avg_value = round(sum(values) / len(values), 2) if values else 0
                store_totals['metrics'][col] = {'value': avg_value, 'label': col, 'unit': ''}
        
        # Додаємо загальні показники на початок
        all_data = [store_totals] + sales_data
        
        # Зберігаємо у файл
        with open('sales-data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Оновлено дані:")
        print(f"   📊 Магазин")
        print(f"   👥 {len(sales_data)} продавців")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  ОНОВЛЕННЯ З GOOGLE ТАБЛИЦІ")
    print("="*60 + "\n")
    
    if fetch_and_convert():
        print("\n" + "="*60)
        print("  ✅ ГОТОВО!")
        print("="*60 + "\n")
    else:
        sys.exit(1)
