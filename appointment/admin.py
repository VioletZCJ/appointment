from django.contrib import admin
from .models import Appointment, OnceDisablePeriod, DailyDisablePeriod, WeeklyDisablePeriod, HourRange, WeekdayRange

class AppointmentAdmin(admin.ModelAdmin):
    list_display_links = ('user',)
    list_display = ('user', 'start_time', 'end_time', 'status', 'remarks',) 
    list_filter = ['user', 'status']
    search_fields =  ['user', 'status', 'remarks']
    ordering = ('start_time',)
    
admin.site.register(Appointment, AppointmentAdmin)

class OnceDisablePeriodAdmin(admin.ModelAdmin):
    list_display_links = ('start_time', 'end_time', 'remarks')
    list_display = ('start_time', 'end_time', 'remarks') 
    search_fields =  ['start_time', 'end_time', 'remarks']
admin.site.register(OnceDisablePeriod, OnceDisablePeriodAdmin)

class DailyDisablePeriodAdmin(admin.ModelAdmin):
    list_display_links = ('start_hour', 'end_hour', 'remarks')
    list_display = ('start_hour', 'end_hour', 'remarks') 
    search_fields =  ['start_hour', 'end_hour', 'remarks']
admin.site.register(DailyDisablePeriod, DailyDisablePeriodAdmin)

class WeeklyDisablePeriodAdmin(admin.ModelAdmin):
    list_display_links = ('start_weekday', 'start_hour', 'end_weekday', 'end_hour', 'remarks')
    list_display = ('start_weekday', 'start_hour', 'end_weekday', 'end_hour', 'remarks') 
    search_fields =  ['start_weekday', 'start_hour', 'end_weekday', 'end_hour', 'remarks']
admin.site.register(WeeklyDisablePeriod, WeeklyDisablePeriodAdmin)


class HourRangeAdmin(admin.ModelAdmin):
    list_display_links = ('start_hour', 'end_hour')
    list_display = ('start_hour', 'end_hour')

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def get_actions(self, request):
        return []

admin.site.register(HourRange, HourRangeAdmin)

class WeekdayRangeAdmin(admin.ModelAdmin):
    list_display_links = ('monday','tuesday','wednesday','thursday','friday','saturday','sunday',)
    list_display = ('monday','tuesday','wednesday','thursday','friday','saturday','sunday',)

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def get_actions(self, request):
        return []

admin.site.register(WeekdayRange, WeekdayRangeAdmin)

# class DeviceAdmin(admin.ModelAdmin):
#     list_display_links = ('name',)
#     list_display = ('name', 'status', 'remarks') 
#     list_filter = ['status']
#     search_fields =  ['name', 'status', 'remarks']
    
# admin.site.register(Device, DeviceAdmin)