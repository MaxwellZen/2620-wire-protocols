import socket
import selectors 
import types 
from utils import decode_request, encode_request
from fnmatch import fnmatch

sel = selectors.DefaultSelector()

# do not actually do this
HOST = "127.0.0.1"
PORT = 54400

users = {}

def create_account(username, data):
    if data.logged_in:
        return f"ERROR: already logged into account {data.username}"
    if username in users:
        return "username taken. please login with your password"
    else:
        data.username = username
        data.supplying_pass = True
        return "enter password to create new account"

def supply_pass(password, data):
    if data.logged_in:
        return f"ERROR: already logged into account {data.username}"
    if data.supplying_pass:
        users.update({data.username: [hash(password), []]})
        data.supplying_pass = False
        return "SUCCESS: account created. please login with your new account"
    return "ERROR: should not be supplying password"

def login(username, password, data):
    if data.logged_in:
        return f"ERROR: already logged into account {data.username}"
    if username in users:
        if (hash(password) == users[username][0]):
            data.username = username
            data.logged_in = True
            return "SUCCESS: logged in"
        else:
            return "password is incorrect. please try again"
    return "username does not exist. please create a new account"

def list_accounts(pattern):
    accounts = [user for user in users if fnmatch(user, pattern)]
    count = len(accounts)
    return encode_request(str(count), accounts)

def send(recipient, message, data):
    if not data.logged_in:
        return "ERROR: not logged in"
    if recipient not in users:
        return "ERROR: recipient does not exist"
    messages = users[recipient][1]
    id = -1
    for msg in messages:
        id = max(id, int(msg[1]))
    users[recipient][1].append([data.username, str(id + 1), False, message])
    return "SUCCESS: message sent"

def read(count, data):
    if not data.logged_in:
        return "ERROR: not logged in"
    all_messages = users[data.username][1]
    count = min(count, len(all_messages))
    to_read = all_messages[len(all_messages) - count:]
    messages = []
    for sender, msg_id, _, msg in to_read[::-1]:
        messages.extend([sender, msg_id, msg])
    for i in range(count):
        users[data.username][1][len(all_messages) - count + i][2] = True 
    return encode_request(str(count), messages)

def delete_msg(IDs, data):
    if not data.logged_in:
        return "ERROR: not logged in"
    messages = users[data.username][1]
    print(messages)
    print(IDs)
    updated_messages = [msg for msg in messages if int(msg[1]) not in IDs]
    print(updated_messages)
    users[data.username][1] = updated_messages
    return "SUCCESS: messages deleted"

def delete_account(data):
    if not data.logged_in:
        return "ERROR: not logged in"
    users.pop(data.username)
    data.username = None
    data.logged_in = False
    return "SUCCESS: account deleted"

def logout(data):
    if not data.logged_in:
        return "ERROR: not logged in"
    data.username = None
    data.logged_in = False
    return "SUCCESS: logged out"

def num_msg(data):
    if not data.logged_in:
        return "ERROR: not logged in"
    return str(len(users[data.username][1]))

def handle_command(request, data):
    print(f"received request: [{request}]")
    request = decode_request(request)
    command = request[0]
    print("handling command:", command, request)
    match command:
        # TODO can paste try except into each case for index errors
        case "create_account":
            try:
                return create_account(request[1], data)
            except IndexError:
                return "usage: create_account [username]"
            except:
                return "ERROR: create_account"
        case "supply_pass":
            return supply_pass(request[1], data)
        case "login":
            return login(request[1], request[2], data)
        case "list_accounts":
            pattern = request[1] if len(request) > 1 else "*"
            return list_accounts(pattern)
        case "send":
            return send(request[1], request[2], data)
        case "read":
            return read(int(request[1]), data)
        case "delete_msg":
            return delete_msg(list(map(int, request[1].split(" "))), data)
        case "delete_account":
            return delete_account(data)
        case "logout":
            return logout(data)
        case "num_msg":
            return num_msg(data)
        case _:
            return "ERROR: invalid command"

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
            data.outb = b""

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
