TOPICS = "test"
from kafka import KafkaConsumer
import queue


if __name__ == "__main__":
    
    consumer = KafkaConsumer(TOPICS, bootstrap_servers='localhost:9092')
    q = queue.Queue()
    for msg in consumer:
        q.put(str(msg.value))
        if q.qsize() >= 30:
            q.get()
        
