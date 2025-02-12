import server
import server_json
import types

data = types.SimpleNamespace(username=None, logged_in=False, supplying_pass=False)

def test_login():
    assert(server.create_account("maxwell", data) == "enter password to create new account")
    assert(data.username == "maxwell")
    assert(data.supplying_pass == True)

    assert(server.supply_pass("password", data) == "SUCCESS: account created. please login with your new account")
    assert(data.supplying_pass == False)

    assert(server.login("maxwell", "password", data) == "SUCCESS: logged in") 
    assert(data.username == "maxwell")
    assert(data.logged_in == True)

    assert(server.create_account("andrew", data) == f"ERROR: already logged into account {data.username}")
    assert(server.supply_pass("andrew", data) == f"ERROR: already logged into account {data.username}")
    assert(server.login("andrew", "password", data) == f"ERROR: already logged into account {data.username}")

    assert(server.logout(data) == "SUCCESS: logged out")
    assert(data.username == None)
    assert(data.logged_in == False)
    assert(server.logout(data) == "ERROR: not logged in")

    assert(server.create_account("maxwell", data) == "username taken. please login with your password")
    assert(server.supply_pass("password", data) == "ERROR: should not be supplying password")
    
    print("login tests passed")

def test_login_json():
    assert(server_json.create_account("maxwell", data) == {"status": "success", "message": "enter password to create new account"})
    assert(data.username == "maxwell")
    assert(data.supplying_pass == True)

    assert(server_json.supply_pass("password", data) == {"status": "success", "message": "account created. please login with your new account"})
    assert(data.supplying_pass == False)

    assert(server_json.login("maxwell", "password", data) == {"status": "success", "message": "logged in"}) 
    assert(data.username == "maxwell")
    assert(data.logged_in == True)

    assert(server_json.create_account("andrew", data) == {"status": "error", "message": f"already logged into account {data.username}"})
    assert(server_json.supply_pass("andrew", data) == {"status": "error", "message": f"already logged into account {data.username}"})
    assert(server_json.login("andrew", "password", data) == {"status": "error", "message": f"already logged into account {data.username}"})

    assert(server_json.logout(data) == {"status": "success", "message": "logged out"})
    assert(data.username == None)
    assert(data.logged_in == False)
    assert(server_json.logout(data) == {"status": "error", "message": "not logged in"})

    assert(server_json.create_account("maxwell", data) == {"status": "error", "message": "username taken. please login with your password"})
    assert(server_json.supply_pass("password", data) == {"status": "error", "message": "should not be supplying password"})
    
    print("login tests json passed")

def test_accounts():
    server.create_account("andrew", data)
    server.supply_pass("password_andrew", data)
    server.create_account("johnathan", data)
    server.supply_pass("password_johnathan", data)
    assert(server.list_accounts("*") == "3 [maxwell] [andrew] [johnathan]")
    assert(server.list_accounts("*an*") == "2 [andrew] [johnathan]")

    server.login("johnathan", "password_johnathan", data)
    assert(server.delete_account(data) == "SUCCESS: account deleted")
    assert(data.username == None)
    assert(data.logged_in == False)
    assert(server.delete_account(data) == "ERROR: not logged in")
    assert(server.list_accounts("*") == "2 [maxwell] [andrew]")

    print("account tests passed")

def test_accounts_json():
    server_json.create_account("andrew", data)
    server_json.supply_pass("password_andrew", data)
    server_json.create_account("johnathan", data)
    server_json.supply_pass("password_johnathan", data)
    assert(server_json.list_accounts("*") == {"status": "success", "count": 3, "accounts": ["maxwell", "andrew", "johnathan"]})
    assert(server_json.list_accounts("*an*") == {"status": "success", "count": 2, "accounts": ["andrew", "johnathan"]})

    server_json.login("johnathan", "password_johnathan", data)
    assert(server_json.delete_account(data) == {"status": "success", "message": "account deleted"})
    assert(data.username == None)
    assert(data.logged_in == False)
    assert(server_json.delete_account(data) == {"status": "error", "message": "not logged in"})
    assert(server_json.list_accounts("*") == {"status": "success", "count": 2, "accounts": ["maxwell", "andrew"]})

    print("account tests json passed")

def test_messages():
    assert(server.send("andrew", "I'm not logged in", data) == "ERROR: not logged in")
    server.login("maxwell", "password", data)
    assert(server.send("johnathan", "You do not exist", data) == "ERROR: recipient does not exist")
    assert(server.send("andrew", "m0", data) == "SUCCESS: message sent")
    server.send("andrew", "m1", data)
    server.send("andrew", "m2", data)
    server.send("andrew", "m3", data)
    server.send("andrew", "m4", data)
    server.logout(data)

    assert(server.read(3, data) == "ERROR: not logged in")
    server.login("andrew", "password_andrew", data)
    assert(server.read(3, data) == "3 [maxwell] [4] [m4] [maxwell] [3] [m3] [maxwell] [2] [m2]")
    assert(server.read(10, data) == "5 [maxwell] [4] [m4] [maxwell] [3] [m3] [maxwell] [2] [m2] [maxwell] [1] [m1] [maxwell] [0] [m0]")
    assert(server.num_msg(data) == "5")
    assert(server.delete_msg([1, 2], data) == "SUCCESS: messages deleted")
    assert(server.read(10, data) == "3 [maxwell] [4] [m4] [maxwell] [3] [m3] [maxwell] [0] [m0]")
    assert(server.num_msg(data) == "3")
    assert(server.delete_msg([4], data) == "SUCCESS: messages deleted")
    assert(server.read(10, data) == "2 [maxwell] [3] [m3] [maxwell] [0] [m0]")
    assert(server.num_msg(data) == "2")

    print("message tests passed")

def test_messages_json():
    server_json.logout(data)
    assert(server_json.send("andrew", "I'm not logged in", data) == {"status": "error", "message": "not logged in"})
    server_json.login("andrew", "password_andrew", data)
    assert(server_json.send("johnathan", "You do not exist", data) == {"status": "error", "message": "recipient does not exist"})
    assert(server_json.send("maxwell", "a0", data) == {"status": "success", "message": "message sent"})
    server_json.send("maxwell", "a1", data)
    server_json.send("maxwell", "a2", data)
    server_json.send("maxwell", "a3", data)
    server_json.send("maxwell", "a4", data)
    server_json.logout(data)
    
    assert(server_json.read(3, data) == {"status": "error", "message": "not logged in"})
    server_json.login("maxwell", "password", data)
    assert(server_json.read(3, data) == {"status": "success", "count": 3, "messages": [{"sender": "andrew", "id": "4", "message": "a4"}, \
                                                                                       {"sender": "andrew", "id": "3", "message": "a3"}, \
                                                                                       {"sender": "andrew", "id": "2", "message": "a2"}]})
    assert(server_json.read(10, data) == {"status": "success", "count": 5, "messages": [{"sender": "andrew", "id": "4", "message": "a4"}, \
                                                                                        {"sender": "andrew", "id": "3", "message": "a3"}, \
                                                                                        {"sender": "andrew", "id": "2", "message": "a2"}, \
                                                                                        {"sender": "andrew", "id": "1", "message": "a1"}, \
                                                                                        {"sender": "andrew", "id": "0", "message": "a0"}]})
    assert(server_json.num_msg(data) == {"status": "success", "message": "5"})
    assert(server_json.delete_msg([1, 2], data) == {"status": "success", "message": "messages deleted"})
    assert(server_json.read(10, data) == {"status": "success", "count": 3, "messages": [{"sender": "andrew", "id": "4", "message": "a4"}, \
                                                                                        {"sender": "andrew", "id": "3", "message": "a3"}, \
                                                                                        {"sender": "andrew", "id": "0", "message": "a0"}]})
    assert(server_json.num_msg(data) == {"status": "success", "message": "3"})
    assert(server_json.delete_msg([4], data) == {"status": "success", "message": "messages deleted"})
    assert(server_json.read(10, data) == {"status": "success", "count": 2, "messages": [{"sender": "andrew", "id": "3", "message": "a3"}, \
                                                                                        {"sender": "andrew", "id": "0", "message": "a0"}]})
    assert(server_json.num_msg(data) == {"status": "success", "message": "2"})
    print("message tests json passed")

if __name__ == "__main__":
    test_login()
    test_login_json()
    test_accounts()
    test_accounts_json()
    test_messages()
    test_messages_json()