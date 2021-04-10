import socket
import sys
import json
from predictor import predict, predict_proba, similar
from joblib import load
import pandas as pd
from scipy.sparse import load_npz
from datetime import datetime

class Server:
    def __init__(self, tfidf, model, encoded_words, reviews, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.tfidf = tfidf
        self.model = model
        self.encoded_words = encoded_words
        self.reviews = reviews

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen()
        s.settimeout(0.1)
        print(f'[start] listening at {s.getsockname()}\n')
        try:
            while True:
                try:
                    conn, addr = s.accept()
                    now = datetime.now()
                    print(f'{now.strftime("%c")}  | connected by {addr}')
                    data = conn.recv(1024)
                    if not data:
                        print('[error] client disconnected')
                    else:
                        print(f'client message:\t {data.decode()}')
                        response = self.handle_request(data)
                        conn.sendall(response)
                        print(f'server message:\t {response.decode()}\n')
                        conn.close()
                except socket.timeout:
                    pass
                except KeyboardInterrupt:
                    pass
        except KeyboardInterrupt:
            print('[end] server closed with KeyboardInterrupt')
            
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
            print(f'[error] unknown method: {req["method"]}')
            return b'error: unknown method'


if __name__ == '__main__':
    print('loading model files...')
    path = sys.argv[0].split('\\')
    path = '\\'.join(path[:-1])
    path = path + '\\' if len(path) > 0 else ''
    tfidf = load(path+'tfidf.joblib')
    model = load(path+'model.joblib')
    encoded_words = load_npz(path+'encoded_words.npz')
    reviews = pd.read_csv(path+'reviews.csv', index_col='id')

    server = Server(tfidf, model, encoded_words, reviews)
    server.start()