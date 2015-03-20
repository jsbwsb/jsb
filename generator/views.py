from django.shortcuts import render, render_to_response
from django.http import HttpResponse
#from generator.models import AddressData
# Create your views here.
from generator.models import generate_file #models


def genout(request):
    return render_to_response('output.html', {'link': generate_file(request)})

def showform(request):
    return render_to_response('genform.html')