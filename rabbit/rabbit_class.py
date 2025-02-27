
import pika
from os import getenv
import json
from threading import Thread
from time import sleep

class RabbitMQ:
    def __init__(self):
        self.host = str(getenv("RABBITMQ_URL"))
        self.port = int(getenv("RABBITMQ_PORT"))
        self.username = str(getenv("RABBITMQ_USERNAME"))
        self.vhost = str(getenv("RABBITMQ_VHOST"))
        self.password = str(getenv("RABBITMQ_PASSWORD"))
        self.queue = str(getenv("RABBITMQ_QUEUE"))
        self.promt_routing_key = str(getenv("RABBITMQ_PROMT_ROUTING_KEY"))
        self.answer_routing_key = str(getenv("RABBITMQ_ANSWER_ROUTING_KEY"))
        self.connection = None
        self.channel = None
        
    def is_connected(self):
        return (
            self.connection is not None and 
            self.connection.is_open and 
            self.channel is not None and 
            self.channel.is_open
        )

    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(host=self.host,port=self.port, virtual_host=self.vhost, credentials=credentials)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue, auto_delete=False, durable=True)
            print(f"Connected to RabbitMQ on {self.host}, queue: {self.queue}")
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
    
    def check_connection(self):
        if not self.is_connected():
            print("Connection is not established or has been closed. Attempting to reconnect...")
            self.connect()
        
        if self.is_connected():
            print("Connection is established and channel is open.")
        else:
            print("Failed to establish connection.")

    def send_data(self, message, queue):
        data=json.dumps(message,ensure_ascii=False).encode('utf8')
        if not self.channel:
            print("Channel not initialized. Call connect() first.")
            return
        
        try:
            self.channel.basic_publish(exchange='', routing_key=queue, body=data)
            print(f"Sent: data with routing key: {queue}")
        except Exception as e:
            print(f"Failed to send message: {e}")
        
    def consume(self, callback):
        self.connect()

        # Declare the queue again to ensure it exists with proper settings
        self.channel.queue_declare(queue=self.queue, auto_delete=False, durable=True)

        def on_message(ch, method, properties, body):
            try:
                body = body.decode('utf-8')
            except Exception as e:
                print(f"Error decoding message: {str(e)}")
                self.channel.basic_nack(delivery_tag=method.delivery_tag)
                return

            try:
                body = json.loads(body)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                self.channel.basic_nack(delivery_tag=method.delivery_tag)
                return
            
            
            try:
                callback(body)  # Call the provided callback function
                self.channel.basic_ack(delivery_tag=method.delivery_tag)
            except: 
                self.channel.basic_nack(delivery_tag=method.delivery_tag)
                raise Exception("a")
                
            
            # Create a thread for processing the message
            # thread = Thread(target=self.process_message, args=(callback, body, method.delivery_tag))
            # thread.start()

        try:
            self.channel.basic_qos(prefetch_count=1)  # Limit unacknowledged messages
            self.channel.basic_consume(queue=self.queue, on_message_callback=on_message, auto_ack=False)
            self.channel.start_consuming()
        except Exception as e:
            sleep(300)
            print(f"consume error: {str(e)}")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Stopping consumption...")
            self.close()

    def process_message(self, callback, body, delivery_tag):
        try:
            callback(body)  # Call the provided callback function
            self.channel.basic_ack(delivery_tag=delivery_tag)
        except: 
            self.channel.basic_nack(delivery_tag=delivery_tag)
        def stop_consuming(self):
            """Stop consuming messages and close the connection."""
            if self.channel:
                self.channel.stop_consuming()
            if self.connection:
                self.connection.close()
                print("Connection closed.")
                
        