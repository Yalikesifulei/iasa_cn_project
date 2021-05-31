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
    welcome_message = s.recv(1024).decode()
    auth_opt_request = {'method': 'welcome', 'text': 'auth_opt'}
    s.sendall(json.dumps(auth_opt_request).encode())
    auth_opt = s.recv(1024).decode()
    return s, host, port, welcome_message, json.loads(auth_opt)

def disconnect(conn):
    conn.close()

def request(conn, method, text):
    req = {'method': method, 'text': text}
    conn.sendall(json.dumps(req).encode())
    data = conn.recv(4096).decode()
    return data

def get_pass(fernet):
    return fernet.encrypt(getpass.getpass('\tPassword: ').encode()).decode()

def authorize(conn, username, password):
    res = request(conn, 'authorize', f'{username}; {password}')
    while res != 'auth_ok':
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
    while res != 'auth_ok':
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
    try:
        conn, host, port, welcome_message, auth_opt = connect()
        print(f'Connected to {host}:{port}')
        print('Server message:', welcome_message)
        print('\tEnter disconnect or press Ctrl+C if you want to disconnect.')
        try:
            auth = input('Enter authorization option: ')
            if auth == auth_opt['authorize'] or auth == auth_opt['register']:
                username = input('\tUsername: ')
                password = get_pass(fernet)
                if auth == auth_opt['authorize']:
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
                    elif ans == 'history':
                        if auth == '1' or auth == '2':
                            print('Server message:', request(conn, 'history', username))
                        else:
                            print('History is available only for authorized users')
                    else:
                        ans = ans.split(' ')
                        method, text = ans[0], " ".join(ans[1:])[1:-1]
                        print('Server message:', request(conn, method, text))
                except ConnectionResetError:
                    disconnect(conn)
                    print('\nServer disconnected!')
                    break
                except KeyboardInterrupt:
                    disconnect(conn)
                    print('\nDisconnected!')
                    break
        except KeyboardInterrupt:
            disconnect(conn)
            print('\nDisconnected!')
    except ConnectionRefusedError:
        print('Server is unreachable!')