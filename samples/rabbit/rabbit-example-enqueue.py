#!/usr/bin/env python
import pika
import sys
import random
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(
       host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

for i in range(1000) : 
    message = "message %d" % i 
    channel.basic_publish(exchange='',
                          routing_key='task_queue',
                          body=message,
                          properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                              ))
    print " [x] Sent %r" % (message,)
    time.sleep(random.uniform(0, 1.0)) 

connection.close()

