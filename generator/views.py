from django.shortcuts import render_to_response
from django.http import HttpResponse
#from generator.models import AddressData


#ON SERVER
#from jsb.generator.models import generate_file #models

#LOCAL
from generator.models import generate_file #models


def genout(request):
    return render_to_response('output.html', {'link': generate_file(request.GET)})

def showform(request):
    return render_to_response('genform.html')