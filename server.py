import socket
import sys
import contextlib
import json
from predictor import predict, predict_proba, similar
from joblib import load
import pandas as pd
from scipy.sparse import load_npz
from datetime import datetime
import os
import pickle
from _thread import start_new_thread
import base64
from cryptography.fernet import Fernet

@contextlib.contextmanager
def smart_open(fname=None):
    fout = open(fname, 'a') if fname else sys.stdout
    try:
        yield fout
    finally:
        if fout is not sys.stdout:
            fout.close()

class Server:
    def __init__(self, model_path, host='127.0.0.1', port=8888, log_file=None):
        self.thread_count = 0
        self.welcome_message = '''Welcome! Enter 1 to authorize, 2 to register, 0 to use anonymously.
        Available requests are:
            - predict 'text' to predict text sentiment (positive/negative)
            - predict_proba 'text' to predict sentiment with probability
            - similar 'text' to show similar review from IMDB reviews dataset
            - history to show history of your requests (if authorized)
        Enter disconnect or press Ctrl+C if you want to disconnect.'''
        self.host = host
        self.port = port
        self.model_path = model_path
        if log_file:
            self.log_file = os.getcwd() + '\\' + log_file
        else:
            self.log_file = None
        self.users_path = os.getcwd() + '\\users.dat'
        if os.path.exists(self.users_path):
            try:
                with open(self.users_path, 'rb') as fin:
                    self.users = pickle.load(fin)
            except EOFError:
                self.users = {}
        else:
            self.users = {}
        self.current_users = []
        if self.log_file:
            print(f'logging into {self.log_file}')
            now = datetime.now()
            with smart_open(self.log_file) as fout:
                print(f'----- {now.strftime("%c")} -----', file=fout)
        with open(os.getcwd() + '\\key.dat', 'rb') as kf:
            key = kf.read()
        self.key = base64.b64decode(key)
        self.fernet = Fernet(self.key)
        with smart_open(self.log_file) as fout:
            print('[info]\tloading model files...', file=fout)
        tick = datetime.now()    
        self.tfidf = load(self.model_path + 'tfidf.joblib')
        self.model = load(self.model_path + 'model.joblib')
        self.encoded_words = load_npz(self.model_path + 'encoded_words.npz')
        self.reviews = pd.read_csv(self.model_path + 'reviews.csv', index_col='id')
        tock = datetime.now()
        with smart_open(self.log_file) as fout:
            print(f'\tdone in {(tock - tick).seconds}.{(tock - tick).microseconds} sec', file=fout)

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen()
        s.settimeout(0.1)
        with smart_open(self.log_file) as fout:
            print(f'[start]\tlistening at {s.getsockname()}\n', file=fout)
        try:
            while True:
                try:
                    conn, addr = s.accept()
                    now = datetime.now()
                    with smart_open(self.log_file) as fout:
                        print(f'{now.strftime("%c")} | connected by {addr}', file=fout)
                    start_new_thread(self.client_thread, (conn, addr))
                except socket.timeout:
                    pass
                except KeyboardInterrupt:
                    pass
        except KeyboardInterrupt:
            with smart_open(self.log_file) as fout:
                print('[end]\tserver closed with KeyboardInterrupt\n', file=fout)
            with open(self.users_path, 'wb') as fout:
                    pickle.dump(self.users, fout)
            s.close()
            
    def client_thread(self, conn, addr):
        while True:
            data = conn.recv(1024)
            if not data:
                with smart_open(self.log_file) as fout:
                    print(f'[info] {addr[1]} client disconnected\n', file=fout)
                break
            else:
                with smart_open(self.log_file) as fout:
                    print(f'[info] {addr[1]} client message:\t {data.decode()}', file=fout)
                response = self.handle_request(data)
                conn.sendall(response)
                with smart_open(self.log_file) as fout:
                    print(f'[info] {addr[1]} server message:\t {response.decode()}\n', file=fout)
        conn.close()

    def authorize(self, username, password):
        if username in self.users.keys():
            if self.fernet.decrypt(self.users[username]['password'].encode()) == self.fernet.decrypt(password.encode()):
                self.current_users.append(username)
                return b'ok'
            else:
                return b'Wrong password, try again'
        else:
            return b'User not found, try again'

    def register(self, username, password):
        if username not in self.users.keys():
            self.users[username] = {'password': password, 'history': []}
            with open(self.users_path, 'wb') as fout:
                    pickle.dump(self.users, fout)
            self.current_users.append(username)
            return b'ok'
        else:
            return b'User already exists'

    def handle_request(self, data):
        req = json.loads(data.decode())
        req_method, req_text = req['method'], req['text']
        if req_method == 'welcome':
            return self.welcome_message.encode()
        elif req_method == 'authorize':
            username, password = req['text'].split('; ')
            return self.authorize(username, password)
        elif req_method == 'register':
            username, password = req['text'].split('; ')
            return self.register(username, password)
        elif req_method == 'predict':
            res = predict(req_text, self.tfidf, self.model)
            return b'negative' if res == 0 else b'positive'
        elif req_method == 'predict_proba':
            res = predict_proba(req_text, self.tfidf, self.model)
            res = 100*res[0, 1]
            res_str = f'positive {res:.3f}% | negative {100-res:.3f}%'
            return res_str.encode()
        elif req_method == 'similar':
            res = similar(req_text, self.tfidf, self.encoded_words, self.reviews)
            return res.encode()
        else:
            with smart_open(self.log_file) as fout:
                print(f'[error]\tunknown method: {req_method}', file=fout)
            return b'Error: unknown method'


if __name__ == '__main__':
    path = sys.argv[0].split('\\')
    path = '\\'.join(path[:-1])
    model_path = path + '\\model_data\\' if len(path) > 0 else 'model_data\\'
    log_path = path + '\\' if len(path) > 0 else ''
    log_path = log_path + sys.argv[1] if len(sys.argv) > 1 else None
    
    server = Server(model_path=model_path, log_file=log_path)
    server.start()