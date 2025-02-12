import socket
import selectors 
import types 
from utils import decode_request, encode_request
from fnmatch import fnmatch
import sys

sel = selectors.DefaultSelector()

# dictionary to store user info
users = {}

def create_account(username, data):
    """
    Creates new account with given username.
    If the username is taken, prompt user to log in.
    """
    if data.logged_in:
        return f"ERROR: already logged into account {data.username}"
    if username in users:
        return "username taken. please login with your password"
    else:
        data.username = username
        data.supplying_pass = True
        return "enter password to create new account"

def supply_pass(password, data):
    """
    Supplies password for account creation.
    """
    if data.logged_in:
        return f"ERROR: already logged into account {data.username}"
    if data.supplying_pass:
        # hash password before storing it
        users.update({data.username: [hash(password), []]})
        data.supplying_pass = False
        return "SUCCESS: account created. please login with your new account"
    return "ERROR: should not be supplying password"

def login(username, password, data):
    """
    Logs in to an account.
    """
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
    """
    Lists all accounts matching the given wildcard pattern. Default to all accounts.
    """
    accounts = [user for user in users if fnmatch(user, pattern)]
    count = len(accounts)
    return encode_request(str(count), accounts)

def send(recipient, message, data):
    """
    Sends a message to a recipient.
    """
    if not data.logged_in:
        return "ERROR: not logged in"
    if recipient not in users:
        return "ERROR: recipient does not exist"
    messages = users[recipient][1]
    # generate new id that is not currently in use
    id = -1
    for msg in messages:
        id = max(id, int(msg[1]))
    users[recipient][1].append([data.username, str(id + 1), False, message])
    return "SUCCESS: message sent"

def read(count, data):
    """
    Displays the specified number of unread messages. 
    """
    if not data.logged_in:
        return "ERROR: not logged in"
    all_messages = users[data.username][1]
    count = min(count, len(all_messages))
    to_read = all_messages[len(all_messages) - count:]
    messages = []
    # display messages in order of most recent to least recent
    for sender, msg_id, _, msg in to_read[::-1]:
        messages.extend([sender, msg_id, msg])
    # mark messages as read
    for i in range(count):
        users[data.username][1][len(all_messages) - count + i][2] = True 
    return encode_request(str(count), messages)

def delete_msg(IDs, data):
    """
    Deletes the messages with the specified IDs. 
    Ignores invalid or non-existent IDs.
    """
    if not data.logged_in:
        return "ERROR: not logged in"
    messages = users[data.username][1]
    updated_messages = [msg for msg in messages if int(msg[1]) not in IDs]
    users[data.username][1] = updated_messages
    return "SUCCESS: messages deleted"

def delete_account(data):
    """
    Deletes the currently logged-in account.
    """
    if not data.logged_in:
        return "ERROR: not logged in"
    users.pop(data.username)
    data.username = None
    data.logged_in = False
    return "SUCCESS: account deleted"

def logout(data):
    """
    Logs out of the currently logged-in account.
    """
    if not data.logged_in:
        return "ERROR: not logged in"
    data.username = None
    data.logged_in = False
    return "SUCCESS: logged out"

def num_msg(data):
    """
    Returns the number of unread messages for the logged-in user.
    """
    if not data.logged_in:
        return "ERROR: not logged in"
    return str(len(users[data.username][1]))

def handle_command(request, data):
    """
    Handles incoming commands from the client.
    """
    print(f"received request: [{request}]")
    request = decode_request(request)
    command = request[0]
    print("handling command:", command, request)
    match command:
        case "create_account":
            try:
                return create_account(request[1], data)
            except:
                return "usage: create_account [username]"
        case "supply_pass":
            try:
                return supply_pass(request[1], data)
            except:
                return "usage: supply_pass [password]"
        case "login":
            try:
                return login(request[1], request[2], data)
            except:
                return "usage: login [username] [password]"
        case "list_accounts":
            pattern = request[1] if len(request) > 1 else "*"
            return list_accounts(pattern)
        case "send":
            try:
                return send(request[1], request[2], data)
            except:
                return "usage: send [recipient] [message]"
        case "read":
            try:
                return read(int(request[1]), data)
            except:
                return "usage: read [n]"
        case "delete_msg":
            try:
                return delete_msg(list(map(int, request[1].split(" "))), data)
            except:
                return "usage: delete_msg [i j k]"
        case "delete_account":
            return delete_account(data)
        case "logout":
            return logout(data)
        case "num_msg":
            return num_msg(data)
        case _:
            return "ERROR: invalid command"

def accept_wrapper(sock):
    """
    Accepts new connections
    """
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"", username=None, logged_in=False, supplying_pass=False)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE 
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    """
    Services existing connections and reads/writes to the connected socket
    """
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


def main():
    # grabs host and port from command-line arguments
    if len(sys.argv) < 3 or not sys.argv[2].isdigit():
        print("Please provide a host and port for the socket connection")
        print("Example: python3 client_gui.py 127.0.0.1 54400")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])
    
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    print("Listening on", (host, port))
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


if __name__ == "__main__":
    main()