# Communication 2: RPC

Documentation is generally very similar to that of the original wire protocol implementation. Main distrinctions include minor data structure differences and the usage of commands, as they are implemented without our wire protocol parsing so there are not any brackets surrounding the arguments.

## Data Structures
self.users: server-side dictionary that stores {username: [password, messages, logged_in, supplying_pass]}
- password: string storing password of user
- messages: array of arrays [user, id, msg]
    - user is the sender of the message
- logged_in: boolean storing whether the user is currently logged_in
- supplying_pass: boolean storing whether the user is providing a password to create an account

logged_in_user: client-side string used for storing what user (if any) the current client is logged into
- important as gRPC is stateless, so needed for determining permissions of certain commands (e.g., deleting messages)

## Commands & Usage

Each command has associated SUCCESS and ERROR messages, such as "ERROR: not logged in" or "SUCCESS: message sent"

create_account username:
- Creates new account with given username. If the username is taken, prompt user to log in.
- Username limited to 32 characters

supply_pass password:
- Supplies password for account creation.

login username password:
- Logs in to an account.

list_accounts pattern: 
- Lists all accounts matching the given wildcard pattern. Default to all accounts.
- output: count user1 … userk
    
send username message: 
- Sends a message to a recipient.

read count: 
- Displays the specified number of unread messages. If count > # unread, then return # unread
- output: n sender1 id1 msg1 … sendern idn msgn
    
delete_msg id1 … idn:
- Deletes the messages with the specified IDs. Ignores invalid or non-existent IDs.

delete_account: 
- Deletes the currently logged-in account.

logout: 
- Logs out of the currently logged-in account.

num_msg: 
- Returns the number of unread messages for the logged-in user.
- output: n

Example commands:
- create_account alice
- supply_pass password
- login alice password

Assuming you also created another account named bob:
- send bob hello!
- read 10
- logout 
