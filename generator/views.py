from django.shortcuts import render_to_response
from django.http import HttpResponse



#ON SERVER
#from jsb.generator.models import generate_file #models

#LOCAL
from generator.models import generate_file #models
from generator.models import get_option_value
from generator.models import WojSet
from generator.models import PowSet
from generator.models import GmSet
from generator.models import MiejSet
from generator.models import AdresSet



def genout(request):
    return render_to_response('output.html', {'link': generate_file(request.GET)})

def step1(request):
    return render_to_response('genform.html', {'step': 1, 'woj': WojSet.choose_woj(),
                                               'req': get_option_value(request.GET, 1)})

def step2(request):
    return render_to_response('genform.html', {'step': 2, 'pow': PowSet.choose_pow(get_option_value(request.GET, 2)),
                                               'req': get_option_value(request.GET, 2)})

def step3(request):
    return render_to_response('genform.html', {'step': 3, 'gm': GmSet.choose_gm(get_option_value(request.GET, 3)),
                                               'req': get_option_value(request.GET, 3)})

def step4(request):
    return render_to_response('genform.html', {'step': 4, 'miej': MiejSet.choose_miej(get_option_value(request.GET, 4)),
                                               'req': get_option_value(request.GET, 4)})

def step5(request):
    return render_to_response('genform.html', {'step': 5, 'req': get_option_value(request.GET, 5)})