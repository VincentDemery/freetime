#!/usr/bin/python3

import os
from pathlib import Path
import datetime
import icalendar
import argparse
import yaml


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--nbweeks", default=0, type=int,
                    help="number of weeks to look forward (0 just looks for the present week)")
parser.add_argument("-d", "--duration", default=0, type=int,
                    help="minimal duration of the free slots in minutes")
args = parser.parse_args()


with open(os.path.join(os.path.dirname(__file__), 'freetime_conf.yaml'), 'r') as file:
    config = yaml.safe_load(file)

def upcoming_events(cals, verb=False):
    ue = []
    now = datetime.datetime.now()
    for cal in cals :
        for component in cal.walk():
            if component.name == "VEVENT":
                try :
                    dtend = component.get('dtend').dt
                    if isinstance(dtend, datetime.datetime) :
                        dtend = dtend.astimezone(None).replace(tzinfo=None)
                        dtstart = component.get('dtstart').dt.astimezone(None).replace(tzinfo=None)
                        if dtend > now:
                            if verb :
                                print(component.get('summary'), dtstart, dtend)
                            ue.append([dtstart, dtend, str(component.get('summary'))])
                except AttributeError :
                    if verb :
                        print('AttributeError for event ' + component.get('summary'))
    return ue

def read_time_slot(s):
    ss = s.split(' ')
    if len(ss) != 3:
        return

    d = int(ss[0])
    t1 = datetime.datetime.strptime(ss[1], '%H:%M').time()
    t2 = datetime.datetime.strptime(ss[2], '%H:%M').time()
    return [d, t1, t2]

def read_time_slots(time_slots):
    dts = [[] for k in range(5)]
    for l in time_slots :
        ts = read_time_slot(l)
        if ts :
            dts[ts[0]].append([ts[1], ts[2]])
    return dts

def next_weeks_slots(tsl, n=0):
    """
    Return the free slots in the following n weeks from a list of weekly time slots tsl.
    Returns a list of pairs of datetimes.
    """
    now = datetime.datetime.now()
    now_wd = now.weekday()
    nbdays = 5 - now_wd + 7*n
    slots = []
    for n in range(1, nbdays):
        day = datetime.datetime.now() + datetime.timedelta(days=n)
        wd = day.weekday()
        if wd < 5:
            if len(tsl[wd])>0:
                s1 = day.strftime("%a %d/%m")
                s2 = [ts[0].strftime("%H:%M") + '-' + ts[1].strftime("%H:%M") for ts in tsl[wd]]
                for ts in tsl[wd]:
                    t = day
                    slots.append([t.replace(hour=ti.hour, minute=ti.minute, second=0, microsecond=0) for ti in ts])
    return slots
                
                    

def difference_intervals(a, b, margin=0):
    b0 = b[0] - margin
    b1 = b[1] + margin

    if b1 <= a[0]:     # b ends before a starts
        return [a]
    elif b0 >= a[1]:   # b starts after a ends
        return [a]
    elif b0 <= a[0]:   # b starts before a
        if b1 >= a[1]:     # b ends after a
            return []
        else:
            return [[b[1], a[1]]]
    elif b1 >= a[1]:   # b ends after a
        return [[a[0], b0]]
    else:
        return [[a[0], b0], [b1, a[1]]]
    return []

def difference_list_of_intervals_interval(la, b, margin=0):
    la_diff_b = []
    for a in la:
        a_diff_b = difference_intervals(a, b, margin=margin)
        for i in a_diff_b:
            la_diff_b.append(i)
    return la_diff_b

def difference_lists_of_intervals(la, lb, margin=0):
    la_diff_lb = la
    for b in lb :
        la_diff_lb = difference_list_of_intervals_interval(la_diff_lb, b, margin=margin)
    return la_diff_lb

def filter_duration(li, duration=0):
    if duration == 0 :
        return li
    else :
        lif = []
        for i in li :
            if i[1] - i[0] >= datetime.timedelta(minutes=duration) :
                lif.append(i)
        return lif

def print_hour_short(t):
    s = t.strftime("%H:%M")
    if s[0] == '0':
        s = s[1:]
    if s[-3:] == ':00':
        s = s[:-3]
    return s

def print_intervals(li):
    date = datetime.datetime(2000, 1, 1).date()
    s = ''
    for i in li :
        t1, t2 = i[0], i[1]
        idate = t1.date()
        if idate > date :
            date = idate
            s += date.strftime("\n- %a %d/%m: ")
            s += print_hour_short(t1) + '-' + print_hour_short(t2)
        else :
            s += ', ' + print_hour_short(t1) + '-' + print_hour_short(t2)
    print(s[1:])
    return


def freetime(tsl, cals, n=0, duration=0, margin=0):
    nws = next_weeks_slots(tsl, n=n)
    ue = upcoming_events(cals)
    diff = difference_lists_of_intervals(nws, ue, margin=margin)
    diff = filter_duration(diff, duration)
    print_intervals(diff)
    return

tsl = read_time_slots(config['time_slots'])

calendars = []
for d in os.walk(os.path.expanduser(config['calendar_path'])) :
    if 'calendar.ics' in d[2] :
        ics_path = Path(os.path.join(d[0], 'calendar.ics'))
        calendars.append(icalendar.Calendar.from_ical(ics_path.read_bytes()))

freetime(tsl, calendars, n=args.nbweeks, duration=args.duration, 
              margin=datetime.timedelta(minutes=float(config['margin'])))
