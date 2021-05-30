import socket
import json
import getpass
import os
import base64
from cryptography.fernet import Fernet

with open(os.getcwd() + '\\key.dat', 'rb') as kf:
    key = kf.read()
key = base64.b64decode(key)
fernet = Fernet(key)

def connect(host='127.0.0.1', port=8888):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    welcome_request = {'method': 'welcome', 'text': ''}
    s.sendall(json.dumps(welcome_request).encode())
    welcome_message = s.recv(1024)
    return s, host, port, welcome_message.decode()

def disconnect(conn):
    conn.close()

def request(conn, method, text):
    req = {'method': method, 'text': text}
    conn.sendall(json.dumps(req).encode())
    data = conn.recv(4096)
    return data.decode()

def get_pass(fernet):
    return fernet.encrypt(getpass.getpass('\tPassword: ').encode()).decode()

def authorize(conn, username, password):
    res = request(conn, 'authorize', f'{username}; {password}')
    while res != 'ok':
        again = input(f'{res}. Try again? (y/n, n means register) ')
        if again.lower() == 'y':
            username = input('\tUsername: ')
            password = get_pass(fernet)
            res = request(conn, 'authorize', f'{username}; {password}')
        else:
            username = input('\tUsername: ')
            password = get_pass(fernet)
            return register(conn, username, password)
    return f'You can make requests now, {username}!'

def register(conn, username, password):
    res = request(conn, 'register', f'{username}; {password}')
    while res != 'ok':
        again = input(f'{res}. Try again? (y/n, n means authorize) ')
        if again.lower() == 'y':
            username = input('\tUsername: ')
            password = get_pass(fernet)
            res = request(conn, 'register', f'{username}; {password}')
        else:
            username = input('\tUsername: ')
            password = get_pass(fernet)
            return authorize(conn, username, password)
    return f'You can make requests now, {username}!'

if __name__ == '__main__':
    conn, host, port, welcome_message = connect()
    print(f'Connected to {host}:{port}')
    print('Server message:', welcome_message)
    try:
        auth = input('Enter authorization option: ')
        if auth == '1' or auth == '2':
            username = input('\tUsername: ')
            password = get_pass(fernet)
            if auth == '1':
                print(authorize(conn, username, password))
            else:
                print(register(conn, username, password))
        while True:
            try:
                ans = input('Request: ')
                if ans == 'disconnect':
                    disconnect(conn)
                    print('Disconnected!')
                    break
                else:
                    ans = ans.split(' ')
                    method, text = ans[0], " ".join(ans[1:])
                    print('Server message:', request(conn, method, text))
            except KeyboardInterrupt:
                disconnect(conn)
                print('\nDisconnected!')
                break
    except KeyboardInterrupt:
        disconnect(conn)
        print('\nDisconnected!')