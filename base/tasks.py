import asyncio
import aiohttp
from celery import shared_task
from .sync_scraper import IndeedScrape
from pymongo import MongoClient
from admin.settings import MONGODB_URL
from admin.celery import app
from .utils import MatchCV
client = MongoClient(MONGODB_URL)
db = client.cv



@app.task()
def async_scrape(subject):
  subject_corpus = IndeedScrape(subject)
  data = {
    'subject':subject,
    'corpus':subject_corpus,
    'result':[]
  }
  db["something"].insert_one(data)

  return "Done"




