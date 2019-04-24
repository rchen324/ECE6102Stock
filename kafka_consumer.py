TOPICS = ""
from kafka import KafkaConsumer
consumer = KafkaConsumer('')

for msg in consumer:
    print(msg)