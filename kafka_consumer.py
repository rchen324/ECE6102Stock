TOPICS = "test"
from kafka import KafkaConsumer
consumer = KafkaConsumer(TOPICS, bootstrap_servers='localhost:9092')

for msg in consumer:
    print(msg)