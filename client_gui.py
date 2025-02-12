import socket 
from tkinter import *

# don't actually do this 
HOST = "127.0.0.1"
PORT = 54400





def setup_login_menu():
    global root, login_menu_button, register_menu_button, greeting_label, username_entry, password_entry, login_menu_back_button, login_menu_login_button, username_label, password_label
    greeting_label.pack_forget()
    login_menu_button.pack_forget()
    register_menu_button.pack_forget()

    username_label.pack()
    username_entry.pack()
    password_label.pack()
    password_entry.pack()
    login_menu_back_button.pack()
    login_menu_login_button.pack()
    root.update_idletasks()

def login_to_greeting():
    global root, login_menu_button, register_menu_button, greeting_label, username_entry, password_entry, login_menu_back_button, login_menu_login_button, username_label, password_label

    username_label.pack_forget()
    username_entry.pack_forget()
    username_entry.delete(0, 'end')
    password_label.pack_forget()
    password_entry.pack_forget()
    password_entry.delete(0, 'end')
    login_menu_back_button.pack_forget()
    login_menu_login_button.pack_forget()

    greeting_label.pack()
    register_menu_button.pack()
    login_menu_button.pack()
    root.update_idletasks()

def login_account():
    pass

def main():
    global root, login_menu_button, register_menu_button, greeting_label, username_entry, password_entry, login_menu_back_button, login_menu_login_button, username_label, password_label

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((HOST, PORT))

    root = Tk()
    root.title("Email.com")
    root.geometry('800x500')

    greeting_label = Label(text = "Welcome to email.com")
    login_menu_button = Button(root, text = "Login", command=setup_login_menu)
    register_menu_button = Button(root, text = "Create Account")

    username_label = Label(text = "Username:")
    password_label = Label(text = "Password:")
    username_entry = Entry(root, width=20)
    password_entry = Entry(root, width=20)
    login_menu_back_button = Button(root, text = "Back", command=login_to_greeting)
    login_menu_login_button = Button(root, text= "Login", command=login_account)

    greeting_label.pack()
    register_menu_button.pack()
    login_menu_button.pack()

    root.mainloop()

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