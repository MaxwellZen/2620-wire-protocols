import socket 
import sys

# grabs host and port from command-line arguments
if len(sys.argv) < 3 or not sys.argv[2].isdigit():
    print("Please provide a host and port for the socket connection")
    print("Example: python3 client_gui.py 127.0.0.1 54400")
    sys.exit(0)

host = sys.argv[1]
port = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    while True:
        message = input("Enter a message to send to the server: ")
        if message == "exit":
            break 
        print(f"c2s (pre-encode): {len(message)}")
        message = message.encode("utf-8")
        print(f"c2s (post-encode): {len(message)}")
        s.sendall(message)
        data = s.recv(1024)

        print(f"s2c (pre-decode): {len(data)}")
        data = data.decode("utf-8")
        print(f"s2c (post-decode): {len(data)}")
        print(f"Received: {data}")