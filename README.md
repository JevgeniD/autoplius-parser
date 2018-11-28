# autoplius-parser
Script to parse cars data from Auto-Plius (https://ru.autoplius.lt)

### How it works
1. Connect to autoplius.lt
2. Get the following data from pre-defined URL (e.g, 'https://ru.autoplius.lt/objavlenija/b-u-avtomobili?make_date_from=2011&sell_price_to=15000&fuel_id=32&make_id_list=67&make_id%5B67%5D=682&slist=636345659&order_by=3&order_direction=DESC'):
    - ID
    - Марка
    - Модель
    - Дата выпуска
    - Объем двигателя
    - Тип топлива
    - Коробка передач
    - Мощность (кВт)
    - Тип кузова
    - Пробег (км)
    - Страна первичной регистрации
    - Стоимость
    - Телефон продавца
    - Местонахождение
    - Ссылка
3. Save collected information to `result.csv`

### How to execute locally
```
python3 -m pip install -r reqs.txt
python3 parser.py
```