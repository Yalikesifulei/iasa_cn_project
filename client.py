import socket
import sys
import json

def request(req, host='127.0.0.1', port=8888):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(json.dumps(req).encode())
        data = s.recv(4096)
    return data.decode()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        text = sys.argv[1]
        method = sys.argv[2]
    elif len(sys.argv) == 2:
        method = 'predict'
        text = sys.argv[1]
    else:
        method = 'predict_proba'
        text = """What makes this film stand out, aside from its superb effects, 
        humor and script, is the contrast between Tommy Lee Jones and Will Smith. 
        While Jones is the emotionless, smarter and wiser one out of the two, 
        Smith is the younger and more enthusiastic. These 'Men In Black' are on a 
        mission to save Earth from a really, really nasty bug infestation. 
        This is one Sci-Fi film that shouldn't be missed."""
    print('server message:', request({'method': method, 'text': text}))