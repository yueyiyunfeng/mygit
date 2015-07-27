from django.contrib import admin

#from models import Course,Publisher,Author,Book,Person
from models import *
class CourseAdmin(admin.ModelAdmin):
	list_display = ('course_code','course_name')
	list_display_links = ('course_code','course_name')
class StudentAdmin(admin.ModelAdmin):
	list_display = ('user','name','major','institute')
	list_display_links = ('user','name')
class TeacherAdmin(admin.ModelAdmin):
	list_display = ('user','name')
	list_display_links = ('user','name')
class Stu_VMAdmin(admin.ModelAdmin):
	list_display = ('student','course','virtualmachine')
	list_display_links = ('student','virtualmachine')
class Tea_VMAdmin(admin.ModelAdmin):
	list_display = ('teacher','course','virtualmachine')
	list_display_links = ('teacher','virtualmachine')
class LogDetailAdmin(admin.ModelAdmin):
	list_display = ('manager','detail')
class ApplyClassAdmin(admin.ModelAdmin):
	list_display = ('teacher','course_code','description')
	list_display_links = ('teacher','course_code')
admin.site.register(Student,StudentAdmin)
admin.site.register(Teacher,TeacherAdmin)
admin.site.register(Manager)
admin.site.register(Course,CourseAdmin)
admin.site.register(VirtualMachine)
admin.site.register(Stu_VM,Stu_VMAdmin)
admin.site.register(Tea_VM,Tea_VMAdmin)
admin.site.register(ApplyClass,ApplyClassAdmin)
admin.site.register(Message)
admin.site.register(LogDetail,LogDetailAdmin)
