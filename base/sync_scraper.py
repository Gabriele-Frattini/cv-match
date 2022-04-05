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

def IndeedScrape(subject):

    subject = subject.replace(" ", "+")
    all_requirements = " "
    url = "https://se.indeed.com/jobb?q="+subject + \
        "&l=sverige"+"&lang=en&start=10"
    htmldata = requests.get(url).text
    soup = BeautifulSoup(htmldata, 'html.parser')

    jobs_body = soup.find('div', {'class': 'mosaic-provider-jobcards'})
    if jobs_body is None:
        return None

    else:
        for a in jobs_body.select('a', href=True):
            while len(all_requirements) < 4000:
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

        return all_requirements
