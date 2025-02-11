import socket
import selectors 
import types 
from utils import decode_request, encode_request

sel = selectors.DefaultSelector()

# do not actually do this
HOST = "127.0.0.1"
PORT = 54400

users = {}

def create_account(username, data):
    if username in users:
        return "Username taken. Please login with your password"
    else:
        data.username = username
        data.supplying_pass = True
        return "Enter password to create new account"

def supply_pass(password, data):
    if data.supplying_pass:
        users.update({data.username: (password, [])})
        data.supplying_pass = False
        return "Account created. Please login with your new account"
    return "ERROR: should not be supplying password"
        
def login(username, password, data):
    if username in users:
        if (password == users[username][1]):
            data.username = username
            data.loggedin = True
            return "SUCCESS"
    return "ERROR: username does not exist. Please create a new account"

def list_accounts(data):
    return

def send(username, message, data):
    return

def read(count, data):
    return

def delete_msg(IDs, data):
    return

def delete_account(data):
    if data.loggedin:
        # need to delete all msgs
        users.pop(data.username)
        data.username = None
        data.loggedout = False
        return "SUCCESS"
    return "ERROR: not logged in"

def logout(data):
    if data.loggedin:
        data.username = None
        data.loggedout = False
        return "SUCCESS"
    return "ERROR: not logged in"

def handle_command(request, data):
    request = decode_request(request)
    command = request[0]
    match command:
        case "create_account":
            return create_account(request[1], data)
        case "supply_pass":
            return supply_pass(request[1], data)
        case "login":
            return login(request[1], request[2], data)
        case "list_accounts":
            return list_accounts(data)
        case "send":
            return send(request[1], request[2], data)
        case "read":
            return read(request[1], data)
        case "delete_msg":
            return delete_msg(request[1], data)
        case "delete_account":
            return delete_account(data)
        case "logout":
            return logout(data)
        case _:
            return "ERROR: Invalid command"

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"", username=None, logged_in=False, supplying_pass=False)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE 
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data 
    return_data = ""
    
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            return_data = handle_command(data.outb.decode("utf-8"), data)
            return_data = return_data.encode("utf-8")
            sent = sock.send(return_data)
            data.outb = data.outb[sent:]

if __name__ == "__main__":
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print("Listening on", (HOST, PORT))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data = None)
    try:
        while True:
            events = sel.select(timeout = None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()
