import pika
from flask import Flask, request
from waitress import serve
import json
# Connection parameters
host = 'rmq'
credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(host=host, port=5672, credentials=credentials)
# Establish a connection to RabbitMQ
queue_name = 'rpalogs'

app = Flask(__name__)


@app.route('/', methods=['GET'])
def sendmsg():
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()
    # Declare a queue
    channel.queue_declare(queue=queue_name)
    # Message to send
    args = request.args
    payload = {}
    payload['message'] = args.get('msg') or ""
    payload['cat'] = args.get('cat') or "info"
    payload['type'] = args.get('type') or "dev"
    payload['process'] = args.get('process') or "default"

    payload['server'] = args.get('server') or request.remote_addr
    payload_json = json.dumps(payload)
    # Send the message to the queue
    channel.basic_publish(exchange='', routing_key=queue_name, body=payload_json)
    connection.close()
    return json.dumps({'success' : True}), 200, {'ContentType' : 'application/json'}


# Consume messages from the queue

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8081)




# Close the connection

