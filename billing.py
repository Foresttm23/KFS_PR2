import mysql.connector
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def process_reading(data):
    conn = get_connection()
    cursor = conn.cursor()

    type = data['type']


    if type == 'tariffs':
        day_tariff = data['day_tariff']
        night_tariff = data['night_tariff']
        day_adjustment = data['day_adjustment']
        night_adjustment = data['night_adjustment']

        cursor.execute('INSERT INTO tariffs (day_tariff, night_tariff, day_adjustment, night_adjustment) VALUES (%s, %s, %s, %s)', (day_tariff, night_tariff, day_adjustment, night_adjustment))
        print(f'Нові тарифи вставлено {day_tariff, night_tariff, day_adjustment, night_adjustment}')
    
    if type == 'insert':
        meter_id = data['meter_id']
        day_reading = data['day_reading']
        night_reading = data['night_reading']

        cursor.execute('SELECT * FROM meters_history WHERE meter_id = %s ORDER BY id DESC LIMIT 1', (meter_id,)) # (meter_id,)
        result = cursor.fetchone()

        if result:
            prev_day_reading = result[2]
            prev_night_reading = result[3]

            cursor.execute('SELECT * FROM tariffs ORDER BY id DESC LIMIT 1')
            tariffs = cursor.fetchone()

            DAY_TARIFF = tariffs[1]
            NIGHT_TARIFF = tariffs[2]
            DAY_ADJUSTMENT = tariffs[3]
            NIGHT_ADJUSTMENT = tariffs[4]

            if day_reading < prev_day_reading:
                day_reading = prev_day_reading + DAY_ADJUSTMENT

            if night_reading < prev_night_reading:
                night_reading = prev_night_reading + NIGHT_ADJUSTMENT

            day_usage = day_reading - prev_day_reading
            night_usage = night_reading - prev_night_reading


            bill = (day_usage * DAY_TARIFF) + (night_usage * NIGHT_TARIFF)

            bill = round (bill, 2)

            cursor.execute('INSERT INTO meters_history (meter_id, day_reading, night_reading, bill) VALUES (%s, %s, %s, %s)', (meter_id, day_reading, night_reading, bill))

            print(f'Bill for meter {meter_id}: {bill}')

        else:
            cursor.execute('INSERT INTO meters_history (meter_id, day_reading, night_reading, bill) VALUES (%s, %s, %s, %s)', (meter_id, day_reading, night_reading, 0))

            print(f'New meter {meter_id} added')

    if type == 'update':
        cursor.execute('UPDATE meters_history SET day_reading = %s, night_reading = %s, bill = %s WHERE id = %s', (data['day_reading_update'], data['night_reading_update'],data['bill_update'], data['id_update']))


    if type == 'delete':
        cursor.execute('DELETE FROM meters_history WHERE id = %s', (data['id_delete'],))

    
    conn.commit()
    conn.close()