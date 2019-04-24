TOPICS = "test"
from kafka import KafkaConsumer
import queue
from portfolio import *
from io import StringIO
from google.cloud import datastore



if __name__ == "__main__":
    datastore_client = datastore.Client()
    consumer = KafkaConsumer(TOPICS, bootstrap_servers='localhost:9092')
    q = queue.Queue()
    for msg in consumer:
        q.put(str(msg.value))
        if q.qsize() >= 30:
            q.get()
        if q.qsize() >= 21:
            head = 'date,GOOGL,FB,MSFT\n'
            for elem in list(q.queue):
                s = str(elem)[3:-2]
                head += s
                head += '\n'
            mu, S = calcMuCov2(StringIO(head))
            cleaned_weights, perf = maxSharpeRatio(mu, S)
            result = combineWeigPerf(cleaned_weights, perf)
    
            kind = 'Results'
            name = 'result_'+today_str
            task_key = datastore_client.key(kind, name)
            task = datastore.Entity(key=task_key)
            task['date'] = today_str
            task['rec'] = str(result)
            datastore_client.put(task)
            # print (result)

                
            # print(head)
        
