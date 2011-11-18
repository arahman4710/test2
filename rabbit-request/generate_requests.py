import pika 
import json

def info_response(ch, method, properties, body) :
    print "info_response"
    print properties
    print body 
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
def main(): 
   connection = pika.BlockingConnection(pika.ConnectionParameters(
      host='localhost'))
   channel = connection.channel()

   channel.queue_declare(queue='info_request',  durable=True)
   channel.queue_declare(queue='info_response', durable=True)

   print 'Rabbit waiting for messages. To exit press CTRL+C'

   channel.basic_qos(prefetch_count=1)

   channel.basic_consume(info_response,
                         queue='info_response')

   rd = {}
   
   rd['location'] = "Seattle, WA"
   rd['startdate'] = "07/20/2011" 
   rd['enddate'] = "07/21/2011"
   rd['adults'] = 1

   for i in range(10) :
       rd['message_id'] = i
       js = json.dumps(rd)
       print "json request:"
       print js 
       channel.basic_publish(exchange='',
                             routing_key='info_request',
                             body = js,  
                             properties=pika.BasicProperties(
                                 delivery_mode = 2, # make message persistent
                                 ))

   channel.start_consuming()



main() 
