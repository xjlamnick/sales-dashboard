#!/usr/bin/env python3
"""
Скрипт для автоматичного оновлення даних з Google Таблиці (РОБОЧИЙ!)
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
        # Читаємо з header=0 і очищуємо назви колонок
        df = pd.read_csv(GOOGLE_SHEET_URL, header=0)
        
        # ✅ КРИТИЧНО: ДРУКУЄМО РЕАЛЬНІ КОЛОНКИ
        print("🔍 РЕАЛЬНІ назви колонок:", [repr(col) for col in df.columns.tolist()])
        print("📊 Перший рядок даних:", df.iloc[0].to_dict())
        
        print(f"✅ Завантажено {len(df)} рядків, {len(df.columns)} стовпців")
        
        # Градієнти
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
        
        # ✅ АВТОПШУК: перша колонка = імена (ПК), друга = посади
        name_col = df.columns[0]   # Перша колонка — ПК
        pos_col = df.columns[1]    # Друга колонка — Посада
        
        print(f"🎯 Використовуємо колонки: '{name_col}' (ПК), '{pos_col}' (Посада)")
        
        # Автоматично визначаємо колонку з іменами продавців
name_column = None
position_column = None

# Шукаємо першу колонку, яка не є числовою і має довгі рядки (імена)
for col in df.columns:
    first_val = str(df[col].iloc[0]).strip()
    if len(first_val) > 5 and ' ' in first_val:  # ймовірно ім'я + прізвище
        name_column = col
        break

if name_column is None:
    # якщо не знайшли — беремо першу колонку
    name_column = df.columns[0]

# Друга колонка — зазвичай посада
position_column = df.columns[1] if len(df.columns) > 1 else None

print(f"Використовуємо колонку для імен: '{name_column}'")
print(f"Використовуємо колонку для посад: '{position_column}'")

sales_data = []

for idx, row in df.iterrows():
    name = str(row[name_column]).strip()
    if not name or name.lower() in ['пк', 'посада', 'заголовок', '']:
        continue  # пропускаємо заголовки або порожні рядки

    # Генеруємо ініціали
    name_parts = name.split()
    initials = ''.join([p[0] for p in name_parts[:2]]).upper() if len(name_parts) >= 2 else name[0].upper()

    # позиція
    position = str(row.get(position_column, 'продавець-консультант')).strip() if position_column else 'продавець-консультант'

    # метрики — всі колонки після другої
    metrics = {}
    start_idx = 2 if position_column else 1
    for col in df.columns[start_idx:]:
        val = row.get(col)
        if pd.isna(val):
            val = 0

        col_clean = str(col).strip()

        # логіка визначення формату (можна залишити як була)
        if col_clean in ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС'] or '%' in col_clean or 'Доля' in col_clean or 'Конверсія' in col_clean:
            value = round(float(val) * 100, 2) if pd.notna(val) else 0
            unit = '%'
        elif col_clean in ['Шт.', 'Чеки', 'ПЧ'] or 'шт' in col_clean.lower():
            value = int(float(val)) if pd.notna(val) else 0
            unit = 'шт'
        elif col_clean in ['ТО', 'ASP', 'Ср. Чек', 'ACC', 'Послуги грн', 'УДС'] or 'грн' in col_clean.lower():
            value = round(float(val), 2) if pd.notna(val) else 0
            unit = 'грн'
        else:
            value = round(float(val), 2) if pd.notna(val) else 0
            unit = ''

        metrics[col_clean] = {'value': value, 'label': col_clean, 'unit': unit}

    person = {
        'id': len(sales_data) + 1,
        'name': name,
        'position': position,
        'initials': initials,
        'gradient': gradients[len(sales_data) % len(gradients)],
        'metrics': metrics
    }
    sales_data.append(person)
        
        # Загальні показники магазину (суми/середні)
        store_totals = {
            'id': 0,
            'name': 'Загальні показники магазину',
            'position': 'Всі продавці',
            'initials': 'МАГ',
            'gradient': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
            'metrics': {}
        }
        
        metric_cols = [str(col).strip() for col in df.columns[2:]]
        for col in metric_cols:
            values = [p['metrics'].get(col, {'value': 0})['value'] for p in sales_data]
            if any('%' in col or 'Доля' in col or 'Конверсія' in col):
                avg = round(sum(values) / len(values), 2) if values else 0
                store_totals['metrics'][col] = {'value': avg, 'label': col, 'unit': '%'}
            elif any(x in col for x in ['Шт.', 'Чеки', 'ПЧ']):
                total = sum(values)
                store_totals['metrics'][col] = {'value': int(total), 'label': col, 'unit': 'шт'}
            elif any(x in col for x in ['ТО', 'ASP', 'Чек', 'ACC', 'Послуги', 'УДС']):
                if 'ASP' in col or 'Чек' in col:
                    avg = round(sum(values) / len(values), 2) if values else 0
                else:
                    avg = round(sum(values), 2)
                store_totals['metrics'][col] = {'value': avg, 'label': col, 'unit': 'грн'}
            else:
                avg = round(sum(values) / len(values), 2) if values else 0
                store_totals['metrics'][col] = {'value': avg, 'label': col, 'unit': ''}
        
        all_data = [store_totals] + sales_data
        
        # Зберігаємо
        with open('sales-data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ ГОТОВО! 📊 Магазин + {len(sales_data)} продавців")
        return True
        
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🚀 ОНОВЛЕННЯ ПРОДАЖІВ З GOOGLE SHEETS")
    print("="*60 + "\n")
    
    if fetch_and_convert():
        print("\n🎉 ДАНІ ОНОВЛЕНО! Запусти GitHub Actions.")
    else:
        sys.exit(1)
