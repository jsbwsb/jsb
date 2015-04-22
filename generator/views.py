from django.shortcuts import render_to_response
from django.http import HttpResponse
#from generator.models import AddressData


#ON SERVER
#from jsb.generator.models import generate_file #models

#LOCAL
from generator.models import generate_file #models
from generator.models import get_option_value
from generator.models import AdresySet


def genout(request):
    return render_to_response('output.html', {'link': generate_file(request.GET)})

def step1(request):
    return render_to_response('genform.html', {'step': 1, 'woj': AdresySet.choose_woj(),
                                               'req': get_option_value(request.GET, 1)})

def step2(request):
    return render_to_response('genform.html', {'step': 2, 'pow': AdresySet.choose_pow(get_option_value(request.GET, 2)),
                                               'req': get_option_value(request.GET, 2)})

def step3(request):
    return render_to_response('genform.html', {'step': 3, 'gm': AdresySet.choose_gm(get_option_value(request.GET, 3)),
                                               'req': get_option_value(request.GET, 3)})