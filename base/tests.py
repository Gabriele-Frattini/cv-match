from django.test import SimpleTestCase
from .utils import MatchCV
from admin.settings import MEDIA_ROOT
import os

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

    def test_score(self):

      #invalid cv
      match = MatchCV(cv_path=image_file, subject="machine learning")
      with self.assertRaises(ValueError):
        match.ReadCV()

      #invalid subject
      match = MatchCV(cv_path=pdf_file, subject="not a real job123")
      with self.assertRaises(AttributeError):
        match.IndeedScrape()

      #valid form
      match = MatchCV(cv_path=pdf_file, subject="machine learning")
      score = match.calculate_cosine_similarity(subject_corpus=None)
      self.assertIsNot(score, None)


