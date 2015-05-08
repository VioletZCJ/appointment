#coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from datetime import datetime
from dateutil.relativedelta import relativedelta

from utils import render_to_response, render_to_response_json

from .models import  Appointment, OnceDisablePeriod, DailyDisablePeriod, WeeklyDisablePeriod, HourRange, WeekdayRange
from django.utils.timezone import localtime

@login_required
def home(request):
    dicts = {}
    dicts['appointments'] = get_appointments(request)
    dicts['oncedisable'] = OnceDisablePeriod.objects.all()
    dicts['dailydisable'] = DailyDisablePeriod.objects.all()
    dicts['weeklydisable'] = WeeklyDisablePeriod.objects.all()
    dicts['hourrange'] = HourRange.objects.all()[0]
    dicts['weekdayrange'] = WeekdayRange.objects.all()[0]
    return render_to_response(request, 'home.html', dicts)

@login_required
def add(request):
    id = request.POST.get('id', None)
    start_time = request.POST.get('start_date', None)
    end_time = request.POST.get('end_date', None)
    remarks = request.POST.get('remarks')
    if not id or not start_time or not end_time:
        return render_to_response_json({'res':False})

    ap = Appointment()
    ap.id = id
    ap.user = request.user
    ap.start_time = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
    ap.end_time = datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S')
    ap.status = 0
    ap.remarks = remarks
    now = datetime.now()
    if ap.start_time < now or ap.start_time.strftime('%Y-%m-%d') == now.strftime('%Y-%m-%d'):
        return render_to_response_json({'res':False, 'msg': '请至少提前一天提交预约！'})
    res, msg = ap.save()
    return render_to_response_json({'res':res, 'msg': msg})

@login_required
def update(request):
    id = request.POST.get('id', None)
    start_time = request.POST.get('start_date', None)
    end_time = request.POST.get('end_date', None)
    remarks = request.POST.get('remarks')
    if not id or not start_time or not end_time:
        return render_to_response_json({'res':False})

    try:
        obj = Appointment.objects.get(pk=id)
    except:
        return render_to_response_json({'res':False, 'msg':'参数有误'})

    if not request.user.is_staff and obj.user != request.user:
        data = {'res':False, 'msg': '您没有权限修改该记录'}
        return render_to_response_json(data)

    if obj.status == 1:
        return render_to_response_json({'res':False, 'msg':'管理员已锁定的预约不能修改'})

    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    now = datetime.now()
    if localtime(obj.start_time).strftime('%Y-%m-%d') == now.strftime('%Y-%m-%d') or start_time.strftime('%Y-%m-%d') == now.strftime('%Y-%m-%d'):
        return render_to_response_json({'res':False, 'msg':'当天不能再更改'})
    if localtime(obj.start_time).replace(tzinfo=None) < now or start_time < now:
        return render_to_response_json({'res':False, 'msg':'历史记录不可更改'})

    obj.start_time = start_time
    obj.end_time = end_time
    obj.remarks = remarks
    res, msg = obj.save()
    return render_to_response_json({'res':res, 'msg': msg})

@login_required
def delete(request):
    id = request.POST.get('id')
    obj = Appointment.objects.filter(pk=id)
    if not id or not obj:
        return render_to_response_json({'res':-1})

    obj = obj[0]
    if not request.user.is_staff and obj.user != request.user:
        return render_to_response_json({'res':False, 'msg':'您没有权限删除该记录'})

    if obj.status == 1:
        return render_to_response_json({'res':False, 'msg':'管理员已锁定的预约不能删除'})

    now = datetime.now()
    if localtime(obj.start_time).strftime('%Y-%m-%d') == now.strftime('%Y-%m-%d'):
        return render_to_response_json({'res':False, 'msg':'当天不能再删除'})
    if localtime(obj.start_time).replace(tzinfo=None) < now:
        return render_to_response_json({'res':False, 'msg':'历史记录不可删除'})

    try:
        obj.delete()
        return render_to_response_json({'res':True, 'msg':'删除成功'})
    except:
        return render_to_response_json({'res':False, 'msg':'删除失败'}) 

def get_appointments(request):
    now = datetime.now()
    year = int(now.strftime('%Y'))
    month = int(now.strftime('%m'))
    month_start = datetime(year, month, 1)
    month_end = month_start + relativedelta(months = 1) 
    appointments = Appointment.objects.filter(start_time__gte= now + relativedelta(months=-3))#filter(end_time__gt = month_start, start_time__lt = month_end).order_by('start_time')
    res = []
    for a in appointments:
        if request.user.is_staff or a.user == request.user:
            a.readonly = False
        else:
            a.readonly = True       #其他用户的  
            res.append(a)
            continue
        if localtime(a.start_time).replace(tzinfo=None) < now:  #历史记录
            a.readonly = True
        elif localtime(a.start_time).strftime('%Y-%m-%d') == now.strftime('%Y-%m-%d'):  #当天的
            a.readonly = True
        res.append(a)
    return res
