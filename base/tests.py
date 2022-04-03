from django.test import SimpleTestCase
from .utils import MatchCV
from admin.settings import MEDIA_ROOT
import os
import asyncio

pdf_file = os.path.join(MEDIA_ROOT,"resume.pdf")
image_file = os.path.join(MEDIA_ROOT, "image.jfif")
print(image_file)
print(MEDIA_ROOT)

class TestClass(SimpleTestCase):

    def test_home_view(self):
        home_response = self.client.get("/")
        info_response = self.client.get("/info")

        self.assertEqual(home_response.status_code,
                         200) and self.assertEqual(info_response, 200)

    def test_subject(self):

      #invalid subject
      match = MatchCV(cv=None, subject="not a real job123")
      with self.assertRaises(AttributeError):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(match.IndeedScrape())

      #invalid resume
      with open("C:/Users/gabbe/Downloads/cv-match/media/image.jfif", 'rb') as file:
        match = MatchCV(cv=file, subject=None)
        self.assertIsNone(match.ReadCV())

      # valid resume and subject
      with open("C:/Users/gabbe/Downloads/cv-match/media/Resume.pdf", 'rb') as file:
        match = MatchCV(cv=file, subject="machine learning")
        self.assertIsNotNone(match.calculate_cosine_similarity)        


