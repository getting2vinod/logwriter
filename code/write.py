import os

import pika
import json
import datetime
from time import sleep

# Connection parameters
host = 'rmq'
credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(host=host, port=5672, credentials=credentials)
# Establish a connection to RabbitMQ
queue_name = 'rpalogs'


# Define a callback function to process incoming messages
def callback(ch, method, properties, body):
    # print(f"Received: {body}") #do not use print, since it blocks reception on consume
    jo = json.loads(body)
    log_date = datetime.datetime.utcnow()
    with open('/code/logs/debug' + str(log_date.weekday()) + '.log', 'a+') as f:
        f.write("[" + log_date.strftime("UTC %m/%d/%Y %H:%M:%S") + "]"
                + " [" + jo["procid"] + "]"
                + " [" + jo["server"] + "]" + " [" + jo["process"] + "]" + " [" + jo["type"] + "]"
                + " [" + jo["cat"] + "]" + " - " + jo["message"] + '\n')


sleep(30) #wait for rmq to be up
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()
# Declare a queue
try:
    #print(os.getcwd())
    channel.queue_declare(queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    # Start consuming messages
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
    print("Closing connection")
    connection.close()
# Close the connection:Q
