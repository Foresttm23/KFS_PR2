from database import create_tables, get_db_data, get_db_last_meter_history_by_id
from rabbitmq_consumer import start_consumer
from rabbitmq_producer import generate_random_readings, send_reading
import threading
import time

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
task_thread = None
task_running = False # toggle_data_generator()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send_reading_py', methods=['POST'])
def send_reading_py():
    data = request.json
    send_reading(data)
    return jsonify({"message": "Відправлено"})

@app.route('/get_meter_preview_py', methods=['POST'])
def get_meter_preview_py():
    data = request.json
    result = get_db_last_meter_history_by_id(data)
    return jsonify(result)

@app.route('/toggle_data_generator', methods=['POST'])
def toggle_data_generator():
    global task_thread, task_running

    if task_running:
        task_running = False  # Зупиняємо процес
        return jsonify({"status": "stopped"})
    else:
        task_running = True  # Запускаємо новий потікц
        task_thread = threading.Thread(target=data_generator, daemon=True)
        task_thread.start()
        return jsonify({"status": "Запущено"})

def data_generator():
    global task_running
    while task_running:
        print("Фоновий процес працює...")
        reading = generate_random_readings()
        send_reading(reading)
        time.sleep(1)

@app.route('/get_tables_data', methods=['GET'])
def get_tables_data():
    return get_db_data()


if __name__ == '__main__':
    create_tables()

    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.start()

    app.run(debug=True)