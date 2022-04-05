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
                    async_scrape.delay(subject=subject)
                    reverse('info')
                    # a = async_scrape.AsyncResult(v)
                    # print(a.get())
                    # async_scrape.apply_sync((subject), link=db["something"].find_one({'subject': subject}))
                    # print(db["something"].find_one({'subject': subject}))
                    # print(res)
                    # print(res.get())
                    # qurey_dict = db["something"].find_one({'subject': subject})
                    # print(qurey_dict)


                    # if qurey_dict is None:
                    #     context = {'invalid_file': (f"{file.name} är inte giltig.")}
                    #     return render(request, "home.html", context)

                    # else:
                    #     subject_corpus = qurey_dict["corpus"]

                    #     score = match.calculate_cosine_similarity(
                    #         _subject_corpus=subject_corpus)
                    #     db["cv_collection"].update_one({'subject': subject},
                    #                                 {"$push": {"result": score}
                    #                                     })

                    #     result = f"Likheten var {score}%"
                    
            else:
                context = {'invalid_file': (f"{file.name} är inte giltig.")}
                return render(request, "home.html", context)

    else:
        upload_form = uploadFileForm()

    context = {"upload_form": upload_form,
               "result": result, 'subject_scrape': subject_scrape}
    return render(request, "home.html", context)
