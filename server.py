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
        return f"ERROR: already logged in to account {data.username}"
    if username in users:
        return "Username taken. Please login with your password"
    else:
        data.username = username
        data.supplying_pass = True
        return "Enter password to create new account"

def supply_pass(password, data):
    if data.logged_in:
        return f"ERROR: already logged in to account {data.username}"
    if data.supplying_pass:
        users.update({data.username: (password, [])})
        data.supplying_pass = False
        return "SUCCESS: account created. Please login with your new account"
    return "ERROR: should not be supplying password"

def login(username, password, data):
    if data.logged_in:
        return f"ERROR: already logged in to account {data.username}"
    if username in users:
        if (password == users[username][0]):
            data.username = username
            data.logged_in = True
            return "SUCCESS: logged in"
    return "Username does not exist. Please create a new account"

def list_accounts(pattern):
    accounts = [user for user in users if fnmatch(user, pattern)]
    # TODO (when GUI is made) If there are more accounts than can comfortably be displayed, allow iterating through the accounts.
    count = len(accounts)
    return f"{count} " + " ".join(accounts)

def send(recipient, message, data):
    if not data.logged_in:
        return "ERROR: not logged in"
    if recipient not in users:
        return "ERROR: recipient does not exist"
    # TODO temp solution: theoretically ID's are in order, would get messed up if processed in wrong order
    id = str(len(users[recipient][1]))
    users[recipient][1].append((data.username, id, False, message))
    return "SUCCESS: message sent"

def read(count, data):
    if not data.logged_in:
        return "ERROR: not logged in"
    count = min(count, len(users[data.username][1]))
    to_read = users[data.username][1][:int(count)]
    messages = [f"{sender} {msg_id} {msg}" for sender, msg_id, _, msg in to_read]
    for i in range(len(to_read)):
        sender, msg_id, _, msg = to_read[i]
        to_read[i] = (sender, msg_id, True, msg)
    users[data.username][1][:int(count)] = to_read
    return f"[{len(to_read)}] " + " ".join(messages)

def delete_msg(IDs, data):
    if not data.logged_in:
        return "ERROR: not logged in"
    messages = users[data.username][1]
    users[data.username][1] = [msg for msg in messages if msg[1] not in IDs]
    return "SUCCESS: Messages deleted"

def delete_account(data):
    if not data.logged_in:
        return "ERROR: not logged in"
    users.pop(data.username)    # no need to delete the msgs for the user bc everything gets deleted anyways?
    data.username = None
    data.logged_in = False
    return "SUCCESS: account deleted"

def logout(data):
    if not data.logged_in:
        return "ERROR: not logged in"
    data.username = None
    data.logged_in = False
    return "SUCCESS: logged out"

def handle_command(request, data):
    request = decode_request(request)
    command = request[0]
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
