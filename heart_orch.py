from confluent_kafka import Consumer, KafkaException

def consume_heartbeats(consumer, topics):
    consumer.subscribe(topics)

    try:
        while True:
            msg = consumer.poll(1.0)  # adjust timeout as needed
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            # Process heartbeat message
            print(f"Heartbeat received: {msg.value().decode('utf-8')}")

    finally:
        consumer.close()

def main():
    # Configure Kafka consumer
    consumer_config = {'bootstrap.servers': 'localhost:9092', 'group.id': 'orchestrator-group'}
    consumer = Consumer(consumer_config)

    # Define the topic for heartbeat
    heartbeat_topic = 'heartbeat_topic'

    # Start listening for heartbeats
    consume_heartbeats(consumer, [heartbeat_topic])

if __name__ == "__main__":
    main()

