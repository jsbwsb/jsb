from django.shortcuts import render, render_to_response
from django.http import HttpResponse
#from generator.models import AddressData
# Create your views here.


def genout(request):
    return render_to_response('output.html', {'link': "Test"})

def showform(request):
    return render_to_response('genform.html')