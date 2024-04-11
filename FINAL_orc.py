from flask import Flask, jsonify
from flask import render_template
from confluent_kafka import Producer, Consumer, KafkaError
import json
import uuid
import ipaddress
import threading
import time
import requests

app = Flask(__name__)
metrics_lock = threading.Lock()
# Kafka broker address
bootstrap_servers = 'localhost:9092'

# Kafka topics
register_topic = 'register'
test_config_topic = 'test_config'
trigger_topic = 'trigger'
metrics_topic = 'metrics'
heartbeat_topic = 'heartbeat'
workload_topic = 'workload'

registered = False

# Global count variable
count = 0



request_counter = {
    '/register': 0,
    '/test-config': 0,
    '/trigger-test': 0
}

# Kafka producer configuration
producer_conf = {
    'bootstrap.servers': bootstrap_servers
}

# Kafka producer for sending messages
producer = Producer(producer_conf)


metrics_data = []  # Store metrics data

def add_metrics_data(node_id, metrics):
    metrics_data.append({"node_id": node_id, "metrics": metrics})

@app.route('/metrics')
def display_metrics():
    global metrics_data
    with metrics_lock:
        metrics_copy = metrics_data.copy()  # Copy metrics_data to avoid modifying it while rendering
    return render_template('metrics.html', metrics_data=metrics_copy)




def consume_metrics_messages():
    consumer_conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'metrics_consumer_group',
        'auto.offset.reset': 'earliest' 
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe([metrics_topic])

    while True:
        msg = consumer.poll(1.0)  
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error: {msg.error()}")
                break

        metrics_message = json.loads(msg.value().decode('utf-8'))
        process_metrics_message(metrics_message)
        

def process_metrics_message(metrics_message):
    node_id = metrics_message.get("node_id")
    metrics_data = metrics_message.get("metrics")

    print(f"Received metrics for node ID: {node_id}")
    print("Metrics:")
    print(json.dumps(metrics_data, indent=2))
    print("=" * 50)
    add_metrics_data(node_id, metrics_data)
node_list = []

def consume_register_messages():
    global count 
    consumer_conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'my_consumer_group',
        'auto.offset.reset': 'earliest' 
    }

    consumer = Consumer(consumer_conf)
    consumer.subscribe([register_topic])
    while True:
        msg = consumer.poll(1.0)  
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error: {msg.error()}")
                break

        register_message = json.loads(msg.value().decode('utf-8'))
        process_register_message(register_message)


def process_register_message(register_message):
    global count 
    node_id = register_message.get("node_id")
    node_ip = register_message.get("node_ip")
    message_type = register_message.get("message_type")

    if message_type == "DRIVER_NODE_REGISTER":
        print(f"Received registration message from node ID: {node_id}, IP: {node_ip}")

        node_list.append({
            "node_id": node_id,
            "node_ip": node_ip,
            "message_type": message_type
        })
        count = count + 1


def start_consumer_thread(t):
    consumer_thread = threading.Thread(target=t)
    consumer_thread.daemon = True
    consumer_thread.start()


current_node_id = str(uuid.uuid4())


def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def send_trigger_message(current_test_id):
    trigger_message = {
        "test_id": current_test_id,
        "trigger": "YES"
    }
    producer.produce(trigger_topic, key=current_node_id,value=json.dumps(trigger_message).encode('utf-8'), callback=delivery_report)
    producer.flush()
    print(f'Trigger message sent for test ID: {current_test_id}')

def send_test_config(current_test_id, test_type, delay, message_count_per_driver):
    test_config_message = {
        "test_id": current_test_id,
        "test_type": test_type,
        "test_message_delay": delay,
        "message_count_per_driver": message_count_per_driver
    }
    producer.produce(test_config_topic, key=current_test_id,
                     value=json.dumps(test_config_message), callback=delivery_report)
    producer.flush()
    request_counter['/test-config'] += 1

last_heartbeat_timestamps={}
def process_heartbeat_message(heartbeat_message):
    node_id = heartbeat_message.get("node_id")
    timestamp = heartbeat_message.get("timestamp")

    # Update the last heartbeat timestamp for the corresponding driver
    last_heartbeat_timestamps[node_id] = timestamp
    print(f"Received heartbeat from node ID: {node_id}, timestamp: {timestamp}")


def consume_heartbeat_messages():
    consumer_conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'heartbeat_consumer_group',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(consumer_conf)
    consumer.subscribe([heartbeat_topic])
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error: {msg.error()}")
                break

        heartbeat_message = json.loads(msg.value().decode('utf-8'))
        process_heartbeat_message(heartbeat_message)

current_test_id = str(uuid.uuid4())
test_type=input("Enter the test type: ")
test_delay = 0
if test_type == "TSUNAMI":
    test_delay = int(input("Enter test delay: "))
mcpd = int(input("Enter the message_count_per_driver: "))
send_test_config(current_test_id, test_type, test_delay, mcpd)
input("Press Enter to trigger the test...")
send_trigger_message(current_test_id)

if __name__ == '__main__':
    start_consumer_thread(consume_register_messages)
    start_consumer_thread(consume_metrics_messages)
    start_consumer_thread(consume_heartbeat_messages)
    while count < 8:
        time.sleep(1)  
    app.run(debug=True, use_reloader=False)
