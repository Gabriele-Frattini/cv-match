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
import os


class MatchCV(object):
    cv = None
    subject = None
    new_subject_corpus = None

    def __init__(self, cv_path, subject, new_subject_corpus=None):
        self.cv_path = cv_path
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

        cv_path = self.cv_path

        if not cv_path.endswith("pdf"):
            raise ValueError

        pdfFileObj = open(cv_path, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        pageObj = pdfReader.getPage(0)
        text = pageObj.extractText()
        text = text.replace("\n", "")

        return text

    def IndeedScrape(self, pages=1):

        subject = self.subject

        subject = subject.replace(" ", "+")
        all_requirements = " "
        for i in range(0, pages*10, 10):
            url = "https://se.indeed.com/jobb?q="+subject + \
                "&l=sverige"+"&lang=en&start="+str(i)
            htmldata = requests.get(url).text
            soup = BeautifulSoup(htmldata, 'html.parser')

            jobs_body = soup.find('div', {'class': 'mosaic-provider-jobcards'})

            for a in jobs_body.select('a', href=True):
                if a is None:
                    raise AttributeError
                link = a["href"]

                if link.startswith("/rc/clk?"):
                    url = "https://indeed.com"+link

                    job_response = requests.get(url)
                    job_data = job_response.text
                    job_soup = BeautifulSoup(job_data, "html.parser")

                    job_description = job_soup.find(
                        'div', {'id': 'jobDescriptionText'})
                    job_description = job_description.text if job_description else "N/A"
                    paragraphs = job_description.split("\n")

                    for sentence in str(paragraphs).split("."):
                        if sentence != "" or "requirements" in sentence or "qualifications" in sentence or "skills" in sentence or "background" in sentence:
                            all_requirements += sentence+" "

        preprocessed_subject = self.preprocess(all_requirements)
        self.new_subject_corpus = preprocessed_subject

        return preprocessed_subject

    def calculate_cosine_similarity(self, _new_subject_corpus=None):

        cv = self.ReadCV()

        if _new_subject_corpus is None:
            subject = self.IndeedScrape()

        elif _new_subject_corpus is not None:
            subject = _new_subject_corpus

        tfidf_vectorizer = TfidfVectorizer()

        subject = subject[:len(subject)]
        corpus = [subject, cv]

        sparse_mtx = tfidf_vectorizer.fit_transform(corpus)
        cosine_sim = cosine_similarity(sparse_mtx, sparse_mtx)[0][1]
        cosine_sim = round(cosine_sim*100, 2)

        return cosine_sim


def delete_file(path):
    if os.path.isfile(path):
        os.remove(path)
