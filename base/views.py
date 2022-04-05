from django.shortcuts import redirect, render
from .forms import uploadFileForm
from pymongo import MongoClient
from admin.settings import MONGODB_URL
from .tasks import async_scrape
from .utils import MatchCV
import io
import pickle
import time
from celery.result import AsyncResult
from django.urls import reverse

# connect to db
client = MongoClient(MONGODB_URL)
db = client.cv


# Create your views here.

def infoView(request):
    return render(request, 'info.html', {})


def formView(request):
    score = 0
    subject_scrape = ""
    result = ""
    if request.method == "POST":
        upload_form = uploadFileForm(request.POST, request.FILES)
        if upload_form.is_valid():
            file = request.FILES["file_name"]
            if file.name.endswith("pdf"):
                subject = upload_form.cleaned_data["subject"]
                match = MatchCV(cv=file, subject=subject)
                qurey_dict = db["something"].find_one({'subject': subject})

                if qurey_dict is not None:
                    subject_corpus = qurey_dict["corpus"]

                    score = match.calculate_cosine_similarity(
                        _subject_corpus=subject_corpus)

                    db["cv_collection"].update_one({'subject': subject},
                                                   {"$push": {"result": score}
                                                    })
                    result = f"Likheten var {score}%"

                elif qurey_dict is None:
                    new_data = async_scrape(subject=subject)
                    if new_data["corpus"] is not None:
                        score = match.calculate_cosine_similarity(
                            new_data["corpus"])
                        result = f"Likheten var {score}%"
                    elif new_data["corpus"] is None:

                        context = {'invalid_file': (
                            f"{subject} har inga jobbannonser.")}
                        return render(request, "home.html", context)

            else:
                context = {'invalid_file': (f"{file.name} är inte giltig.")}
                return render(request, "home.html", context)

    else:
        upload_form = uploadFileForm()

    context = {"upload_form": upload_form,
               "result": result, 'subject_scrape': subject_scrape, 'score':score}
    return render(request, "home.html", context)
