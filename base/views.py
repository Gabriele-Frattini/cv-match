from django.shortcuts import redirect, render
from .forms import uploadFileForm
from .utils import MatchCV, delete_file
import shutil
from django.http import HttpResponse
from pymongo import MongoClient

from admin.settings import MONGODB_URL

# connect to db
client = MongoClient(MONGODB_URL)
db = client.cv




# Create your views here.

def infoView(request):
    return render(request, 'info.html', {})


def formView(request):

    result = ""
    if request.method == "POST":
        upload_form = uploadFileForm(request.POST, request.FILES)
        if upload_form.is_valid():

            file = upload_form.save()
            file = request.FILES["file_name"]
            if file.name.endswith("pdf"):
                    file_path = "media/files/"+str(file)
                    subject = upload_form.cleaned_data["subject"]
                    match = MatchCV(cv_path=file_path, subject=subject)
                    delete_file(file_path)
                    qurey_dict = db["cv_collection"].find_one({'subject':subject})

                    if qurey_dict is not None:
                        subject_corpus = qurey_dict["subject_corpus"]

                        score = match.calculate_cosine_similarity(_new_subject_corpus=subject_corpus)
                        db["cv_collection"].update_one({'subject':subject},
                                                         {"$push": {"result":score}
                                                         })
                        result = f"Likheten var {score}%"

                    elif qurey_dict is None:
                        try:
                            score = match.calculate_cosine_similarity()
                        except AttributeError:
                            context = {'invalid_subject': (f"{subject} har inga jobbinlägg")}
                            return render(request, "home.html",context)

                        result_db = {
                            'subject':subject,
                            'result':[score,],
                            'subject_corpus':match.new_subject_corpus
                            }
                        db["cv_collection"].insert_one(result_db)
                        result = f"Likheten var {score}%"


            else:
                context= {'invalid_file': (f"{file.name} är inte giltig.")}
                return render(request, "home.html",context)



    else:
        upload_form = uploadFileForm()

    context = {"upload_form": upload_form,
               "result": result}
    return render(request, "home.html", context)
