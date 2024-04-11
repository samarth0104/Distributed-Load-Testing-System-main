import json
import time
import requests
import statistics
import uuid, threading
import socket
from kafka import KafkaProducer
from confluent_kafka import Producer, Consumer, KafkaError
from flask import Flask, request, jsonify
from multiprocessing import Process, Manager

app = Flask(__name__)

metrics_topic = "metrics"
heartbeat_topic = 'heartbeat'
register_topic = 'register'
test_config_topic = 'test_config'
trigger_topic = 'trigger'
kafka_broker = 'localhost:9092'

# The number of concurrent driver instances to run
num_drivers = 1

# List to store driver_ids
driver_ids = []

port=8085

def send_heartbeat(producer,driver_id):
        while True:
            heartbeat_message = {
                "node_id": driver_id,
                "heartbeat": "YES",
                "timestamp": str(time.time())
            }
            print("sending heartbeat")
            producer.produce(heartbeat_topic, key=driver_id, value=json.dumps(heartbeat_message).encode('utf-8'))
            producer.flush()
            time.sleep(1)

def run_driver(port, shared_list):
    producer = Producer({'bootstrap.servers': kafka_broker})
    latency_list = shared_list  
    driver_id = str(uuid.uuid4())
    driver_ids.append(driver_id)
    '''def send_heartbeat():
        while True:
            #producer.produce(heartbeat_topic, key=driver_id, value='heartbeat')
            producer.flush()
            time.sleep(1)  # adjust as needed
            heartbeat_message = {
                "node_id": driver_id,
                "heartbeat": "YES",
                "timestamp": str(time.time())
            }
            producer.produce(heartbeat_topic, key=driver_id, value=json.dumps(heartbeat_message).encode('utf-8'))
            producer.flush()
            time.sleep(1)


    def send_heartbeat():
        while True:
            producer.produce(heartbeat_topic, key=driver_id, value='heartbeat')
            producer.flush()
            time.sleep(1)'''  

    @app.route('/start_test', methods=['POST'])
    def start_test():
        data = request.get_json()
        start_time = time.time()
        response = requests.get('http://localhost:8080')
        end_time = time.time()

        latency = end_time - start_time
        latency_list.append(latency)
        print(latency_list)
        return jsonify({"message": "Test started"})

    def get_metrics(latency_list, current_test_id, driver_id):
        if not latency_list:
            print("No latency data available.")
            return

        mean_latency = statistics.mean(latency_list)
        median_latency = statistics.median(latency_list)
        min_latency = min(latency_list)
        max_latency = max(latency_list)
        r_id = str(uuid.uuid4())
        metrics = {
            "mean_latency": mean_latency,
            "median_latency": median_latency,
            "min_latency": min_latency,
            "max_latency": max_latency
        }

        m_dict = {
            "node_id": driver_id,
            "test_id": current_test_id,
            "report_id": r_id,
            "metrics": metrics
        }
        producer.produce(metrics_topic, value=json.dumps(m_dict))
        producer.flush()

        print("Metrics produced for driver_id:", driver_id)

    def register_driver():
        node_ip = socket.gethostbyname(socket.gethostname())
        driver_ids.append(driver_id)
        register_message = {
            "node_id": driver_id,
            "node_ip": node_ip +'    ' + str(port),
            "message_type": "DRIVER_NODE_REGISTER"
        }

        producer.produce(register_topic, key=driver_id, value=json.dumps(register_message).encode('utf-8'))
        producer.flush()
        print("Registration completed for driver_id:", driver_id)

    def consume_test_config():
        consumer_conf = {
            'bootstrap.servers': kafka_broker,
            'group.id': 'test_config_id',
            'auto.offset.reset': 'earliest' 
        }
        consumer = Consumer(consumer_conf)
        consumer.subscribe([test_config_topic])
        partitions = consumer.assignment()
        for partition in partitions:
            partition.seek(0)
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
            test_config_message = json.loads(msg.value().decode('utf-8'))
            current_test_id = test_config_message.get('test_id')
            test_type = test_config_message.get('test_type')
            test_message_delay = test_config_message.get('test_message_delay', 0)
            message_count_per_driver = test_config_message.get('message_count_per_driver', 0)

            print("Waiting for trigger...")
            trigger_received = wait_for_trigger(current_test_id)
            
            if trigger_received:
            
                if test_type == 'AVALANCHE':
                    for _ in range(num_drivers):  
                        avalanche_test(current_test_id, message_count_per_driver)
                    
                elif test_type == 'TSUNAMI':
                    for _ in range(num_drivers):
                        tsunami_test(current_test_id, test_message_delay, message_count_per_driver)
            test_triggered = False
    def wait_for_trigger(current_test_id):
        trigger_received = False 
        consumer_conf = {
            'bootstrap.servers': kafka_broker,
            'group.id': 'my_consumer_group',
            'auto.offset.reset': 'earliest'  
        }

        consumer = Consumer(consumer_conf)
        consumer.subscribe([trigger_topic])
        partitions = consumer.assignment()
        for partition in partitions:
            partition.seek(0)

        while not trigger_received:
            msg = consumer.poll(1.0)  
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Error: {msg.error()}")
                    break

            trigger_message = json.loads(msg.value().decode('utf-8'))
            if trigger_message.get('test_id') == current_test_id and trigger_message.get('trigger') == 'YES':
                print("created heartbeat thread")
                heartbeat_thread = threading.Thread(target=send_heartbeat,args = (producer,driver_id))
                heartbeat_thread.daemon = True
                heartbeat_thread.start()
                print(f"Trigger received for test_id {current_test_id}")
                trigger_received = True

        return trigger_received

    def tsunami_test(current_test_id, test_message_delay, message_count_per_driver):
        print(f'Tsunami Test started for node ID: {driver_id} with test ID: {current_test_id}')
        for _ in range(message_count_per_driver):
            '''if _ == messagecount_per_drive - 1:
                start_time = time.time()
                response = requests.get('http://127.0.0.1:8080/ping')  
                print(f'Response: {_}')'''
            start_time = time.time()
            response = requests.get('http://127.0.0.1:8080/test')  
            print(f'Response: {_}')
            time.sleep(test_message_delay)
            end_time = time.time()
            latency = end_time - start_time
            latency_list.append(latency)
        print('Test completed')
        get_metrics(latency_list, current_test_id, driver_id)
    def avalanche_test(current_test_id, message_count_per_driver):
        for _ in range(message_count_per_driver):
            start_time = time.time()
            response = requests.get('http://localhost:8080/test')
            end_time = time.time()

            latency = end_time - start_time
            latency_list.append(latency)

        print('Test completed')
        get_metrics(latency_list, current_test_id, driver_id)

    if __name__ == '__main__':
        # Start a separate thread to register the driver
        register_driver()
        consume_test_config()
        # Start the Flask app
        #app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    with Manager() as manager:
        shared_list = manager.list() 
        processes = []
        for i in range(num_drivers):
            
            port = port + i
            process = Process(target=run_driver, args=(port, shared_list))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

    print("List of driver_ids:", driver_ids)
