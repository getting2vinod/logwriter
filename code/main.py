import pika
from flask import Flask, request
from waitress import serve
import json
from threading import Thread

# Connection parameters
host = 'rmq'
credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(host=host, port=5672, credentials=credentials)
# Establish a connection to RabbitMQ
queue_name = 'rpalogs'

app = Flask(__name__)


def push_to_queue(args, remote_addr):
    try:
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()
        # Declare a queue
        channel.queue_declare(queue=queue_name)
        # should have been msgsource todo.
        msgtype = 'dev'
        if '10.80' in remote_addr:
            msgtype = 'prod'
        if 'UAT' in args.get('process'):
            msgtype = 'qa'
        payload = {'message': args.get('msg') or "", 'cat': args.get('cat') or "info",
                   'type': args.get('type') or msgtype,
                   'process': args.get('process') or "default",
                   'procid': args.get('procid') or "000",
                   'server': args.get('server') or remote_addr}
        payload_json = json.dumps(payload)
        channel.basic_publish(exchange='', routing_key=queue_name, body=payload_json)
        connection.close()
    except Exception as inst:
        print("Exception: " + str(inst))


@app.route('/', methods=['GET'])
def sendmsg():
    # Spawn thread to process the data
    args = request.args
    t = Thread(target=push_to_queue, args=(args, request.remote_addr,))
    t.start()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/ping', methods=['GET'])
def sendpong():
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8081)
