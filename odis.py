# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import json
import pika
import os

app = Flask(__name__)
 
__author__ = 'Lukasz Zalewski / plus.pl'

RABBITMQ_MAIN_HOST = str(os.environ['RABBITMQ_MAIN_HOST'])
RABBITMQ_MAIN_PORT = int(os.environ['RABBITMQ_MAIN_PORT'])
RABBITMQ_BCK_HOST = str(os.environ['RABBITMQ_BCK_HOST'])
RABBITMQ_BCK_PORT = int(os.environ['RABBITMQ_BCK_PORT'])
VIRTUAL_HOST = os.environ['VIRTUAL_HOST']
USER = os.environ['USER']
PASSWD = os.environ['PASSWD']
QUEUE = os.environ['QUEUE']

def connect_to_rabbit_node(connectionParams):
    # polacz sie z pierwszym dostepnym nodem rabbitowym z listy
    i=-1 
    while True:
        try:     
            # wpadnie w nieskonczona petle jezeli poleca wszystkie brokery.
            # Dlatego tym bardziej wazne zeby w produkcyjnym rozwiazaniu usunac printy.
            # raise ValueError('A very specific bad thing happened', 'foo', 'bar', 'baz')             
            #if(i==-1):
            #    print 'Try to connect to RabbitMQ. Message broker nr: 1'
            #else:
            #    print 'Connection with node C1H%d failed... connecting to node C1H%d.'%(i+1, (i+1)%len(connectionParams)+1)

            # id of rabbit node on the list
            i=(i+1)%len(connectionParams)

            # Step #1: Connect to RabbitMQ using the default parameters
            connection = pika.BlockingConnection(connectionParams[i])
            return connection
        
        except exceptions.AMQPConnectionError as e:
            # print "Rabbitmq Connection error " + e.message        
            pass
        except:
            print "Unexpected error:"
            raise

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
	connectionParams = []
        credentials = pika.PlainCredentials(USER, PASSWD)
        main_parameters = pika.ConnectionParameters(RABBITMQ_MAIN_HOST,
                                               RABBITMQ_MAIN_PORT,
                                               VIRTUAL_HOST,
                                               credentials)
	#backup connection parameters
        bck_parameters = pika.ConnectionParameters(RABBITMQ_BCK_HOST,
                                               RABBITMQ_BCK_PORT,
                                               VIRTUAL_HOST,
                                               credentials)
	connectionParams.append(main_parameters)
	connectionParams.append(bck_parameters)

        #connection = pika.BlockingConnection(main_parameters)
        connection = connect_to_rabbit_node(connectionParams)

        channel = connection.channel()
        channel.queue_declare(queue=QUEUE, durable=True)

        message = content
        channel.basic_publish(exchange='',
                              routing_key=QUEUE,
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
