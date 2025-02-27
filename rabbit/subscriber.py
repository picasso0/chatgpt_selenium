from rabbit_class import RabbitMQ
import time
import os
from time import sleep
import json
from database import get_db



def message_callback(data):
    if 'isBatch' in data and data['isBatch']==1:
        # 1. Create the JSONL file
        jsonl_file_path,chat_ids = create_jsonl_file(data['body'])

        # 2. Upload the JSONL file
        file_id = upload_file(jsonl_file_path)

        # 3. Create the batch job
        batch_id = create_batch_job(file_id)
        
        db=get_db()
        for chat_id in chat_ids :
            db.chats.update_one({"_id": chat_id},{"$set":{"batch_id": batch_id.id}})
        with open('batch_ids', 'a') as file:
            file.write(batch_id.id+'\n')
        
        

if __name__ == "__main__":
    while(True):
        print("start subscriber")
        rabbit_connection = RabbitMQ()

        try:
            # Start consuming messages
            rabbit_connection.consume(message_callback)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        sleep(60)