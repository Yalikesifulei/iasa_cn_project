import socket
import sys
import contextlib
import json
from predictor import predict, predict_proba, similar
from joblib import load
import pandas as pd
from scipy.sparse import load_npz
from datetime import datetime

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
        self.host = host
        self.port = port
        self.model_path = model_path
        self.log_file = log_file
        if self.log_file:
            print(f'logging into {self.log_file}')
            now = datetime.now()
            with smart_open(self.log_file) as fout:
                print(f'----- {now.strftime("%c")} -----', file=fout)
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
                    data = conn.recv(1024)
                    if not data:
                        with smart_open(self.log_file) as fout:
                            print('[error] client disconnected', file=fout)
                    else:
                        with smart_open(self.log_file) as fout:
                            print(f'client message:\t {data.decode()}', file=fout)
                        response = self.handle_request(data)
                        conn.sendall(response)
                        with smart_open(self.log_file) as fout:
                            print(f'server message:\t {response.decode()}\n', file=fout)
                        conn.close()
                except socket.timeout:
                    pass
                except KeyboardInterrupt:
                    pass
        except KeyboardInterrupt:
            with smart_open(self.log_file) as fout:
                print('[end]\tserver closed with KeyboardInterrupt\n', file=fout)
            
    def handle_request(self, data):
        req = json.loads(data.decode())
        if req['method'] == 'predict':
            res = predict(req['text'], self.tfidf, self.model)
            return b'negative' if res == 0 else b'positive'
        elif req['method'] == 'predict_proba':
            res = predict_proba(req['text'], self.tfidf, self.model)
            res = 100*res[0, 1]
            res_str = f'positive {res:.3f}% | negative {100-res:.3f}%'
            return res_str.encode()
        elif req['method'] == 'similar':
            res = similar(req['text'], self.tfidf, self.encoded_words, self.reviews)
            res_str = f'{res}'
            return res_str.encode()
        else:
            with smart_open(self.log_file) as fout:
                print(f'[error]\tunknown method: {req["method"]}', file=fout)
            return b'error: unknown method'


if __name__ == '__main__':
    path = sys.argv[0].split('\\')
    path = '\\'.join(path[:-1])
    model_path = path + '\\model_data\\' if len(path) > 0 else 'model_data\\'
    log_path = path + '\\' if len(path) > 0 else ''
    log_path = log_path + sys.argv[1] if len(sys.argv) > 1 else None
    
    server = Server(model_path=model_path, log_file=log_path)
    server.start()