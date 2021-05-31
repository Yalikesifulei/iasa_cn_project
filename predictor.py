import re
import os
import pickle
import nltk
if os.path.join(os.getcwd(), 'model_data'):
    nltk.data.path.append(os.path.join(os.getcwd(), 'model_data'))
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity

with open(os.path.join(os.getcwd(), 'model_data', 'stopwords.dat'), 'rb') as fin:
    stopwords = pickle.load(fin)

def process(text):
    res = re.sub('<.*?>', ' ', text)
    res = re.sub('\W', ' ', res)
    res = re.sub('\s+[a-zA-Z]\s+', ' ', res)
    res = re.sub('\s+', ' ', res)
    word_tokens = word_tokenize(res)
    filtered_res = " ".join([w for w in word_tokens if w not in stopwords])
    return filtered_res

def predict(text, tfidf, model):
    transformed_text = tfidf.transform([process(text)])
    return model.predict(transformed_text)[0]

def predict_proba(text, tfidf, model):
    transformed_text = tfidf.transform([process(text)])
    return model.predict_proba(transformed_text)

def similar(text, tfidf, encoded_words, reviews):
    transformed_text = tfidf.transform([process(text)])
    cos_sim = cosine_similarity(encoded_words, transformed_text)
    top_id = (-cos_sim).argsort(axis=0)[:1].flatten()[0]
    res = reviews.loc[top_id]['review']
    return re.sub('<.*?>', ' ', res)