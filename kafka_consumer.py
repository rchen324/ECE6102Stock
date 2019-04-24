TOPICS = "test"
from kafka import KafkaConsumer
import queue
import portfolio
from io import StringIO


if __name__ == "__main__":
    
    consumer = KafkaConsumer(TOPICS, bootstrap_servers='localhost:9092')
    q = queue.Queue()
    for msg in consumer:
        q.put(str(msg.value))
        if q.qsize() >= 30:
            q.get()
        if q.qsize() >= 20:
            head = 'date,GOOGL,FB,MSFT\n'
            for elem in list(q):
                elem[1:-1]
                head += elem
                head += '\n'
            print(head)
        
