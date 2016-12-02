# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import json
import pika
import os

app = Flask(__name__)
 
__author__ = 'Lukasz Zalewski / plus.pl'

RABBITMQ_HOST = str(os.environ['RABBITMQ_HOST'])
RABBITMQ_PORT = int(os.environ['RABBITMQ_PORT'])
VIRTUAL_HOST = os.environ['VIRTUAL_HOST']
USER = os.environ['USER']
PASSWD = os.environ['PASSWD']
QUEUE = os.environ['QUEUE']

@app.route('/hello')
def HelloODIS():
    return "Hello ODIS"

@app.route('/')
def main():
    return HelloODIS()

@app.route('/api/add_record', methods=['GET', 'POST'])
def add_msg():
    content = request.json
    if content is None:
    	return jsonify({"status":"ERROR"})
    else:
	#print content
        credentials = pika.PlainCredentials(USER, PASSWD)
        parameters = pika.ConnectionParameters(RABBITMQ_HOST,
                                               RABBITMQ_PORT,
                                               VIRTUAL_HOST,
                                               credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue=QUEUE, durable=True)

        message = content
        channel.basic_publish(exchange='',
                              routing_key=QUEUE,
                              #body="hello",
                              #body=str(content),
                              body=json.dumps(content),
                              properties=pika.BasicProperties(
                                  delivery_mode = 2, # make message persistent
                                ))
#        print(" [x] Sent %r" % message)
        connection.close()
	return jsonify({"status":"OK","next":87000})


if __name__ == '__main__':
    app.debug = True
    app.run()
