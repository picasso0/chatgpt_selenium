from rabbit_class import RabbitMQ
import os
from time import sleep
import json
from datetime import datetime
from database import get_db
    
def publish_data(data):   
    rabbit_connection = RabbitMQ()
    rabbit_connection.connect()
    rabbit_connection.send_data(data)
    
if __name__ == "__main__":
    print("start publisher")
    db = get_db()
    while(True):
        with open('batch_ids', 'r') as file:
            lines = file.readlines()
        with open('batch_ids', 'w') as f:
            for line in lines:
                line=line.strip()
                batch = get_batch_status(line)
                if batch and batch.status == "completed":
                    output_file_id = batch.output_file_id

                    # 3. Get the file content
                    results = get_file_content(output_file_id)
                    for result in results:
                        response_dict = convert_to_dict(result)
                        chat_data = {'batch_id': line,
                                        "custom_id": result['custom_id'],
                                    'response': result, 'create_at': datetime.now(),
                                    "status":batch.status}
                        db.chats.update_one({'custom_id':result['custom_id']},{"$set":chat_data})                            
                        result = {"custom_id": result['custom_id'], "response": result['response']['body']['choices'][0]['message']['content'],
                                    "prompt_tokens": result['response']['body']['usage']['prompt_tokens'],
                                    "completion_tokens": result['response']['body']['usage']['completion_tokens'],
                                    "total_tokens": result['response']['body']['usage']['total_tokens']}
                        publish_data(result)
            
                    print ({"status":batch.status, "message":"Batch job completed","results":results})
                else:
                    db.chats.update_many({"batch_id":batch.id},{"$set":{"status":batch.status}})
                    f.write(line+'\n')
                    print ({"status":batch.status, "message":"Batch job not completed"})
        sleep(60)
    

    