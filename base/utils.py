import PyPDF2
import requests
from bs4 import BeautifulSoup
from nltk.stem.porter import *
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import io
import os
import time

class MatchCV(object):
    cv = None
    subject = None
    score = None

    def __init__(self, cv, subject, score=None):
        self.cv = cv
        self.subject = subject
        self.score = score

    def preprocess(self, object):

        lowered = str.lower(object)
        string_punctuation = """\n\n \n\n\n!"-#$%&()--.*+,-/:;<=>?@[\\]^_`{|}~\t\n``'... """
        stop_words = set(stopwords.words("english"))
        word_tokens = word_tokenize(lowered)
        lemmatizer = WordNetLemmatizer()

        string_corpus = ""
        for w in word_tokens:
            if w not in stop_words:
                if w not in string_punctuation:
                    lemmatized = lemmatizer.lemmatize(w)
                    string_corpus += str(lemmatized+" ")

        return string_corpus

    def ReadCV(self):

        cv = self.cv
        if not cv.name.endswith("pdf"):
            return None

        pdfFileObj = io.BytesIO(cv.read())
        print(pdfFileObj)
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        pageObj = pdfReader.getPage(0)
        text = pageObj.extractText()
        text = text.replace("\n", "")

        return text

    def calculate_cosine_similarity(self, _subject_corpus):

        cv = self.ReadCV()
        subject = _subject_corpus

        if cv is not None and subject is not None:
            cv = self.preprocess(cv)
            subject = self.preprocess(subject)

            tfidf_vectorizer = TfidfVectorizer()
            subject = subject[:len(cv)]
            corpus = [subject, cv]

            sparse_mtx = tfidf_vectorizer.fit_transform(corpus)
            cosine_sim = cosine_similarity(sparse_mtx, sparse_mtx)[0][1]
            cosine_sim = round(cosine_sim*100, 2)
            self.score = cosine_sim

            return cosine_sim



# if __name__=="__main__":
#     loop = asyncio.get_event_loop()
#     match = MatchCV(cv_path="C:/Users/gabbe/Downloads/cv-match/media/Resume.pdf", subject="machine learning")
#     start = time.perf_counter()
#     data = loop.run_until_complete(match.IndeedScrape())
#     finish = time.perf_counter() - start
#     print(f"Parsed {len(data)} elements in {finish:.2f}s")

# Parsed 5286 elements in 9.39s with synchronous function
# Parsed 5286 elements in 7.02s with asynchronous function

