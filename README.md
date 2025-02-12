# 2620-wire-protocols

# Data Structures
users: dictionary that stores {username: [password, messages]}

messages: array of arrays [user, id, msg]
- user is the sender of the message

information stored on socket:
- username: string that stores what username the client is logged in to
- logged_in: boolean that stores whether the client is logged into any account
- supplying_pass: boolean that stores whether the client is attempting to create an account and is supplying the password for that

# Wire Protocol

Commands are inputted as command [arg1] [arg2]. 

Examples:
- create_account [andrew]
- send [maxwell] [hello!]

Handled by encode_request and decode_request (and encode_json for JSON). If brackets or backslashes are in the text, they get replaced by "\\\[" or "\\\\"

# Commands

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
- create_account [andrew]
- supply_pass [password]
- login [andrew] [password]
Assuming you also created another account named maxwell:
- send [maxwell] [hello!]
- read [10]
- logout 