#!/usr/bin/env python3
"""
Скрипт для автоматичного оновлення даних з Google Таблиці
"""

import pandas as pd
import json
import sys
import traceback

# Публічне посилання на CSV-експорт Google Таблиці
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQOxz-ozH9yNLW3IAzlkMlbRqOTrR4sIUO1__KpAMBFEvvpMXr4LWTnRvzYGb_y6za7WBxOUhl2DV84/pub?output=csv"

def fetch_and_convert():
    """Завантажує дані з Google Таблиці та конвертує в JSON"""
    
    print("\n" + "="*70)
    print(" ОНОВЛЕННЯ ДАНИХ З GOOGLE ТАБЛИЦІ")
    print("="*70 + "\n")
    
    print(f"📥 Завантажую дані...")
    print(f"🔗 URL: {GOOGLE_SHEET_URL}\n")

    try:
        # Читаємо CSV, явно вказуємо, що перша строка — заголовки
        df = pd.read_csv(GOOGLE_SHEET_URL, header=0)
        
        # Видаляємо повністю порожні рядки
        df = df.dropna(how='all').reset_index(drop=True)
        
        print("Колонки в таблиці:", df.columns.tolist())
        print(f"Завантажено рядків: {len(df)}")
        print("\nПерші 5 значень стовпця 'ПК':")
        print(df.get('ПК', pd.Series()).head(10).tolist())
        print("-"*60)

        # Обробка числових колонок — замінюємо кому на крапку
        for col in df.columns:
            if col == 'ПК':
                # Для імені продавця — тільки очищаємо від пробілів
                df[col] = df[col].astype(str).str.strip()
            else:
                # Для всіх інших — заміна коми на крапку + спроба перетворити в число
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')

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
            if pd.notna(pk_value) and str(pk_value).strip():
                name = str(pk_value).strip()
                
                # Ініціали
                name_parts = name.split()
                initials = ''.join(p[0] for p in name_parts[:2]).upper() if len(name_parts) >= 2 else name[0].upper() if name else '?'
                
                # Посада
                position = str(row.get('Посада', 'Менеджер з продажу')).strip()

                # Метрики
                metrics = {}
                for col in df.columns[2:]:  # пропускаємо ПК і Посада
                    col_name = col.strip()
                    val = row.get(col)
                    if pd.isna(val):
                        val = 0

                    if col_name in ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС']:
                        value = round(val * 100, 2) if pd.notna(val) else 0
                        unit = '%'
                    elif col_name in ['Шт.', 'Чеки', 'ПЧ']:
                        value = int(val) if pd.notna(val) else 0
                        unit = 'шт'
                    elif col_name in ['ТО', 'ASP', 'Ср. Чек', 'ACC', 'Послуги грн', 'УДС']:
                        value = round(val, 2) if pd.notna(val) else 0
                        unit = 'грн'
                    else:
                        value = round(val, 2) if pd.notna(val) else 0
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
                print(f"Додано продавця: {name} ({initials})")

        print(f"\nУсього додано продавців: {len(sales_data)}")

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
            values = [p['metrics'][col_name]['value'] for p in sales_data if col_name in p['metrics']]

            if not values:
                store_totals['metrics'][col_name] = {'value': 0, 'label': col_name, 'unit': ''}
                continue

            if col_name in ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС']:
                avg_value = round(sum(values) / len(values), 2)
                unit = '%'
            elif col_name in ['Шт.', 'Чеки', 'ПЧ']:
                total = sum(values)
                unit = 'шт'
                store_totals['metrics'][col_name] = {'value': int(total), 'label': col_name, 'unit': unit}
                continue
            elif col_name in ['ТО', 'ACC', 'Послуги грн', 'УДС']:
                total = sum(values)
                unit = 'грн'
                store_totals['metrics'][col_name] = {'value': round(total, 2), 'label': col_name, 'unit': unit}
                continue
            else:  # ASP, Ср. Чек тощо — середнє
                avg_value = round(sum(values) / len(values), 2)
                unit = 'грн'

            store_totals['metrics'][col_name] = {'value': avg_value, 'label': col_name, 'unit': unit}

        # Збираємо всі дані: магазин першим, потім продавці
        all_data = [store_totals] + sales_data

        # Зберігаємо у файл
        with open('sales-data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Успішно збережено у sales-data.json")
        print(f" 📊 Магазин + {len(sales_data)} продавців")
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
