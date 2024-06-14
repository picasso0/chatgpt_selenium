from chatgpt_automatic import ChatGPTAutomator
breakpoint()
chatgpt = ChatGPTAutomator()
question = "How ChatGPT Ignited the A.I. Competition Wave"

chatgpt.send_prompt_to_chatgpt(question)

# wait a moment ...

answer = chatgpt.return_last_response()

print(answer)