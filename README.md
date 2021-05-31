# iasa_cn_project
 Project for Computer Networks discipline

A TCP server that gets three types of requests from client: predict sentiment of given text, predict it with probability, and find similar film review in [IMDB dataset](https://ai.stanford.edu/~amaas/data/sentiment/). Server supports multi-user connection using threading. Users can authorize or use server anonymously. Authorized users can view their requests history. 

Usage: run `server.py` somewhere:
```
PS C:\Users\Yalikesi\Documents\server> python server.py
loading model files...
[start] listening at ('127.0.0.1', 8888)
```
Then one can send requests using `client.py`:
```
PS C:\Users\Yalikesi\Documents\server> python client.py
Connected to 127.0.0.1:8888
Server message: Welcome! Enter 1 to authorize, 2 to register, 0 to use anonymously.
        Available requests are:
            - predict 'text' to predict text sentiment (positive/negative)
            - predict_proba 'text' to predict sentiment with probability
            - similar 'text' to show similar review from IMDB reviews dataset
            - history to show history of your requests (if authorized)
        Enter disconnect or press Ctrl+C if you want to disconnect.
Enter authorization option: 1
        Username: admin
        Password:
You can make requests now, admin!
Request: predict_proba 'Nice movie!'
Server message: positive 93.900% | negative 6.100%
```

All requests are logged while server is running. If `server.py` is called with second argument
```
PS C:\Users\Yalikesi\Documents\server> python server.py filename
```
everything will be logged to `filename` in the same folder as server: [example](https://github.com/Yalikesifulei/iasa_cn_project/blob/main/test_log.txt).
