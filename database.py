import mysql.connector
from config import DB_CONFIG, DEFAULT_DAY_TARIFF, DEFAULT_NIGHT_TARIFF, DEFAULT_DAY_ADJUSTMENT, DEFAULT_NIGHT_ADJUSTMENT

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tariffs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        day_tariff FLOAT,
        night_tariff FLOAT,
        day_adjustment INT,
        night_adjustment INT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meters_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        meter_id VARCHAR(50),
        day_reading INT,
        night_reading INT,
        bill FLOAT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        tariff_id INT,
        FOREIGN KEY (tariff_id) REFERENCES tariffs(id)
    )
    ''')

    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS insert_tariff_to_meters_history
        BEFORE INSERT ON meters_history
        FOR EACH ROW
        BEGIN
            SET NEW.tariff_id = (SELECT id FROM tariffs ORDER BY id DESC LIMIT 1);
        END;         
    ''')

    # Перевіряємо чи пуста таблиця, щоб задати базовк значення тарифів
    cursor.execute('SELECT COUNT(*) FROM tariffs')
    count = cursor.fetchone()[0]  # Кортеж (1,)

    if count == 0:
        cursor.execute('INSERT INTO tariffs (day_tariff, night_tariff, day_adjustment, night_adjustment) VALUES (%s, %s, %s, %s)', 
                       (DEFAULT_DAY_TARIFF, DEFAULT_NIGHT_TARIFF, DEFAULT_DAY_ADJUSTMENT, DEFAULT_NIGHT_ADJUSTMENT))

    conn.commit()
    conn.close()

def get_db_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM tariffs ORDER BY id DESC')
    tariffs = cursor.fetchall()

    cursor.execute('SELECT * FROM meters_history ORDER BY id DESC')
    meters_history = cursor.fetchall()

    cursor.close()
    conn.close()

    return {'tariffs': tariffs, 'meters_history': meters_history}

def get_db_last_meter_history_by_id(data):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM meters_history WHERE meter_id = %s ORDER BY id DESC', (data['meter_id'],))
    last_meter_history_by_id = cursor.fetchone()

    cursor.close()
    conn.close()

    return last_meter_history_by_id


# def update_db_meter_data(data):
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute('UPDATE meters_history SET day_reading = %s, night_reading = %s, bill = %s WHERE id = %s', (data['day_reading_update'], data['night_reading_update'],data['bill_update'], data['id_update']))

#     conn.commit()
#     conn.close()

# def delete_db_meter_data(data):
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute('DELETE FROM meters_history WHERE id = %s', (data['id_delete'],))

#     conn.commit()
#     conn.close()