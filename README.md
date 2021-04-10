# iasa_cn_project
 Project for Computer Networks discipline

A TCP server that gets three types of requests from client: predict sentiment of given text, predict it with probability, and find similar film review in [IMDB dataset](https://ai.stanford.edu/~amaas/data/sentiment/).

Usage: run `server.py` somewhere:
```
PS C:\Users\Yalikesi\Documents\server> python server.py
loading model files...
[start] listening at ('127.0.0.1', 8888)
```
Then one can send requests using `client.py`:
```
PS C:\Users\Yalikesi\Documents\kursach\server> python client.py 'Awesome movie' predict
server message: positive
PS C:\Users\Yalikesi\Documents\kursach\server> python client.py 'Awesome movie' predict_proba
server message: positive 99.205% | negative 0.795%
PS C:\Users\Yalikesi\Documents\kursach\server> python client.py 'Awesome movie' similar
server message: I think that Never Been Kissed was a totally awesome movie. The casting was really good and they acted very well. I really like Drew Barrymore and of course for me it was excellent. I was scared at first because it said that it wasn't coming out on video. Boy, am I happy that it is because it's a beyond cool movie. Go see it if you already haven't!
PS C:\Users\Yalikesi\Documents\kursach\server> python client.py 'Awesome movie' bad_method
server message: error: unknown method
```

All requests are logged while server is running:
```
Sun Apr 11 01:01:02 2021  | connected by ('127.0.0.1', 64359)
client message:  {"method": "predict", "text": "Awesome movie"}
server message:  positive

Sun Apr 11 01:01:18 2021  | connected by ('127.0.0.1', 64366)
client message:  {"method": "predict_proba", "text": "Awesome movie"}
server message:  positive 99.205% | negative 0.795%

Sun Apr 11 01:01:29 2021  | connected by ('127.0.0.1', 64367)
client message:  {"method": "similar", "text": "Awesome movie"}
server message:  I think that Never Been Kissed was a totally awesome movie. The casting was really good and they acted very well. I really like Drew Barrymore and of course for me it was excellent. I was scared at first because it said that it wasn't coming out on video. Boy, am I happy that it is because it's a beyond cool movie. Go see it if you already haven't!

Sun Apr 11 01:02:50 2021  | connected by ('127.0.0.1', 64368)
client message:  {"method": "bad_method", "text": "Awesome movie"}
[error] unknown method: bad_method
server message:  error: unknown method
```
