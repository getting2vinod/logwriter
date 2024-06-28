import os

import pika
from flask import Flask, request
from waitress import serve
import json
from threading import Thread
import requests
import time

# Connection parameters
# 'rmq'
host = 'rmq1'
credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(host=host, port=5672, credentials=credentials)
# parameters = pika.ConnectionParameters(host=host, port=80, credentials=credentials)
# Establish a connection to RabbitMQ
queue_name = 'rpalogs'

# Jenkins configuration. Used for triggering a build. Sharing a common web interface.
jenkins_url = "http://"
hip = ""

with open('hostip.txt', 'r') as jf:
    hip = jf.read()
    jenkins_url = jenkins_url+hip+":81"

jenkins_user = "build"
jenkins_pwd = "$cholastiC&$!@2023"
token = "thisIstheLongToken"


app = Flask(__name__)


def push_to_queue(args, remote_addr):
    try:
        msgtype = 'dev'
        if '10.80' in remote_addr or 'AWSRPA' in args.get('server') or 'AWSRPA' in args.get('msg'):
            msgtype = 'prod'
        if 'UAT' in args.get('process'):
            msgtype = 'qa'

        # ignoring dev messages
        if msgtype != 'dev':
            connection = pika.BlockingConnection(parameters=parameters)
            channel = connection.channel()
            # Declare a queue
            channel.queue_declare(queue=queue_name)
            # should have been msgsource todo.

            payload = {'message': args.get('msg')[:200] or "", 'cat': args.get('cat') or "info",
                       'type': args.get('type') or msgtype,
                       'process': args.get('process') or "default",
                       'procid': args.get('procid') or "000",
                       'server': args.get('server') or remote_addr}
            payload_json = json.dumps(payload)
            channel.basic_publish(exchange='', routing_key=queue_name, body=payload_json)
            connection.close()
    except Exception as inst:
        print("Exception: " + str(inst))


@app.route('/runjob', methods=['GET'])
def runjob():
    try:
        job_name_default = "Uipath Project Build and Deploy"
        job_name = request.args.get('jobname') or job_name_default
        jenkins_params = {'token': token}
        auth = (jenkins_user, jenkins_pwd)
        crumb_data = requests.get("{0}/crumbIssuer/api/json".format(jenkins_url), auth=auth,
                                  headers={'content-type': 'application/json'})
        if str(crumb_data.status_code) == "200":
            data = requests.get("{0}/job/{1}/build".format(jenkins_url, job_name),
                                auth=auth, params=jenkins_params,
                                headers={'content-type': 'application/json',
                                         'Jenkins-Crumb': crumb_data.json()['crumb']})
            return json.dumps({'output': "Job triggered "}), 200, {'ContentType': 'application/json'}
        else:
            return (json.dumps({'output': "Failed to trigger the Jenkins job"}), 200,
                    {'ContentType': 'application/json'})
    except Exception as e:
        return json.dumps({'output': str(e)}), 200, {'ContentType': 'application/json'}


@app.route('/output', methods=['GET'])
def output():
    try:
        job_name_default = "Uipath Project Build and Deploy"
        job_name = request.args.get('jobname') or job_name_default
        jenkins_params = {'token': token}
        auth = (jenkins_user, jenkins_pwd)
        crumb_data = requests.get("{0}/crumbIssuer/api/json".format(jenkins_url), auth=auth,
                                  headers={'content-type': 'application/json'})
        if str(crumb_data.status_code) == "200":
            resp = requests.get("{0}/job/{1}/lastBuild/consoleText".format(jenkins_url, job_name),
                                auth=auth, params=jenkins_params,
                                headers={'content-type': 'application/json',
                                         'Jenkins-Crumb': crumb_data.json()['crumb']})
            return json.dumps({'output': resp.text}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'output': "Could not fetch Crumb"}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        return json.dumps({'output': str(e)}), 200, {'ContentType': 'application/json'}


#[UTC 03/02/2024 05:42:00] [564] [rpabotrestock@AWSRPATEMP12] [UAT - Restock Order Processing - Prod] [qa] [Debug] - Found run counter. Reading..
@app.route('/', methods=['GET'])
def sendmsg():
    # Spawn thread to process the data
    args = request.args
    # t = Thread(target=push_to_queue, args=(args, request.remote_addr,))
    remoteip = request.headers.environ['HTTP_X_REAL_IP'] or request.remote_addr
    t = Thread(target=push_to_queue, args=(args, remoteip,))
    #'HTTP_X_REAL_IP'
    t.start()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/ping', methods=['GET'])
def sendpong():
    return json.dumps({'success': True, "ip": hip}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8081)

