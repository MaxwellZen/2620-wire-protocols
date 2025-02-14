# 2620-wire-protocols

## Data Structures
users: dictionary that stores {username: [password, messages]}

messages: array of arrays [user, id, msg]
- user is the sender of the message

information stored on socket:
- username: string that stores what username the client is logged in to
- logged_in: boolean that stores whether the client is logged into any account
- supplying_pass: boolean that stores whether the client is attempting to create an account and is supplying the password for that

## Wire Protocol

Commands are inputted as command [arg1] [arg2]. 

Examples:
- create_account [andrew]
- send [maxwell] [hello!]

Handled by encode_request and decode_request (and encode_json for JSON). If brackets or backslashes are in the text, they get replaced by "\\\[" or "\\\\"

## Commands

Each command has associated SUCCESS and ERROR messages, such as "ERROR: not logged in" or "SUCCESS: message sent"

create_account [username]:
- Creates new account with given username. If the username is taken, prompt user to log in.
- Username limited to 32 characters

supply_pass [password]:
- Supplies password for account creation.

login [username] [password]:
- Logs in to an account.

list_accounts [pattern]: 
- Lists all accounts matching the given wildcard pattern. Default to all accounts.
- output: [count] [user1] … [userk]
    
send [username] [message]: 
- Sends a message to a recipient.

read [count]: 
- Displays the specified number of unread messages. If count > # unread, then return # unread
- output: n [sender1] [id1] [msg1] … [sendern] [idn] [msgn]
    
delete_msg [id1, … idn]:
- Deletes the messages with the specified IDs. Ignores invalid or non-existent IDs.

delete_account: 
- Deletes the currently logged-in account.

logout: 
- Logs out of the currently logged-in account.

num_msg: 
- Returns the number of unread messages for the logged-in user.
- output: n

Example commands:
- create_account [alice]
- supply_pass [password]
- login [alice] [password]

Assuming you also created another account named bob:
- send [bob] [hello!]
- read [10]
- logout 

## Graphical User Interface

The GUI is done in Python's `tkinter` library and is extremely barebones (pretty much all elements are just stacked on top of each other). The design is built around the `ChatApp` class, which is initiated with three arguments:

- `host`: server IP address
- `port`: server port
- `use_json`: whether or not the wire protocol is communicating via JSON

Beyond that, the GUI is centered around the following seven menus:
- `greeting`: offers option to create new account or login
- `login`: prompts user for username and password
- `create_user`: prompts user for new username
- `create_pass`: prompts user for new password
- `readmsg`: displays emails for logged-in user
- `selectuser`: allows user to select another user to send an email to
- `sendmsg`: prompts user to write an email

Nearly all variables and functions are named after their relevant menu, but that might not be true for some of the variables created earlier on when I did not set this convention (and if I were to go back to improve code design this is one of the first things I would fix).

### Usage

The intended usage is shown in the main function of `client_gui.py`, and just requires the following two lines:

```python
chatapp = ChatApp(host, port, USE_JSON)
chatapp.main_loop()
```

### Message Updates

One extra feature that we implemented is automatic updating of emails without the user having to manually refresh. We achieve this by running an update function once every second, which first checks if the user is currently on the `readmsg` menu, and if so then updates the messages. This is pretty inefficient and places an increasing load on the server as the number of users increases, but we are not so worried about this because even if there were millions of users the server is likely capable of handling millions of these queries per second (since sending the information for 5 emails is not very expensive). If we were to make this more robust, we would have each client have two sockets: one for normal queries, and another which waits for notifications that the user's emails have been updated (ie when a new email comes in). On the server end, we would have a list of active "secondary sockets" for each username, and when that user receives an email we would notify each of those sockets.