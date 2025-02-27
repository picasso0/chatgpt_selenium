from rabbit.rabbit_class import RabbitMQ
import time
import os
from datetime import datetime
from time import sleep
import json
from utils.db import get_db
from chatgpt.chatgpt_automatic import ChatGPTAutomator
from health_check_api import update_last_consumption_time
import requests

def message_callback(data):
    print("recieve data")
    update_last_consumption_time()
    db = get_db()
    now_datetime=datetime.now()
    for request in data['body']:
        chat_db_record_id = None
        promt = json.dumps(request['messages'])
        find = db.rabbit_chats.find_one({"promt":promt})
    
        if find :
            chat_db_record_id = find['_id']
        else:
            chat_db_record = db.rabbit_chats.insert_one({"promt":promt, "create_at": now_datetime, "status":"in_progress"})
            chat_db_record_id = chat_db_record.inserted_id
        attempts = 1
        while(attempts < 4):
            try:
                chatgpt = ChatGPTAutomator()
                chatgpt.initialize(0)
                if chatgpt:
                    now_datetime=datetime.now()
                    if not chatgpt.send_prompt_to_chatgpt(promt):
                        chatgpt.quit()
                        db.rabbit_chats.update_one({"_id":chat_db_record_id},{"$set":{"status":"failed","message":"send promt error (login page)"}})
                        raise Exception("error in send prompt ( maybe login page )")
                    answer = chatgpt.return_last_response()
                    try:
                        answer=answer.split('json\nCopy\nEdit\n')[1]
                    except:
                        try:
                            answer=answer.split('json\nCopy\n')[1]
                        except:
                            try:
                                answer=answer.split('json\nCopy code\n')[1]
                            except:
                                pass
                        
                    # print(answer)   
                    try:
                        json.loads(answer)
                        print("data is json")
                    except:
                        print("data is not json")
                        print(answer)
                        raise Exception("answer data is not json")
                    prompt_token = chatgpt.estimate_token_usage(promt)
                    answer_token = chatgpt.estimate_token_usage(answer)
                    send_data_dict = {"status":"complete", "response":answer, 'completion_tokens':answer_token+prompt_token,'prompt_tokens':prompt_token }
                    chatgpt.driver.quit()
                    db.rabbit_chats.update_one({"_id":chat_db_record_id},{"$set":send_data_dict})
                    
                    rabbit_connection = RabbitMQ()
                    rabbit_connection.connect()
                    rabbit_connection.send_data(send_data_dict,"answer")
                    chatgpt.quit()
                    return 1
                else:
                    print("failed")
                    chatgpt.quit()
                db.rabbit_chats.update_one({"_id":chat_db_record_id},{"$set":{"status":"failed","message":"error in create chatgpt session"}})
                raise Exception("failed")
            except Exception as e:
                print(f"get attemt {attempts} with error {str(e)}")
                try:
                    chatgpt.quit()
                except:
                    pass
                attempts+=1
                

            
        
        
        

if __name__ == "__main__":
    try:
        server_init_url = str(os.getenv("SERTVER_INIT_URL"))
        requests.get(server_init_url)
    except:
        print("server init not is up")
    while(True):
        print("start subscriber")
        rabbit_connection = RabbitMQ()
        try:
            # Start consuming messages
            rabbit_connection.consume(message_callback)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        sleep(60)