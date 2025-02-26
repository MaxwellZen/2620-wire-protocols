import grpc
import chat_pb2
import chat_pb2_grpc
import sys

# grabs port from command-line arguments
if len(sys.argv) < 2 or not sys.argv[1].isdigit():
    print("Please provide a port for the connection")
    print("Example: python client_grpc.py 54400")
    sys.exit(0)
PORT = sys.argv[1]

def run():
    # stores what user is logged in at any given point in time
    global logged_in_user
    with grpc.insecure_channel("localhost:" + PORT) as channel:
        stub = chat_pb2_grpc.ChatStub(channel)
        logged_in_user = None
        
        while True:
            # handles incoming commands
            command = input("Enter command: ").split()
            match command[0]:
                case "create_account":
                    if logged_in_user:
                        print("ERROR: already logged into " + logged_in_user)
                        continue
                    reply = stub.create_account(chat_pb2.CreateAccount(username=command[1]))
                case "supply_pass":
                    if logged_in_user:
                        print("ERROR: already logged into " + logged_in_user)
                        continue
                    reply = stub.supply_pass(chat_pb2.SupplyPass(username=command[1], password=command[2]))
                case "login":
                    if logged_in_user:
                        print("ERROR: already logged into " + logged_in_user)
                        continue
                    reply = stub.login(chat_pb2.Login(username=command[1], password=command[2]))
                    if reply.message == "SUCCESS: logged in":
                        logged_in_user = command[1]
                case "list_accounts":
                    pattern = command[1] if len(command) > 1 else "*"
                    reply = stub.list_accounts(chat_pb2.ListAccounts(pattern=pattern))
                    print(f"{reply.count} accounts: {', '.join(reply.accounts)}")
                case "send":
                    if not logged_in_user:
                        print("ERROR: not logged in")
                        continue
                    recipient, message = command[1], " ".join(command[2:])
                    reply = stub.send(chat_pb2.Send(sender=logged_in_user, recipient=recipient, message=message))
                case "read":
                    if not logged_in_user:
                        print("ERROR: not logged in")
                        continue
                    reply = stub.read(chat_pb2.Read(username=logged_in_user, count=int(command[1])))
                case "logout":
                    if not logged_in_user:
                        print("ERROR: not logged in")
                        continue
                    reply = stub.logout(chat_pb2.Logout(username=logged_in_user))
                    if reply.message == "SUCCESS: logged out":
                        logged_in_user = None
                case "delete_msg":
                    if not logged_in_user:
                        print("ERROR: not logged in")
                        continue
                    ids = list(map(int, command[1:]))
                    reply = stub.delete_msg(chat_pb2.DeleteMessages(username=logged_in_user, ids=ids))
                case "delete_account":
                    if not logged_in_user:
                        print("ERROR: not logged in")
                        continue
                    reply = stub.delete_account(chat_pb2.DeleteAccount(username=logged_in_user))
                    if reply.message == "SUCCESS: account deleted":
                        logged_in_user = None
                case "num_msg":
                    if not logged_in_user:
                        print("ERROR: not logged in")
                        continue
                    reply = stub.num_msg(chat_pb2.NumMessages(username=logged_in_user))
                    print(f"{reply.count}")
                    continue
                case _:
                    print("ERROR: invalid command")
                    continue
            
            print(reply)

if __name__ == "__main__":
    run()
