import pika
import json
from config import RABBITMQ_CONFIG
from billing import process_reading

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_CONFIG['host']))
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_CONFIG['queue'])

    def callback(ch, method, properties, body):
        process_reading(json.loads(body))

    channel.basic_consume(queue=RABBITMQ_CONFIG['queue'], on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
