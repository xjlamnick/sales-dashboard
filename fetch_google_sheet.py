#!/usr/bin/env python3
"""
Скрипт для автоматичного оновлення даних з Google Таблиці
ВИПРАВЛЕНА ВЕРСІЯ - правильно обробляє числа з роздільниками
"""

import pandas as pd
import json
import sys
import traceback
import re

# Публічне посилання на CSV-експорт Google Таблиці
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQOxz-ozH9yNLW3IAzlkMlbRqOTrR4sIUO1__KpAMBFEvvpMXr4LWTnRvzYGb_y6za7WBxOUhl2DV84/pub?output=csv"

def clean_number(value):
    """
    Розумно очищає число від різних роздільників.
    
    Підтримує формати:
    - 2.236.554,30 (європейський: крапка=тисячі, кома=десятковий)
    - 2,236,554.30 (американський: кома=тисячі, крапка=десятковий)
    - 2236554.30 (без роздільників)
    - 0.1656 (десятковий дріб)
    """
    if pd.isna(value):
        return 0.0
    
    # Конвертуємо в рядок
    str_val = str(value).strip()
    
    # Порожнє значення
    if not str_val or str_val.lower() in ['nan', 'none', '']:
        return 0.0
    
    # Видаляємо пробіли
    str_val = str_val.replace(' ', '').replace('\xa0', '')
    
    # Якщо немає роздільників - просто конвертуємо
    if ',' not in str_val and '.' not in str_val:
        try:
            return float(str_val)
        except:
            return 0.0
    
    # Визначаємо формат
    # Якщо є обидва роздільники
    if ',' in str_val and '.' in str_val:
        last_comma = str_val.rfind(',')
        last_dot = str_val.rfind('.')
        
        if last_comma > last_dot:
            # Формат: 2.236.554,30 (європейський)
            # Крапка = тисячі, кома = десятковий
            str_val = str_val.replace('.', '').replace(',', '.')
        else:
            # Формат: 2,236,554.30 (американський)
            # Кома = тисячі, крапка = десятковий
            str_val = str_val.replace(',', '')
    
    # Якщо тільки кома
    elif ',' in str_val:
        parts = str_val.split(',')
        # Якщо після коми 3 цифри - це тисячний роздільник
        # Інакше - десятковий
        if len(parts[-1]) == 3 and len(parts) > 1:
            # Тисячний: 2,236 або 2,236,554
            str_val = str_val.replace(',', '')
        else:
            # Десятковий: 0,1656 або 2,50
            str_val = str_val.replace(',', '.')
    
    # Якщо тільки крапка
    elif '.' in str_val:
        parts = str_val.split('.')
        # Якщо після крапки 3 цифри - це тисячний роздільник
        # Інакше - десятковий
        if len(parts[-1]) == 3 and len(parts) > 1 and len(parts[0]) <= 3:
            # Тисячний: 2.236 або 2.236.554
            str_val = str_val.replace('.', '')
        # else: залишаємо як є - це десятковий роздільник
    
    try:
        return float(str_val)
    except:
        return 0.0


def fetch_and_convert():
    """Завантажує дані з Google Таблиці та конвертує в JSON"""
    
    print("\n" + "="*70)
    print(" ОНОВЛЕННЯ ДАНИХ З GOOGLE ТАБЛИЦІ")
    print("="*70 + "\n")
    
    print(f"📥 Завантажую дані...")
    print(f"🔗 URL: {GOOGLE_SHEET_URL}\n")

    try:
        # Читаємо CSV без автоматичної конвертації типів
        df = pd.read_csv(GOOGLE_SHEET_URL, header=0, dtype=str)
        
        # Видаляємо повністю порожні рядки
        df = df.dropna(how='all').reset_index(drop=True)
        
        print(f"✅ Завантажено {len(df)} рядків, {len(df.columns)} стовпців")
        print(f"📋 Колонки: {', '.join(df.columns[:5])}...\n")

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

        # Обробка кожного рядка
        for idx, row in df.iterrows():
            pk_value = row.get('ПК')
            
            # Перевіряємо, чи є ім'я
            if pd.notna(pk_value) and str(pk_value).strip() and str(pk_value).strip().lower() != 'nan':
                name = str(pk_value).strip()
                
                # Ініціали
                name_parts = name.split()
                initials = ''.join(p[0] for p in name_parts[:2]).upper() if len(name_parts) >= 2 else (name[0].upper() if name else '?')
                
                # Посада
                position_val = row.get('Посада', 'Менеджер з продажу')
                position = str(position_val).strip() if pd.notna(position_val) else 'Менеджер з продажу'

                # Метрики
                metrics = {}
                for col in df.columns[2:]:  # пропускаємо ПК і Посада
                    col_name = col.strip()
                    raw_val = row.get(col)
                    
                    # Очищаємо число
                    num_val = clean_number(raw_val)

                    # Визначаємо одиниці та формат
                    if col_name in ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС']:
                        # Якщо число вже у відсотках (>1), не множимо
                        if num_val > 1:
                            value = round(num_val, 2)
                        else:
                            value = round(num_val * 100, 2)
                        unit = '%'
                    elif col_name in ['Шт.', 'Чеки', 'ПЧ']:
                        value = int(num_val)
                        unit = 'шт'
                    elif col_name in ['ТО', 'ASP', 'Ср. Чек', 'ACC', 'Послуги грн', 'УДС']:
                        value = round(num_val, 2)
                        unit = 'грн'
                    else:
                        value = round(num_val, 2)
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
                to_value = metrics.get('ТО', {}).get('value', 0)
                print(f"✓ {name[:30]:30s} (ТО: {to_value:>12,.0f} грн)")

        print(f"\n📊 Усього продавців: {len(sales_data)}")

        if len(sales_data) == 0:
            print("\n⚠️  УВАГА: Не знайдено жодного продавця!")
            print("Перевірте структуру таблиці.")
            return False

        # Загальні показники магазину
        store_totals = {
            'id': 0,
            'name': 'Загальні показники магазину',
            'position': 'Всі продавці',
            'initials': 'МАГ',
            'gradient': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
            'metrics': {}
        }

        # Підсумовуємо метрики
        for col in df.columns[2:]:
            col_name = col.strip()
            values = [p['metrics'][col_name]['value'] for p in sales_data if col_name in p['metrics']]

            if not values:
                store_totals['metrics'][col_name] = {'value': 0, 'label': col_name, 'unit': ''}
                continue

            if col_name in ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС']:
                # Середнє для відсотків
                avg_value = round(sum(values) / len(values), 2)
                store_totals['metrics'][col_name] = {'value': avg_value, 'label': col_name, 'unit': '%'}
            elif col_name in ['Шт.', 'Чеки', 'ПЧ']:
                # Сума для штук
                total = int(sum(values))
                store_totals['metrics'][col_name] = {'value': total, 'label': col_name, 'unit': 'шт'}
            elif col_name in ['ТО', 'ACC', 'Послуги грн', 'УДС']:
                # Сума для грошових показників
                total = round(sum(values), 2)
                store_totals['metrics'][col_name] = {'value': total, 'label': col_name, 'unit': 'грн'}
            else:
                # Середнє для інших (ASP, Ср. Чек, КПЧ)
                avg_value = round(sum(values) / len(values), 2)
                unit = sales_data[0]['metrics'].get(col_name, {}).get('unit', '')
                store_totals['metrics'][col_name] = {'value': avg_value, 'label': col_name, 'unit': unit}

        total_to = store_totals['metrics'].get('ТО', {}).get('value', 0)
        print(f"\n💰 Загальний товарообіг: {total_to:,.2f} грн")

        # Збираємо всі дані
        all_data = [store_totals] + sales_data

        # Зберігаємо
        with open('sales-data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Успішно збережено у sales-data.json")
        print(f"📦 Магазин + {len(sales_data)} продавців")
        print("="*70 + "\n")
        
        return True

    except Exception as e:
        print(f"\n❌ КРИТИЧНА ПОМИЛКА: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = fetch_and_convert()
    if not success:
        sys.exit(1)
