# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import json
import pika
from pika import exceptions
import toml

app = Flask(__name__)
 
__author__ = 'Lukasz Zalewski / plus.pl'

CONF_FILE = '/conf/conf.toml'

def read_conf(CONF_FILE):
    with open(CONF_FILE) as conffile:
        conf = toml.loads(conffile.read())
    return conf


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
    global CONF
    if 'CONF' not in globals():
	CONF = read_conf(CONF_FILE)

    content = request.json
    if content is None:
    	return jsonify({"status":"ERROR"})
    else:
	#print content
        sslOptions = CONF['output']['rabbitmq']['ssl_options']

	connectionParams = []
	rmqaccess = CONF['output']['rabbitmq']
        credentials = pika.PlainCredentials(rmqaccess['username'], rmqaccess['password'])

	for host in CONF['output']['rabbitmq']['host']:
		connection_x = pika.ConnectionParameters(host['url']
						 ,host['port']
						 ,rmqaccess['vhost']
						 ,credentials
						 ,ssl = rmqaccess['ssl']
						 ,ssl_options = sslOptions)
		connectionParams.append(connection_x)

        #connection = pika.BlockingConnection(main_parameters)
        connection = connect_to_rabbit_node(connectionParams)

        channel = connection.channel()
        channel.queue_declare(queue=rmqaccess['queue_name'], durable=True)

        message = content
        channel.basic_publish(exchange='',
                              routing_key=rmqaccess['queue_name'],
                              body=json.dumps(content),
                              properties=pika.BasicProperties(
                                  delivery_mode = 2, # make message persistent
                                ))
#        print(" [x] Sent %r" % message)
        connection.close()
	return jsonify({"status":"OK","next":87000})

if __name__ == '__main__':
    global CONF
    CONF = read_conf(CONF_FILE)
    uwsgiParam = CONF['uwsgi']
    app.debug = uwsgiParam['debug']
    app.run()
