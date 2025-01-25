# Python script to simulate data generation and send to Kafka
import time
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:9092',
}

producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}')

topic = 'my_topic'

for i in range(10):
    data = f'Data point {i}'
    producer.produce(topic, key=str(i), value=data.encode('utf-8'), callback=delivery_report)
    producer.flush()
    time.sleep(1)

print('Data generation and sending to Kafka complete.')
