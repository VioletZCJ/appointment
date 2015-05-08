#coding=utf-8
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import localtime
from dateutil.relativedelta import relativedelta

# Create your models here.
# class Device(models.Model):
#     name = models.CharField('设备名称', max_length=100)
#     status = models.BooleanField('是否可用', default=True)
#     remarks = models.TextField('备注', null=True, blank=True)

#     class Meta:
#         verbose_name = '设备'
#         verbose_name_plural = '设备列表'

class HourRange(models.Model):
    start_hour = models.IntegerField()
    end_hour = models.IntegerField()

    class Meta:
        verbose_name = '每天时间段显示设置'
        verbose_name_plural = verbose_name

try:
    hour_range_check = HourRange.objects.all()
    if not hour_range_check:
        HourRange(start_hour=0, end_hour=24).save()
except:
    pass

class WeekdayRange(models.Model):
    monday = models.BooleanField('星期一', default=True)
    tuesday = models.BooleanField('星期二', default=True)
    wednesday = models.BooleanField('星期三', default=True)
    thursday = models.BooleanField('星期四', default=True)
    friday = models.BooleanField('星期五', default=True)
    saturday = models.BooleanField('星期六', default=True)
    sunday = models.BooleanField('星期日', default=True)

    class Meta:
        verbose_name = '每周显示设置'
        verbose_name_plural = verbose_name

try:
    week_range_check = WeekdayRange.objects.all()
    if not week_range_check:
        WeekdayRange().save()
except:
    pass

class OnceDisablePeriod(models.Model):
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    remarks = models.TextField('备注', null=True, blank=True)
    class Meta:
        verbose_name = '不可预约时段'
        verbose_name_plural = '不可预约时段列表（单次）'

class DailyDisablePeriod(models.Model):
    start_choices = ((i,str(i)+':00') for i in range(24))
    end_choices = ((i,str(i)+':00') for i in range(24))

    start_hour = models.IntegerField('开始时间', choices=start_choices)
    end_hour = models.IntegerField('结束时间', choices=end_choices)

    remarks = models.TextField('备注', null=True, blank=True)

    def get_length(self):
        if self.start_hour < self.end_hour:
            return (self.end_hour - self.start_hour) * 3600
        else:
            return (24 + self.end_hour - self.start_hour) * 3600

    def get_start_length(self):
        if self.start_hour < self.end_hour:
            return (self.end_hour - self.start_hour) * 3600
        else:
            return (24 - self.start_hour) * 3600

    def get_end_length(self):
        if self.start_hour < self.end_hour:
            return (self.end_hour - self.start_hour) * 3600
        else:
            return self.end_hour * 3600

    def get_start_date(self):
        now = datetime.datetime.now()
        start = now + relativedelta(hours=(self.start_hour - now.hour), minutes=(-1*now.minute))
        print start
        return start.strftime('%m/%d/%Y %H:%M')

    def get_end_date(self):
        now = datetime.datetime.now()
        return now.strftime('%m/%d/%Y 00:00')


    class Meta:
        verbose_name = '不可预约时段'
        verbose_name_plural = '不可预约时段列表（日循环）'

class WeeklyDisablePeriod(models.Model):
    weekly_choices = (
        (1, '星期一'),
        (2, '星期二'),
        (3, '星期三'),
        (4, '星期四'),
        (5, '星期五'),
        (6, '星期六'),
        (7, '星期日'),
    )
    start_choices = ((i,str(i)+':00') for i in range(24))
    end_choices = ((i,str(i)+':00') for i in range(24))

    start_weekday = models.IntegerField('周循环开始日', choices=weekly_choices, default=0)
    start_hour = models.IntegerField('开始时间', choices=start_choices)
    end_weekday = models.IntegerField('周循环结束日', choices=weekly_choices, default=0)
    end_hour = models.IntegerField('结束时间', choices=end_choices)

    remarks = models.TextField('备注', null=True, blank=True)

    def get_start_weekday(self):
        dic = dict(self.weekly_choices)
        if dic.has_key(self.start_weekday):
            return dic[self.start_weekday]
        return '--'

    def get_end_weekday(self):
        dic = dict(self.weekly_choices)
        if dic.has_key(self.end_weekday):
            return dic[self.end_weekday]
        return '--'

    def get_length(self):
        start = (self.start_weekday - 1) * 24 + self.start_hour
        end = (self.end_weekday - 1) * 24 + self.end_hour    
        if start < end:
            return (end - start) * 3600
        else:
            return (168 + end - start) * 3600

    def get_start_date(self):
        now = datetime.datetime.now()
        print now.hour
        start = now + relativedelta(days=(self.start_weekday - now.weekday() -1), hours=(self.start_hour - now.hour), minutes=(-1*now.minute))
        return start.strftime('%m/%d/%Y %H:%M')
    
    class Meta:
        verbose_name = '不可预约时段'
        verbose_name_plural = '不可预约时段列表（周循环）'

def in_disable_period(start_time, end_time):
    try:
        start_time = localtime(start_time).replace(tzinfo=None)
        end_time = localtime(end_time).replace(tzinfo=None)
    except:
        pass
    #once
    once_disable = OnceDisablePeriod.objects.all()
    for dis in once_disable:
        dis.start_time = localtime(dis.start_time).replace(tzinfo=None)
        dis.end_time = localtime(dis.end_time).replace(tzinfo=None)
        if (dis.start_time <= start_time and dis.end_time > start_time) or (dis.start_time >= start_time and dis.start_time < end_time):
            return True

    #daily
    daily_disable = DailyDisablePeriod.objects.all()
    start = start_time.hour
    end = end_time.hour
    if end_time.minute >0  or end_time.second > 0 or end_time.microsecond > 0:
        end += 1
    
    if start > end:
        period = ((start, 24), (0,end))
    else:
        period = ((start, end),)

    for dis in daily_disable:
        if dis.start_hour == dis.end_hour:  #无效设置
            continue

        if (end_time - start_time).days >= 1:  # 时长超过一天 一定有冲突
            return True

        if dis.start_hour > dis.end_hour:
            dis.period = ((dis.start_hour, 24), (0, dis.end_hour))
        else:
            dis.period = ((dis.start_hour, dis.end_hour),)

        for p in period:
            if p[0] == p[1]:
                continue
            for dp in dis.period:
                if dp[0] == dp[1]:
                    continue
                if p[0] <= dp[0] and p[1] > dp[0]:
                    return True
                if p[0] > dp[0] and p[0] < dp[1]:
                    return True

    #weekly
    daily_disable = WeeklyDisablePeriod.objects.all()
    start = start_time.weekday() * 24 + start_time.hour
    end = end_time.weekday() * 24 + end_time.hour

    if end_time.minute >0  or end_time.second > 0 or end_time.microsecond > 0:
        end += 1
    print start, end ,1111111111111
    if start > end:
        period = ((start, 168), (0,end))
    else:
        period = ((start, end),)

    for dis in daily_disable:
        dis.start_hour   = (dis.start_weekday - 1) * 24 + dis.start_hour
        dis.end_hour     = (dis.end_weekday - 1) * 24 + dis.end_hour
        
        if dis.start_hour == dis.end_hour:
            continue

        if (end_time - start_time).days >= 7:
            return True

        if dis.start_hour > dis.end_hour:
            dis.period = ((dis.start_hour, 168), (0, dis.end_hour))
        else:
            dis.period = ((dis.start_hour, dis.end_hour),)
        
        for p in period:
            if p[0] == p[1]:
                continue
            for dp in dis.period:
                if dp[0] == dp[1]:
                    continue
                if p[0] <= dp[0] and p[1] > dp[0]:
                    print p, dp
                    return True
                if p[0] > dp[0] and p[0] < dp[1]:
                    return True

    return False


class Appointment(models.Model):
    status_choices = (
        (0, '申请'),
        (1, '锁定'),
        )
    id = models.CharField('ID', max_length=100, primary_key=True)
    user = models.ForeignKey(User, verbose_name='申请用户')
    # device = models.ForeignKey(Device, verbose_name='设备')
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    status = models.IntegerField('状态', choices=status_choices, default=0)
    remarks = models.TextField('备注', null=True, blank=True)

    class Meta:
        verbose_name = '预约'
        verbose_name_plural = '预约列表'

    def save(self):
        if type(self.start_time) != datetime.datetime:
            self.start_time = datetime.datetime.strptime(str(self.start_time),'%Y-%m-%d %H:%M:%S')
        if type(self.end_time) != datetime.datetime:
            self.end_time = datetime.datetime.strptime(str(self.end_time),'%Y-%m-%d %H:%M:%S')
        if in_disable_period(self.start_time, self.end_time):
            return False, '包含不可申请时段'
        exists = self.__class__.objects.filter(
            (Q(start_time__lte=self.start_time) & Q(end_time__gt=self.start_time)) | 
            (Q(start_time__gte=self.start_time) & Q(start_time__lt=self.end_time))).exclude(pk=self.pk).exists()
        if exists:
            return False, '时间冲突'
        try:
            super(self.__class__, self).save()
        except:
            return False, '保存失败'
        return True, '保存成功'
