import grpc
import chat_pb2
import chat_pb2_grpc
from concurrent import futures
from fnmatch import fnmatch
import sys

class Chat(chat_pb2_grpc.Chat):
    # dictionary for storying user information
    def __init__(self):
        self.users = {}

    # all functions have the same functionality as their non-grpc equivalents as in server.py   
    def create_account(self, request, context):
        username = request.username
        if username in self.users:
            return chat_pb2.StatusReply(message="ERROR: username taken. please login with your password")
        self.users[username] = {"password": None, "messages": [], "logged_in": False, "supplying_pass": True}
        return chat_pb2.StatusReply(message="SUCCESS: enter password to create new account")

    def supply_pass(self, request, context):
        username = request.username
        if not self.users[username]["supplying_pass"]:
            return chat_pb2.StatusReply(message="ERROR: should not be supplying password")
        self.users[username]["password"] = request.password
        self.users[username]["supplying_pass"] = False
        return chat_pb2.StatusReply(message="SUCCESS: account created. please login with your new account")

    def login(self, request, context):
        username = request.username
        password = request.password
        if username not in self.users:
            return chat_pb2.StatusReply(message="ERROR: user does not exist")
        if self.users[username]["password"] != password:
            return chat_pb2.StatusReply(message="ERROR: incorrect password")
        self.users[username]["logged_in"] = True
        return chat_pb2.StatusReply(message="SUCCESS: logged in")

    def list_accounts(self, request, context):
        matched_users = [user for user in self.users if fnmatch(user, request.pattern)]
        return chat_pb2.ListAccountsReply(count=str(len(matched_users)), accounts=matched_users)

    def send(self, request, context):
        recipient = request.recipient
        message = request.message

        if recipient not in self.users:
            return chat_pb2.StatusReply(message="ERROR: recipient does not exist")
        message_id = len(self.users[recipient]["messages"]) + 1
        self.users[recipient]["messages"].append({
            "sender": "current_user",  # Replace with actual sender logic
            "id": message_id,
            "msg": message
        })
        return chat_pb2.StatusReply(message="SUCCESS: message sent")

    def read(self, request, context):
        username = request.username
        count = request.count

        messages = self.users[username]["messages"][-count:]
        return chat_pb2.ReadReply(
            count=str(len(messages)),
            messages=[f"From {msg['sender']}: {msg['msg']}" for msg in messages]
        )

    def delete_msg(self, request, context):
        username = request.username
        ids = request.ids

        self.users[username]["messages"] = [msg for msg in self.users[username]["messages"] if msg["id"] not in ids]
        return chat_pb2.StatusReply(message="SUCCESS: messages deleted")

    def delete_account(self, request, context):
        username = request.username

        del self.users[username]
        return chat_pb2.StatusReply(message="SUCCESS: account deleted")
    
    def logout(self, request, context):
        username = request.username

        self.users[username]["logged_in"] = False
        return chat_pb2.StatusReply(message="SUCCESS: logged out")

    def num_msg(self, request, context):
        username = request.username
        return chat_pb2.NumMessagesReply(count=str(len(self.users[username]["messages"])))


def serve():
    # grabs port from command-line arguments
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        print("Please provide a port for the connection")
        print("Example: python server_grpc.py 54400")
        sys.exit(0)
    PORT = sys.argv[1]

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
    server.add_insecure_port("[::]:" + PORT)
    server.start()
    print("Listening on " + PORT)
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
