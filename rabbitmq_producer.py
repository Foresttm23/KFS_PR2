import pika
import json
import random
from config import RABBITMQ_CONFIG

def generate_random_readings():
    meter_id = f'meter_{random.randint(1, 10)}'
    day_reading = random.randint(100, 1000)
    night_reading = random.randint(100, 1000)

    data = {
        'meter_id': meter_id,
        'day_reading': day_reading,
        'night_reading': night_reading,
        'type': 'insert'
    }

    return data

def send_reading(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_CONFIG['host']))
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_CONFIG['queue'])
    channel.basic_publish(exchange='', routing_key=RABBITMQ_CONFIG['queue'], body=json.dumps(data))
    connection.close()
