import socket 
import json
from utils import encode_json

# don't actually do this 
HOST = "127.0.0.1"
PORT = 54400

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        message = input("Enter a message to send to the server: ")
        if message == "exit":
            break 
        json_request = encode_json(message)
        json_str = json.dumps(json_request)
        s.sendall(json_str.encode("utf-8"))
        
        data = s.recv(1024)
        data = data.decode("utf-8")
        print(f"Received: {data}")