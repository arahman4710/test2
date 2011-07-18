import boto 

# this takes amazon id and secret keys, but will read them from the environment
# if necessary - look in ~jeff/.bashrc for them - they start with AWS_

conn = boto.connect_sqs()

q = conn.create_queue('jeffsqueue')
# or 
# q = conn.get_queue('jeffsqueue') 

# send a message to ourselves 
mess = boto.sqs.message.Message( )
mess.set_body("message 1") 
q.write(mess) 

# now get all the messages in the queue (currently only one) 

# rs = q.get_messages()
# or specify how many messages to _try_ to get 
rs  = q.get_messages(num_messages=7)  
print len(rs)
print rs[0].get_body()
q.delete_message(rs[0]) 

conn.delete_queue(q) 
