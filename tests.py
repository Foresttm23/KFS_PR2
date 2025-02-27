import unittest
import mysql.connector
from config import DB_CONFIG
import time
from rabbitmq_producer import send_reading
from database import create_tables
import threading
from rabbitmq_consumer import start_consumer



class TestElectricityBill(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Запускаємо окремо в своєму потоці
        cls.consumer_thread = threading.Thread(target=start_consumer)
        cls.consumer_thread.daemon = True
        cls.consumer_thread.start()
        time.sleep(2)
        
    def setUp(self):
        create_tables()

        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

        # Очищюємо таблиці перед кожним тестом
        self.clear_tables()

        self.cursor.execute('INSERT INTO tariffs (day_tariff, night_tariff, day_adjustment, night_adjustment) VALUES (%s, %s, %s, %s)', (2.0, 1.0, 20, 10))
        self.conn.commit()

    def tearDown(self):
        self.clear_tables()
        self.conn.close()


    def clear_tables(self):
        self.cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
        self.cursor.execute('TRUNCATE TABLE meters_history')
        self.cursor.execute('TRUNCATE TABLE tariffs')
        self.cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
        self.conn.commit()

    def test_new_meter(self):
        send_reading({'meter_id': 'meter_1', 'day_reading': 200, 'night_reading': 100, 'type': 'insert',})
        time.sleep(2)

        self.cursor.execute('UPDATE meters_history SET day_reading = %s, night_reading = %s WHERE meter_id = %s', (300, 200, 'meter_1')) # --
        self.conn.commit()

        self.cursor.execute('SELECT * FROM meters_history WHERE meter_id = %s', ('meter_1',))
        result = self.cursor.fetchone()
        self.assertEqual(result[2], 300)
        self.assertEqual(result[3], 200)
        self.assertIsNotNone(result[4], 0)  # Оскільки ми просто оновлюємо запис, розрахунок не відбувається

    def test_update_existing_meter(self):
        send_reading({'meter_id': 'meter_2', 'day_reading': 200, 'night_reading': 100, 'type': 'insert',})
        time.sleep(2)

        send_reading({'meter_id': 'meter_2', 'day_reading': 300, 'night_reading': 200, 'type': 'insert',})
        time.sleep(2)

        # Перевірка доданих даних
        self.cursor.execute('SELECT * FROM meters_history WHERE meter_id = %s ORDER BY id DESC LIMIT 1', ('meter_2',))
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[2], 300)
        self.assertEqual(result[3], 200)
        self.assertEqual(result[4], 300)  # 100 * 2 + 100 * 1 (тарифф)

    def test_low_night_reading(self):
        send_reading({'meter_id': 'meter_3', 'day_reading': 200, 'night_reading': 100, 'type': 'insert',})
        time.sleep(2)

        send_reading({'meter_id': 'meter_3', 'day_reading': 200, 'night_reading': 50, 'type': 'insert',})
        time.sleep(2)

        self.cursor.execute('SELECT * FROM meters_history WHERE meter_id = %s ORDER BY id DESC LIMIT 1', ('meter_3',))
        result = self.cursor.fetchone()
        self.assertEqual(result[2], 200)
        self.assertEqual(result[3], 110)  # 100 + 10 (накрутка)
        self.assertEqual(result[4], 10)   # 10 * 2 (тарифф)

    def test_low_day_reading(self):
        send_reading({'meter_id': 'meter_4', 'day_reading': 200, 'night_reading': 100, 'type': 'insert',})
        time.sleep(2)

        send_reading({'meter_id': 'meter_4', 'day_reading': 100, 'night_reading': 100, 'type': 'insert',})
        time.sleep(2)

        self.cursor.execute('SELECT * FROM meters_history WHERE meter_id = %s ORDER BY id DESC LIMIT 1', ('meter_4',))
        result = self.cursor.fetchone()
        self.assertEqual(result[2], 220)  # 200 + 20 (накрутка)
        self.assertEqual(result[3], 100)
        self.assertEqual(result[4], 40)   # 20 * 2 (тарифф)

    def test_low_day_night_reading(self):
        send_reading({'meter_id': 'meter_5', 'day_reading': 200, 'night_reading': 100, 'type': 'insert',})
        time.sleep(2)

        send_reading({'meter_id': 'meter_5', 'day_reading': 100, 'night_reading': 50, 'type': 'insert',})
        time.sleep(2)

        self.cursor.execute('SELECT * FROM meters_history WHERE meter_id = %s ORDER BY id DESC LIMIT 1', ('meter_5',))
        result = self.cursor.fetchone()
        self.assertEqual(result[2], 220)  # 200 + 20 (накрутка)
        self.assertEqual(result[3], 110)  # 100 + 10 (накрутка)
        self.assertEqual(result[4], 50)   # 20 * 2 + 10 * 1 (тарифф)

if __name__ == '__main__':
    unittest.main()
