from langchain_community.llms import Ollama
import ollama
import requests
import json
import base64

def myllm(user_input):
    llm = Ollama(model="phi")
    response = llm.invoke(user_input)
    return (response)

def myvisionmodel(user_input,file_path):
    # image path
    image_path = file_path

    # read image and encode in base 64
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llava",
        "prompt": user_input,
        "images": [image_base64],
        "stream": False
    }

    # send post
    response = requests.post(url, json=payload)  # use json parameter instead of data=json.dumps(payload)
    print (response)
    response_json = response.json()
    response_value = response_json.get("response", "")
    return(response_value)  # print the response content
