#!/usr/bin/env python3
"""
Скрипт для автоматичного оновлення даних з Google Таблиці
ФІНАЛЬНА ВЕРСІЯ — коректна обробка відсотків з Google Sheets
"""

import pandas as pd
import json
import sys
import traceback

GOOGLE_SHEET_URL = "#!/usr/bin/env python3
"""
Скрипт для автоматичного оновлення даних з Google Таблиці
(тестуємо CSV з pub?output=csv)
"""

import pandas as pd
import json
import sys
import traceback

# ============================================
# НАЛАШТУВАННЯ
# ============================================

# Твій CSV URL (публічний, export=csv)
BASE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRxPqHp5lwwhjdDTaJdiwWYbhqZmeALG5dVhSZ6rHx2W8KGrcNWaa5-7qiVB87KKbQEXjtF1WVwmBzp/pub?gid=50416606&single=true&output=csv"

# Якщо в таблиці кілька аркушів у вигляді CSV + формули → там може бути лише один CSV
# Тож тут ми читаємо весь CSV як один
# Якщо треба інші аркуші — треба експортувати кожен окремо.

PERCENT_COLUMNS = ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС']


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


def fetch_csv_data(url):
    """Завантажує CSV у DataFrame"""
    print(f"📥 Завантаження CSV з URL:\n   {url}\n")
    try:
        df = pd.read_csv(url, dtype=str)
        print(f"✅ CSV завантажено: {df.shape[0]} рядків, {df.shape[1]} колонок\n")
        return df
    except Exception as e:
        print(f"❌ Помилка при завантаженні CSV: {e}")
        traceback.print_exc()
        return None


def process_main_data(df):
    """Обробка основних даних продавців"""
    sales_data = []
    gradients = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
    ]

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


def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📄 Збережено: {filename}\n")


def main():
    try:
        df_main = fetch_csv_data(BASE_CSV_URL)
        if df_main is None:
            print("❌ Нема даних для обробки.")
            return

        sales_data = process_main_data(df_main)

        # Загальні показники магазину
        store_totals = {
            'name': 'Загальні показники магазину',
            'position': 'Всі продавці',
            'initials': 'МАГ',
            'metrics': {}
        }
        for col in df_main.columns:
            vals = [s['metrics'][col]['value'] for s in sales_data if col in s['metrics']]
            if col in PERCENT_COLUMNS:
                avg = round(sum(vals) / len(vals), 2) if vals else 0
                store_totals['metrics'][col] = {'value': avg, 'unit': '%'}
            elif col in ['Шт.', 'Чеки', 'ПЧ']:
                store_totals['metrics'][col] = {'value': sum(vals), 'unit': 'шт'}
            else:
                store_totals['metrics'][col] = {'value': round(sum(vals), 2), 'unit': 'грн'}

        all_data = [store_totals] + sales_data

        save_json(all_data, 'sales-data.json')

    except Exception as e:
        print("❌ Критична помилка:", e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
"

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
