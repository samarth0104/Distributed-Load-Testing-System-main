from confluent_kafka import Producer
import time

def send_heartbeat(producer, topic):
    while True:
        producer.produce(topic, key='driver', value='heartbeat')
        producer.flush()
        time.sleep(5)  # adjust as needed

def main():
    # Configure Kafka producer
    producer_config = {'bootstrap.servers': 'localhost:9092'}

    # Create an instance of the Producer
    producer = Producer(producer_config)

    # Define the topic for heartbeat
    heartbeat_topic = 'heartbeat_topic'

    # Start sending heartbeats
    send_heartbeat(producer, heartbeat_topic)

if __name__ == "__main__":
    main()

