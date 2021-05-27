import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity

stop_words = set(stopwords.words('english'))

def process(text):
      res = re.sub('<.*?>', ' ', text)
      res = re.sub('\W', ' ', res)
      res = re.sub('\s+[a-zA-Z]\s+', ' ', res)
      res = re.sub('\s+', ' ', res)
      word_tokens = word_tokenize(res)
      filtered_res = " ".join([w for w in word_tokens if w not in stop_words])
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
      return reviews.loc[top_id]['review']