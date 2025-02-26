import unittest
import grpc
from concurrent import futures
import chat_pb2
import chat_pb2_grpc
from server_grpc import Chat

class ChatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        cls.chat_service = Chat()
        chat_pb2_grpc.add_ChatServicer_to_server(cls.chat_service, cls.server)
        cls.port = "54400"
        cls.server.add_insecure_port(f"[::]:{cls.port}")
        cls.server.start()
        cls.channel = grpc.insecure_channel(f"localhost:{cls.port}")
        cls.stub = chat_pb2_grpc.ChatStub(cls.channel)

    @classmethod
    def tearDownClass(cls):
        cls.server.stop(None)

    def test_create_account(self):
        response = self.stub.create_account(chat_pb2.CreateAccount(username="user1"))
        self.assertEqual(response.message, "SUCCESS: enter password to create new account")
        response = self.stub.create_account(chat_pb2.CreateAccount(username="user1"))
        self.assertEqual(response.message, "ERROR: username taken. please login with your password")

    def test_supply_pass(self):
        self.stub.create_account(chat_pb2.CreateAccount(username="user2"))
        response = self.stub.supply_pass(chat_pb2.SupplyPass(username="user2", password="pass"))
        self.assertEqual(response.message, "SUCCESS: account created. please login with your new account")

    def test_login(self):
        self.stub.create_account(chat_pb2.CreateAccount(username="user3"))
        self.stub.supply_pass(chat_pb2.SupplyPass(username="user3", password="pass"))
        response = self.stub.login(chat_pb2.Login(username="user3", password="pass"))
        self.assertEqual(response.message, "SUCCESS: logged in")
        response = self.stub.login(chat_pb2.Login(username="user3", password="wrong"))
        self.assertEqual(response.message, "ERROR: incorrect password")

    def test_list_accounts(self):
        self.stub.create_account(chat_pb2.CreateAccount(username="testuser"))
        response = self.stub.list_accounts(chat_pb2.ListAccounts(pattern="test*"))
        self.assertGreater(int(response.count), 0)
        self.assertIn("testuser", response.accounts)

    def test_send_and_read_messages(self):
        self.stub.create_account(chat_pb2.CreateAccount(username="alice"))
        self.stub.create_account(chat_pb2.CreateAccount(username="bob"))
        self.stub.supply_pass(chat_pb2.SupplyPass(username="alice", password="pass"))
        self.stub.supply_pass(chat_pb2.SupplyPass(username="bob", password="pass"))
        response = self.stub.send(chat_pb2.Send(sender="alice", recipient="bob", message="Hello Bob"))
        self.assertEqual(response.message, "SUCCESS: message sent")
        response = self.stub.read(chat_pb2.Read(username="bob", count=1))
        self.assertEqual(response.count, "1")
        self.assertIn("Hello Bob", response.messages[0])

    def test_delete_messages(self):
        self.stub.create_account(chat_pb2.CreateAccount(username="charlie"))
        self.stub.supply_pass(chat_pb2.SupplyPass(username="charlie", password="pass"))
        self.stub.send(chat_pb2.Send(sender="alice", recipient="charlie", message="Test message"))
        response = self.stub.read(chat_pb2.Read(username="charlie", count=1))
        msg_id = 1
        response = self.stub.delete_msg(chat_pb2.DeleteMessages(username="charlie", ids=[msg_id]))
        self.assertEqual(response.message, "SUCCESS: messages deleted")

    def test_delete_account(self):
        self.stub.create_account(chat_pb2.CreateAccount(username="dave"))
        response = self.stub.delete_account(chat_pb2.DeleteAccount(username="dave"))
        self.assertEqual(response.message, "SUCCESS: account deleted")

    def test_logout(self):
        self.stub.create_account(chat_pb2.CreateAccount(username="eve"))
        self.stub.supply_pass(chat_pb2.SupplyPass(username="eve", password="pass"))
        self.stub.login(chat_pb2.Login(username="eve", password="pass"))
        response = self.stub.logout(chat_pb2.Logout(username="eve"))
        self.assertEqual(response.message, "SUCCESS: logged out")

    def test_num_messages(self):
        self.stub.create_account(chat_pb2.CreateAccount(username="frank"))
        response = self.stub.num_msg(chat_pb2.NumMessages(username="frank"))
        self.assertEqual(response.count, "0")
        self.stub.send(chat_pb2.Send(sender="alice", recipient="frank", message="Hello Frank"))
        response = self.stub.num_msg(chat_pb2.NumMessages(username="frank"))
        self.assertEqual(response.count, "1")

if __name__ == "__main__":
    unittest.main()
