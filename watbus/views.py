from django.core import serializers
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from collections import defaultdict, OrderedDict
import datetime
import time
from watbus.models import StopTimes, Stops
import re

def __getWeekdayString(weekday):

    return {

            0 : 'monday',
            1 : 'tuesday',
            2 : 'wednesday',
            3 : 'thursday',
            4 : 'friday',
            5 : 'saturday',
            6 : 'sunday',

            }.get(weekday, 'monday')


def search(request):

    if 'query' in request.GET and request.GET['query']:
        query = request.GET['query'].strip()
        if not re.match(r'\d+', query):
            return HttpResponseBadRequest("Stop id must only contain numbers")

        #redirect to terminal if stop is part of terminal.
        stop = Stops.objects.get(stop_id=query)
        if stop.parent_station:
            return redirect(reverse('watbus.views.popular_stop', kwargs={'stop_id':stop.parent_station}) + '#stop_' + str(stop.stop_id))
        else:
            return redirect('watbus.views.browse_stops', stop_id=query)
    else:
        return HttpResponseBadRequest("No query entered")

def stopjson(request):
    bus_stop_list = Stops.objects.all();
    bus_json = serializers.serialize("json", bus_stop_list);
    if not bus_stop_list:
        raise Http404
    return HttpResponse(bus_json, content_type="application/json")

def map(request):
    return render(request, 'watbus/map.html')

#Display generic landing page.
def browse(request):
    return render(request, 'watbus/browse.html')

#Returns a dictionary of the next buses coming to a stop orderd by arrival time.
def next_buses_by_time(time, stop_id):

    curr_day = datetime.date.today()
    day_selector_keyword = 'trip_id__service_id__' + __getWeekdayString(datetime.datetime.today().weekday())

    #If invalid stop is returned.
    next_bus_list = StopTimes.objects.filter(stop_id=stop_id)
    if not next_bus_list:
        raise Http404

    #Best solution right now to get past buses
    time = time - datetime.timedelta(hours=2)

    #Will return buses on ALL routes coming to a given stop, ordered by arrival time.
    next_bus_list = next_bus_list.select_related(
            'trip_id'
    ).filter(
            arrival_time__gte=time
    ).filter(
            trip_id__service_id__start_date__lte=curr_day
    ).filter(
            trip_id__service_id__end_date__gte=curr_day
    ).filter(
            **{ day_selector_keyword : 1 }
    ).order_by(
            'trip_id__trip_headsign', 'arrival_time'
    )

    return list(next_bus_list)

def browse_stops(request, stop_id):

    curr_time = datetime.datetime.now()
    next_bus_list = next_buses_by_time(curr_time, stop_id)

    context = { 'next_buses_by_time' : next_bus_list, 'stop_id' : stop_id }
    return render(request, 'watbus/browse_stops.html', context)

def browse_trips(request, trip_id):

    curr_time = datetime.datetime.now();
    curr_day = datetime.date.today();
    day_selector_keyword = 'trip_id__service_id__' + __getWeekdayString(datetime.datetime.today().weekday())

    next_bus_list = StopTimes.objects.filter(trip_id=trip_id)
    if not next_bus_list:
        raise Http404

    next_bus_list = next_bus_list.select_related(
            'trip_id'
    ).filter(
            arrival_time__gte=curr_time
    ).filter(
            trip_id__service_id__start_date__lte=curr_day
    ).filter(
            trip_id__service_id__end_date__gte=curr_day
    ).filter(
            **{ day_selector_keyword : 1}
    ).order_by(
            'stop_sequence'
    )
    context = {'next_buses_by_stop' : next_bus_list, 'trip_id' : trip_id }
    return render(request, 'watbus/browse_trips.html', context)

def popular(request):

    freqstops = Stops.objects.filter(location_type=1).order_by('parent_station_type')
    return render(request, 'watbus/popular.html', { 'freqstops' : freqstops })

def popular_stop(request, stop_id):

    #Get all stops that have the given terminal ID
    freqstops = Stops.objects.filter(parent_station=stop_id)
    if not freqstops:
        raise Http404

    stop_dict = {}
    for stop in freqstops:
        stopid = stop.stop_id
        stop_dict[stopid] = next_buses_by_time(datetime.datetime.now(), stopid)

    return render(request, 'watbus/popular_stop.html', { 'stop_name' : freqstops[0].stop_name , 'stops' : stop_dict.iteritems() })

def about(request):
    return render(request, 'watbus/about.html')

def sitemap(request):
    pois = Stops.objects.filter(location_type=1).values_list('stop_id', 'stop_name')
    if not pois:
        raise Http404

    stops = Stops.objects.filter(location_type=0).values_list('stop_id', 'stop_name')
    if not stops:
        raise Http404

    return render(request, 'watbus/sitemap.html', { 'pois' : pois, 'stops' : stops })

def coming(request):
    return render(request, 'watbus/comingsoon.html')

