import socket 
from tkinter import *
from utils import encode_request, decode_request

# don't actually do this 
HOST = "127.0.0.1"
PORT = 54400

"""
menus:
- greeting
    - greeting_label
    - login_menu_button
    - register_menu_button
- login
- create_user
- create_pass
- read_msg
- select_user
- send_msg
"""

class ChatApp:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        
        self.username = None

        self.root = Tk()
        self.root.title("Email.com")
        self.root.geometry('450x500')

        self.greeting_label = Label(text = "Welcome to email.com")
        self.login_menu_button = Button(self.root, text = "Login", command=self.greeting_to_login)
        self.register_menu_button = Button(self.root, text = "Create Account", command=self.greeting_to_create_user)
        self.greeting_created_label = Label(text = "Account created; please log in with your new account", fg='green')

        self.username_label = Label(text = "Username:")
        self.password_label = Label(text = "Password:")
        self.username_entry = Entry(self.root, width=20)
        self.password_entry = Entry(self.root, width=20)
        self.login_menu_back_button = Button(self.root, text = "Back to Menu", command=self.login_to_greeting)
        self.login_menu_login_button = Button(self.root, text = "Login", command=self.login_account)
        self.login_menu_not_user = Label(text = "Username does not exist; please create a new account", fg = 'red')
        self.login_menu_wrong_pass = Label(text = "Password is incorrect; please try again", fg = 'red')

        self.create_user_label = Label(text = "Input Your New Username:")
        self.create_user_create_button = Button(self.root, text = "Create Username", command = self.create_new_user)
        self.create_user_back_button = Button(self.root, text = "Back to Menu", command=self.create_user_to_greeting)
        self.create_user_again_label = Label(self.root, text = "Username taken; please log in or choose another username", fg='red')

        self.create_pass_label = Label(text = "Input Your New Password:")
        self.create_pass_create_button = Button(self.root, text = "Create Password", command = self.create_new_pass)
        self.create_pass_back_button = Button(self.root, text = "Back to Menu", command=self.create_pass_to_greeting)

        self.reading_msg = False

    def main_loop(self):
        self.greeting_label.pack()
        self.register_menu_button.pack()
        self.login_menu_button.pack()

        self.root.mainloop()

    def readmsg_update(self):
        self.root.after(1000, self.readmsg_update)

    def setup_login(self):
        self.username_label.pack()
        self.username_entry.pack()
        self.password_label.pack()
        self.password_entry.pack()
        self.login_menu_login_button.pack()
        self.login_menu_back_button.pack()

    def close_login(self):
        self.username_label.pack_forget()
        self.username_entry.pack_forget()
        self.username_entry.delete(0, 'end')
        self.password_label.pack_forget()
        self.password_entry.pack_forget()
        self.password_entry.delete(0, 'end')
        self.login_menu_login_button.pack_forget()
        self.login_menu_back_button.pack_forget()
        self.login_menu_not_user.pack_forget()
        self.login_menu_wrong_pass.pack_forget()
    
    def reset_login(self):
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.login_menu_not_user.pack_forget()
        self.login_menu_wrong_pass.pack_forget()

    def setup_greeting(self):
        self.greeting_label.pack()
        self.register_menu_button.pack()
        self.login_menu_button.pack()
    
    def close_greeting(self):
        self.greeting_label.pack_forget()
        self.login_menu_button.pack_forget()
        self.register_menu_button.pack_forget()
        self.greeting_created_label.pack_forget()

    def setup_create_user(self):
        self.username_label.pack()
        self.username_entry.pack()
        self.create_user_create_button.pack()
        self.create_user_back_button.pack()

    def close_create_user(self):
        self.username_label.pack_forget()
        self.username_entry.pack_forget()
        self.username_entry.delete(0, 'end')
        self.create_user_create_button.pack_forget()
        self.create_user_back_button.pack_forget()
        self.create_user_again_label.pack_forget()

    def setup_create_pass(self):
        self.create_pass_label.pack()
        self.password_entry.pack()
        self.create_pass_create_button.pack()
        self.create_pass_back_button.pack()
    
    def close_create_pass(self):
        self.create_pass_label.pack_forget()
        self.password_entry.pack_forget()
        self.password_entry.delete(0,'end')
        self.create_pass_create_button.pack_forget()
        self.create_pass_back_button.pack_forget()

    def greeting_to_login(self):
        self.close_greeting()
        self.setup_login()
        self.root.update_idletasks()

    def login_to_greeting(self):
        self.close_login()
        self.setup_greeting()
        self.root.update_idletasks()

    def create_user_to_greeting(self):
        self.close_create_user()
        self.setup_greeting()
        self.root.update_idletasks()
    
    def greeting_to_create_user(self):
        self.close_greeting()
        self.setup_create_user()
        self.root.update_idletasks()

    def create_pass_to_greeting(self):
        self.close_create_pass()
        self.setup_greeting()
        self.root.update_idletasks()

    def create_user_to_create_pass(self):
        self.close_create_user()
        self.setup_create_pass()
        self.root.update_idletasks()

    def login_account(self):
        message = encode_request("login", [self.username_entry.get(), self.password_entry.get()])
        message = message.encode("utf-8")
        self.sock.sendall(message)
        data = self.sock.recv(1024)
        data = data.decode("utf-8")
        if data == "SUCCESS: logged in":
            pass
        elif data == "Password is incorrect. Please try again":
            self.reset_login()
            self.login_menu_wrong_pass.pack()
            self.root.update_idletasks()
        elif data == "Username does not exist. Please create a new account":
            self.reset_login()
            self.login_menu_not_user.pack()
            self.root.update_idletasks()
        else:
            print(data)
            self.root.destroy()

    def create_new_user(self):
        message = encode_request("create_account", [self.username_entry.get()])
        message = message.encode("utf-8")
        self.sock.sendall(message)
        data = self.sock.recv(1024)
        data = data.decode("utf-8")
        if data == "Username taken. Please login with your password":
            self.create_user_again_label.pack()
            self.root.update_idletasks()
        elif data == "Enter password to create new account":
            self.username = self.username_entry.get()
            self.create_user_to_create_pass()
        else:
            print(data)
            self.root.destroy()

    def create_new_pass(self):
        message = encode_request("supply_pass", [self.password_entry.get()])
        message = message.encode("utf-8")
        self.sock.sendall(message)
        data = self.sock.recv(1024)
        data = data.decode("utf-8")
        if data == "SUCCESS: account created. Please login with your new account":
            self.create_pass_to_greeting()
            self.greeting_created_label.pack()
            self.root.update_idletasks()
        else:
            print(data)
            self.root.destroy()

def main():
    chatapp = ChatApp()
    chatapp.main_loop()

    # while True:
    #     message = input("Enter a message to send to the server: ")
    #     if message == "exit":
    #         break 
    #     message = message.encode("utf-8")
    #     s.sendall(message)
    #     data = s.recv(1024)
    #     data = data.decode("utf-8")
    #     print(f"Received: {data}")

    # s.close()

if __name__ == "__main__":
    main()