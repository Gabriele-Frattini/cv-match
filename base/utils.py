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
import asyncio
import aiohttp


class MatchCV(object):
    cv = None
    subject = None
    new_subject_corpus = None

    def __init__(self, cv, subject, new_subject_corpus=None):
        self.cv = cv
        self.subject = subject
        self.new_subject_corpus = self.new_subject_corpus

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

    async def IndeedScrape(self, pages=1):

        subject = self.subject
        subject = subject.replace(" ", "+")

        for i in range(0, pages*10, 10):
            url = "https://se.indeed.com/jobb?q="+subject + \
                "&l=sverige"+"&lang=en&start="+str(i)
            htmldata = requests.get(url).text
            soup = BeautifulSoup(htmldata, 'html.parser')
            jobs_body = soup.find('div', {'class': 'mosaic-provider-jobcards'})
            all_requirements = ""

            async with aiohttp.ClientSession() as session:
                for a in jobs_body.select('a', href=True):
                    while len(all_requirements) < 6000:
                        if a["href"].startswith("/rc/clk?"):
                            link = "https://indeed.com"+a["href"]
                            async with session.get(link) as resp:
                                html_body = await resp.read()
                                job_soup = BeautifulSoup(
                                    html_body, "html.parser")
                                job_description = job_soup.find(
                                    'div', {'id': 'jobDescriptionText'})
                                if job_description:
                                    paragraphs = job_description.text.split(
                                        "\n")

                                    for sentence in str(paragraphs).split("."):
                                        if sentence != "" or "requirements" in sentence or "qualifications" in sentence or "skills" in sentence or "background" in sentence:
                                            all_requirements += sentence+" "

        preprocessed_subject = self.preprocess(all_requirements)
        self.new_subject_corpus = preprocessed_subject

        return preprocessed_subject

    def calculate_cosine_similarity(self, _new_subject_corpus=None):

        cv = self.ReadCV()

        if _new_subject_corpus is None:
            loop = asyncio.new_event_loop()
            subject = loop.run_until_complete(self.IndeedScrape())

        elif _new_subject_corpus is not None:
            subject = _new_subject_corpus

        tfidf_vectorizer = TfidfVectorizer()

        subject = subject[:len(subject)]
        corpus = [subject, cv]

        sparse_mtx = tfidf_vectorizer.fit_transform(corpus)
        cosine_sim = cosine_similarity(sparse_mtx, sparse_mtx)[0][1]
        cosine_sim = round(cosine_sim*100, 2)

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

