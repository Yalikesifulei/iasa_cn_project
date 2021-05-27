import socket
import json
import getpass

def connect(host='127.0.0.1', port=8888):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    welcome_request = {'method': 'welcome', 'text': ''}
    s.sendall(json.dumps(welcome_request).encode())
    welcome_message = s.recv(256)
    return s, host, port, welcome_message.decode()

def disconnect(conn):
    conn.close()

def request(conn, req):
    conn.sendall(json.dumps(req).encode())
    data = conn.recv(4096)
    return data.decode()

if __name__ == '__main__':
    method = 'predict_proba'
    text = """What makes this film stand out, aside from its superb effects, 
    humor and script, is the contrast between Tommy Lee Jones and Will Smith. 
    While Jones is the emotionless, smarter and wiser one out of the two, 
    Smith is the younger and more enthusiastic. These 'Men In Black' are on a 
    mission to save Earth from a really, really nasty bug infestation. 
    This is one Sci-Fi film that shouldn't be missed."""
    conn, host, port, welcome_message = connect()
    print(f'connected to {host}:{port}')
    print('server message:', welcome_message)
    while True:
        print('server message:', request(conn, {'method': method, 'text': text}))
        ans = input('\nDo you want to continue(y/n): ')
        if ans == 'y':
            continue
        else:
            break
    disconnect(conn)
    print('disconnected')