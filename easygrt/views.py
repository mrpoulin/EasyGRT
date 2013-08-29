from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse
from easygrt.models import Stops

def favourites(request):
    return render(request, 'easygrt/index.html')

def stopjson(request):
    bus_stop_list = Stops.objects.all();
    bus_json = serializers.serialize("json", bus_stop_list);
    if not bus_stop_list:
        raise Http404
    context = {'bus_stops': bus_stop_list, 'stop_id': 3700, 'bus_json': bus_json}
    return HttpResponse(bus_json, content_type="application/json")

def map(request):
    return render(request, 'easygrt/map.html')

def browse(request):
    return render(request, 'easygrt/browse.html')
