#encoding:utf-8
from django.shortcuts import render_to_response
from startvm.models import *
from django.http import HttpResponse
import sys;
#sys.path.append("/var/www/UIBE_VM1/script/UIBE_script_2014_12_22/UIBE_script_2014_12_22/")
import XenAPI
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User


from virtualmachine import *
from add_xml import *
from generate_vm import *
import delete_vm
import create_one 
import vm_status
import logging
log=logging.getLogger("django")
import course
import teacher

@login_required
def top(request):
	return render_to_response("chakanxuesheng.html")
@login_required
def loglist(request):
        user = request.user
        username=user.username
        if not checkUser(user) == 'manager':
                return HttpResponse ("权限不足，禁止访问")
        loglist = LogDetail.objects.order_by('-id')
       # return HttpResponse(loglist[0].manager.user.username)
        return render_to_response("loglist.html",
                                    {"username":username,
                                     "loglist":loglist,
                                     "role":'admin'
                                    },
                                    context_instance=RequestContext(request) )
        return HttpResponse("hell")
def checkUser(user):
    if hasattr(user,"manager"):
        return 'manager'
    elif hasattr(user,"teacher"):
        return 'teacher'
    elif hasattr(user,"student"):
        return 'student'
    else:
        return 'unknow'
@login_required
def subMsg(request):
    user = request.user
    username=user.username
    if not checkUser(user) == 'manager':
        return HttpResponse("权限不足，禁止访问")
    return render_to_response("add_msg.html",
                            {"username":username,
                             "role":'admin'
                            },
                            context_instance=RequestContext(request))  	
@login_required
def allMsg(request):
    user = request.user
    username = user.username
    role = checkUser(user)
    if role == "manager":
        role = 'admin'
#倒序排列，将最新的公告显示在上方
    msgList = Message.objects.order_by('-id')
    return render_to_response("all_msg.html",
                              {"username":username,
                               "role":role,
                               "msgList":msgList},
                               context_instance=RequestContext(request))

@login_required
def addMsg(request):
    username = request.user.username
    user = request.user
    if not hasattr(user,"manager"):
        return HttpResponse("禁止访问，权限不足")
    m_title = request.POST["m_title"]
    m_body  = request.POST["m_body"] 
    flag  = request.POST["flag"]
    msg = Message(title=m_title,body=m_body)
    if not (flag=='0'):
        msg.save()
        log=LogDetail(manager=user.manager,detail=u'发布公告')
        log.save()
    return render_to_response("courseList.html",
                       { "courseList" : None,
                        "base_url":settings.BASE_URL,
                        "role":"admin",
                        "username":username,
                        "msg":msg} ,
                        context_instance=RequestContext(request)) 
          
@login_required
def delMsg(request):
    user = request.user
    username = user.username
    msgId=request.GET.get("id")

    if not checkUser(user) == 'manager':
       return HttpResponse(u"权限不足")
    
    else:
        if (msgId=='all'):
             msg=Message.objects.all()
             msg.delete()
        else:
            msg=Message.objects.get(id=msgId)
            msg.delete()
    msgList = Message.objects.order_by('-id')
    return render_to_response("all_msg.html",
                              {"username":username,
                               "role":"admin",
                               "msgList":msgList},
                               context_instance=RequestContext(request))    
@login_required
def delLog(request):
        user = request.user
        username = user.username
        logId=request.REQUEST.get("id")

        if not checkUser(user) == 'manager':
                return HttpResponse(u'权限不足')
        else:
                if (logId == 'all'):
                        log=LogDetail.objects.all()
                        log.delete()
                else:
                        log=LogDetail.objects.get(id=logId)
                        log.delete()
        loglist = LogDetail.objects.order_by('-id')
        return render_to_response("loglist.html",
                                    {"username":username,
                                     "loglist":loglist,
                                     "role":'admin',
                                    },
                                    context_instance=RequestContext(request) )

@login_required
def getCourseList(request):
    user=request.user
    username=user.username
    userid=user.id

    role=checkUser(user)

    if role=='manager':
        #待修复问题，manager用户组未被实际采用
        role = 'admin'
        courselist = Course.objects.all()
    elif role == 'teacher':
        courselist = Course.objects.filter(teacher=user.teacher)
    elif role == 'student':
        courselist = Course.objects.filter(student=user.student)
    else:
        return HttpResponse(u'未知用户身份')


    if not(len(Message.objects.all())==0):
         msg = Message.objects.order_by('-id')[0]
    else:
        msg = None  
    return render_to_response("courseList.html",
                       { "courseList" : courselist,
                        "base_url":settings.BASE_URL,
                        "role":role,
                        "username":username,
                        "msg":msg} ,
                        context_instance=RequestContext(request))

@login_required
def addApply(request):
    if "description" in request.POST:
        description = request.POST["description"]
	os = request.POST["need_os"]
	bits = request.POST["bits"]
	print "bits="+bits
	course_code = request.POST["course_code"]
	disk=request.POST["disk"]
	mem=request.POST["mem"]
    user1 = request.user
    username = user1.username
	
	
    if(hasattr(user1,"teacher")):
        teacher = user1.teacher
        apply = ApplyClass(teacher=teacher,OS=os,bits=bits,mem=mem,disk=disk,description=description,course_code=course_code)
        apply.save()
        applylist=ApplyClass.objects.filter(teacher=teacher)
        role = "teacher"
    else:
        applylist = None
        role = None
    return render_to_response("templatelist.html",
                       { "templates" : applylist,
                        "base_url":settings.BASE_URL,
                        "role":role,
                        "username":username} ,
                        context_instance=RequestContext(request))       


@login_required
def createtemp(request):
    user = request.user
    username=user.username
    role = checkUser(user)
    return render_to_response("createNew.html",
                            {"username":username,
                             "role":role
                            },
                            context_instance=RequestContext(request))

@login_required
def getAllTemp(request):
    user=request.user
    username=user.username
    if(hasattr(user,"teacher")):
        applylist=ApplyClass.objects.filter(teacher=user.teacher)
        role = "teacher"
    else:
        applylist=ApplyClass.objects.all()
        role = "admin"
    #print "os="+str(applylist[2].get_OS_display)
    return render_to_response("templatelist.html",
                       { "templates" : applylist,
                        "base_url":settings.BASE_URL,
                        "role":role,
                        "username":username} ,
                        context_instance=RequestContext(request))       
@login_required
def prechangepwd(request):
    username=request.user.username
    user = request.user
    role = checkUser(user)

    if role == 'manager':
        persion = user.manager
        role = 'admin'
    elif role == 'teacher':
        persion = user.teacher
    elif role == 'student':
        persion = user.student
    else:
        persion = None
        role = 'other'


#    if hasattr(user, "teacher"):
#        persion = user.teacher
#        role = "teacher"
#    elif hasattr(user, "student"):
#        persion = user.student
#        role = "student"
#    elif hasattr(user, "admin"):
#        persion = user.admin
#        role = "admin"
#    else:
#        persion = None
#        role = "other"
    return render_to_response("change_password.html",
                       { "username":username,
                          "role":role,
                       } ,
                        context_instance=RequestContext(request))     


@login_required
def getAllStu(request):
    username=request.user.username
    user = request.user
    stulist=Student.objects.all()
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    role = "admin"
    if request.method=="GET":
        try:
            stuGrade = request.GET["grade"][:4]
            stulist
            =Student.objects.filter(user=User.objects.filter(username__contains=stuGrade))
            #利用学号找到uesr然后对应找到学生的信息
        except:
            pass
    else:
        return stulist
    return render_to_response("chakanxuesheng.html",
                       { "username":username,
                          "role":role,
			              "stulist" : stulist,
                          
                       },
                        context_instance=RequestContext(request))  

@login_required
def edituser(request):
    id=request.REQUEST.get('id')
    username=request.user.username
    s=User.objects.filter(username=id)
    user = request.user
    status=request.REQUEST.get("status")
    if status=="stu":
        student=Student.objects.filter(user=s)
    elif status=="tea":
        student=Teacher.objects.filter(user=s)
    if not checkUser(user) == 'manager':
        return HttpResponse(u'权限不足，禁止访问')
    role = "admin"
    return render_to_response("stuedit.html",
                       { "username":username,
                          "role":role,
                          "status":status,
			              "student" : student,
                       } ,
                        context_instance=RequestContext(request))  
    

@login_required
def saveuseredit(request):
    user=request.user
    if not checkUser(user) == 'manager':
        return HttpResponse(u'权限不足，禁止访问')
    if "fullname" in request.POST:
        name=request.POST["fullname"]
    if "studentid" in request.POST:
        id=request.POST["studentid"]
    if "sex" in request.POST:
        sex=request.POST["sex"]
    if "mobilephone" in request.POST:
        mobilephone=request.POST["mobilephone"]
    if "institute" in request.POST:
        institute=request.POST["institute"]
    if "major" in request.POST:
        major=request.POST["major"]
    if "description" in request.POST:
        description=request.POST["description"]
    if "status" in request.POST:
        status=request.POST["status"]
    username=request.user.username
    su=User.objects.filter(username=id)[0]

    student = Student.objects.filter(user=su)
    if student:
        student=student[0]
        student.description=description
        student.name=name
        student.sex=sex
        student.mobilephone=mobilephone
        student.major=major
        student.institute=institute
        student.save()

        stulist=Student.objects.all()
        role = "admin"
        return render_to_response("stulist.html",
                           { "username":username,
                              "role":role,
    			              "stulist" : stulist,
                           } ,
                            context_instance=RequestContext(request))  
    else:
        teacher = Teacher.objects.filter(user=su)[0]
        teacher.description=description
        teacher.name=name
        teacher.sex=sex
        teacher.mobilephone=mobilephone
        teacher.major=major
        teacher.institute=institute
        teacher.save()

        tealist=Teacher.objects.all()
        role = "admin"
        return render_to_response("tealist.html",
                           { "username":username,
                              "role":role,
                              "tealist" : tealist,
                           } ,
                            context_instance=RequestContext(request))  

@login_required
def preaddnewstu(request):
    if not checkUser(request.user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    role = "admin"
    username=request.user.username
    return render_to_response("newuser.html",
                       { "username":username,
                          "role":role,
                       } ,
                        context_instance=RequestContext(request))  

@login_required
def preaddnewtea(request):
    if not checkUser(request.user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    role = "admin"
    username=request.user.username
    return render_to_response("newtea.html",
                       { "username":username,
                          "role":role,
                       } ,
                        context_instance=RequestContext(request))  


@login_required
def addnewuser(request):
    user=request.user
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    if "fullname" in request.POST:
        name=request.POST["fullname"]
    if "studentid" in request.POST:
        id=request.POST["studentid"]
    if "sex" in request.POST:
        sex=request.POST["sex"]
    if "mobilephone" in request.POST:
        mobilephone=request.POST["mobilephone"]
    if "institute" in request.POST:
        institute=request.POST["institute"]
    if "major" in request.POST:
        major=request.POST["major"]
    if "description" in request.POST:
        description=request.POST["description"]
    if "status" in request.POST:
        status=request.POST["status"]
    username=request.user.username
    role = "admin"
    
    try:
        u=User(username=id)
        u.save()
        if status=="student":
            student = Student(user=u,description=description,name=name,sex=sex,mobilephone=mobilephone,major=major
                ,institute=institute)
            student.save()
            log = LogDetail(manager = request.user.manager,detail = u'添加学生'+id)
            log.save()
            stulist=Student.objects.all()
            
            return render_to_response("stulist.html",
                               { "username":username,
                                  "role":role,
                                  "stulist" : stulist,
                               } ,
                                context_instance=RequestContext(request))  
        else:
            teacher = Teacher(user=u,description=description,name=name,mobilephone=mobilephone,institute=institute)
            teacher.save()
            log = LogDetail(manager = request.user.manager,detail = u'添加教师'+id)
            log.save()
            tealist=Teacher.objects.all()
            
            return render_to_response("tealist.html",
                               { "username":username,
                                  "role":role,
                                  "tealist" : tealist,
                               } ,
                                context_instance=RequestContext(request))  
    except Exception:
        if status=="student":
            return render_to_response("newuser.html",
                           { "username":username,
                              "role":role,
                              "infomation":"the user exist!!!",
                           } ,
                            context_instance=RequestContext(request))
        else:
            return render_to_response("newtea.html",
                           { "username":username,
                              "role":role,
                              "infomation":"the user exist!!!",
                           } ,
                            context_instance=RequestContext(request)) 

@login_required
def getAllTea(request):
    username=request.user.username
    user = request.user
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足,禁止访问')
    tealist=Teacher.objects.all()
    role = "admin"
    return render_to_response("tealist.html",
                       { "username":username,
                          "role":role,
                          "tealist" : tealist,
                       } ,
                        context_instance=RequestContext(request))  

@login_required
def getCourse(request):
    user=request.user
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    username=user.username
    role = "admin"
    courselist=Course.objects.all();
    return render_to_response("allcourse.html",
                       { "courseList" : courselist,
                        "role":role,
                        "username":username} ,
                        context_instance=RequestContext(request))

@login_required
def getvmbyparam(request):
    user=request.user
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    username=user.username
    role = "admin"
    course_code=request.REQUEST.get("cid")
    course=Course.objects.filter(course_code=course_code)[0]
    sl=Stu_VM.objects.filter(course=course)
    session=vm_status.create_session("http://192.178.1.100","root","123456")
    svmlist=[]
   
    all_vm_status=vm_status.show_vm_status_by_course(session,course_code)

    for a in sl:
        vmstatus=vm_status.get_vm_status(session,a.virtualmachine.VM_number)
        if vmstatus==None:
            vmstatus="nothing"
        c=[a,vmstatus]
        svmlist.append(c)

    tvmlist=[]
    tl=Tea_VM.objects.filter(course=course)
    for a in tl:
        vmstatus=vm_status.get_vm_status(session,a.virtualmachine.VM_number)
        if vmstatus==None:
            vmstatus="nothing"
        c=[a,vmstatus]
        tvmlist.append(c)

    return render_to_response("coursevmlist.html",
                       { "svmlist" : svmlist,
                        "tvmlist" : tvmlist,
                        "cid":course_code,
                        "role":role,
                        "username":username,
						"all_vm_status":all_vm_status,} ,
                        context_instance=RequestContext(request))

@login_required
def getVmInfo(request):
    cid=request.REQUEST.get('cid')
    vm_num=request.REQUEST.get('vm_num')
    username=request.user.username
    session=vm_status.create_session("http://192.178.1.100","root","123456")
    vm_info = vm_status.get_vm_info(session,vm_num)
    if not checkUser(request.user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    role = "admin"
	
    return render_to_response("vminfo.html",
				{"role":role,
				 "vm_info":vm_info,
				 "username":username,
			         "cid":cid
				},
				context_instance=RequestContext(request))

@login_required
def deletevm(request):
    user=request.user
    username=user.username
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    role = "admin"

    status=request.REQUEST.get("status")
    vmid=request.REQUEST.get("vmid")
    course_code=request.REQUEST.get("cid")
    '''
    if(status=="s"):
        v=VirtualMachine.objects.filter(VM_number=vmid)[0]
        vm=Stu_VM.objects.filter(virtualmachine=v)
        vm.delete()
    elif(status=="t"):
        v=VirtualMachine.objects.filter(VM_number=vmid)[0]
        vm=Tea_VM.objects.filter(virtualmachine=v)[0]
        #vm.delete()
    '''

    delete_vm.delete_vm_on_XenSever("aa",vmid)
    log = LogDetail(manager = user.manager,detail = u'删除虚拟机'+vmid)
    course=Course.objects.filter(course_code=course_code)[0]

    sl=Stu_VM.objects.filter(course=course)
    session=vm_status.create_session("http://192.178.1.100","root","123456")
    svmlist=[]
    for a in sl:
        vmstatus=vm_status.get_vm_status(session,a.virtualmachine.VM_number)
        if vmstatus==None:
            vmstatus="nothing"
        c=[a,vmstatus]
        svmlist.append(c)

    tvmlist=[]
    tl=Tea_VM.objects.filter(course=course)
    for a in tl:
        vmstatus=vm_status.get_vm_status(session,a.virtualmachine.VM_number)
        if vmstatus==None:
            vmstatus="nothing"
        c=[a,vmstatus]
        tvmlist.append(c)




    return render_to_response("coursevmlist.html",
                       { "svmlist" : svmlist,
                        "tvmlist" : tvmlist,
                        "role":role,
                        "cid":course_code,
                        "username":username} ,
                        context_instance=RequestContext(request))

@login_required
def preaddvm(request):
    user=request.user
    username=user.username
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    role = "admin"
    cid=request.REQUEST.get("cid")

    if len(cid)==1:
        cid="0"+cid
    return render_to_response("addsinglevm.html",
                       {"role":role,
                       "cid":cid,
                        "username":username} ,
                        context_instance=RequestContext(request))


@login_required
def addsinglevm(request):
    user=request.user
    username=user.username
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    role = "admin"

    status=""
    

    if "status" in request.POST:
        status=request.POST["status"]
    if "courseid" in request.POST:
        courseid=request.POST["courseid"]
    if "stuid" in request.POST:
        stuid=request.POST["stuid"]
    
    if status=="stu":
	log.info("create")
        create_one.create_one_student_vm(stuid,courseid)
        log_detail = LogDetail(manager = user.manager,detail = u'添加学生机'+stuid)
        log_detail.save()
    elif status=="tea":
        create_one.create_one_teacher_vm(stuid,courseid)    
        log_detail = LogDetail(manager = user.manager,detail = u'添加教师机'+stuid)
        log_detail.save()
 


    courselist=Course.objects.all();
    return render_to_response("allcourse.html",
                       { "courseList" : courselist,
                        "role":role,
                        "username":username} ,
                        context_instance=RequestContext(request))


@login_required
def changestatus(request):
    user=request.user
    username=user.username
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    role = "admin"

    vmid=request.REQUEST.get("id")
    newstatus=request.REQUEST.get("s")
    cid=request.REQUEST.get("cid")

    session=vm_status.create_session("http://192.178.1.100","root","123456")
    vm_status.change_vm_status(session,vmid,newstatus)
    

    course=Course.objects.filter(course_code=cid)[0]
    sl=Stu_VM.objects.filter(course=course)
   
    svmlist=[]
    for a in sl:
        vmstatus=vm_status.get_vm_status(session,a.virtualmachine.VM_number)
        if vmstatus==None:
            vmstatus="nothing"
        c=[a,vmstatus]
        svmlist.append(c)

    tvmlist=[]
    tl=Tea_VM.objects.filter(course=course)
    for a in tl:
        vmstatus=vm_status.get_vm_status(session,a.virtualmachine.VM_number)
        if vmstatus==None:
            vmstatus="nothing"
        c=[a,vmstatus]
        tvmlist.append(c)

    return render_to_response("coursevmlist.html",
                       { "svmlist" : svmlist,
                        "tvmlist" : tvmlist,
                        "cid":cid,
                        "role":role,
                        "username":username} ,
                        context_instance=RequestContext(request))

@login_required
def preAddNewCourse(request):
    user=request.user
    username=user.username
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    role = "admin"

    return render_to_response("newcourse.html",
                       {"role":role,
                        "username":username} ,
                        context_instance=RequestContext(request))


@login_required
def uploadFile(request):
    user=request.user
    username=user.username
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    role = "admin"


    if "textfield" in request.POST:
        #name=request.POST["textfield"]
       # sfile=request.FILES["fileField"]
        #name=sfile.name()
        name="a"
        files = request.FILES.getlist('fileField')
	for f in files:     
            #e = Excel("/var/www/UIBE_VM1/new_course.xls")
            filepath=os.path.join("/var/www/UIBE_VM1/course.xls")
            dest=open(filepath,"wb+")
            dest.write(f.read())
            dest.close()
                
            e=Excel(filepath)
            name=f.size

            print f

            
            #获取学生名单
            stu_username = e.get_stu_username_list()
            stu_name = e.get_stu_name_list()
            #获取教师信息
            tea_username = e.get_tea_username()
            tea_name = e.get_tea_name()
            #获取课程信息
            course_code = e.get_course_code()
            course_name = e.get_course_name()

            #创建学生列表
            stu_list = Student_List(stu_username,stu_name)
            student_list = stu_list.create_stu_list()
            #创建教师
            tea = Single_Teacher(tea_username,tea_name)
            teacher = tea.create_single_tea()
            #创建课程
            single_course = Single_Course(course_code,course_name,Student_List.get_stu_list(stu_username),Single_Teacher.get_tea_by_username(tea_username))
            course = single_course.create_course()

            if course == None:
                print u"结束"
            else:
                ip_pre = '192.178'
                mac_pre = '1a:2b:3c:4d'
                #创建并绑定教师机器
                single_teacher_vm = Single_Teacher_VM(course_code,ip_pre,mac_pre)
                tea_vm = single_teacher_vm.create_VM()
                bind_tea_vm = Single_Teacher_VM.bind_VM(Single_Teacher.get_tea_by_username(tea_username),course,tea_vm)
                #创建并绑定学生机器列表
                student_machine_list = Student_VM_List(course_code,ip_pre,mac_pre,Student_List.get_stu_list(stu_username))
                new_stu_list = student_machine_list.create_VM_List()
                bind_stu_vm_list = student_machine_list.bind_VM_List(course,new_stu_list)
                
                
                #学生机配置文件写入XML
                for stu_vm in bind_stu_vm_list:
                    username = stu_vm.student.user.username
                    course_name = stu_vm.course.course_name
                    ip = stu_vm.virtualmachine.ip
                    add_xml = Change_XML(username,'123456',course_name,ip)
                    add_xml.generate_xml()
                    add_xml.write_xml()

                #教师机配置文件写入XML
                add_xml = Change_XML(bind_tea_vm.teacher.user.username,'123456',bind_tea_vm.course.course_name,bind_tea_vm.virtualmachine.ip)
                add_xml.generate_xml()
                add_xml.write_xml() 
                

                #解析数据库配置信息
                conf = ConfigParser.ConfigParser()
                conf.read("generate_vm.cfg")
                '''
                database = conf.get('database_info','database')
                user = conf.get('database_info','user')
                password = conf.get('database_info','password')
                host = conf.get('database_info','host')
                '''
                #database = conf.get('database_info','database')
                database="misspast"
                host="10.1.1.244"
                user="misspast"
                #password = conf.get('database_info','password')
                password='1'
                conn = Xen_VM.pg_connection(database,user,password,host)

                #模式匹配
                mac_pattern =course_code + '___'
                mac_dict = Xen_VM.get_mac_list(conn,mac_pattern)
                #重启DHCP服务
                Xen_VM.dhcp_restart(conn)

                #XENServer配置信息读取
                #server_ip = conf.get('xenserver_info','server_ip')
                #xen_user = conf.get('xenserver_info','xen_user')
                #xen_password = conf.get('xenserver_info','xen_password')
                #创建新的会话连接

                server_ip="http://192.178.1.100"
                xen_user="root"
                xen_password="123456"
                session = Xen_VM.create_session(server_ip,xen_user,xen_password)
                #获取配置文件中的网卡信息和获得当年的网络名称
                pif='bond0'
    	    	#pif = conf.get('vm_info','pif')
                network = Xen_VM.network_selection(session,pif)
                #template_name = conf.get('vm_info','template_name')
                #获取模板名称，并依照数量复制模板 
                template_name = single_course.get_course_name()+ u"模板"
                template_name_list = Xen_VM.template_copy(session,len(bind_stu_vm_list),template_name)
                vm_list = Xen_VM.generate_vm_list(session,mac_dict,network,template_name_list,course_name)
                for vm in vm_list:
                    Xen_VM.first_start_vm(session,vm)
                    

    courselist=Course.objects.all();
    return render_to_response("allcourse.html",
                        { "courseList" : courselist,
                         "role":role,
                         "username":username} ,
                         context_instance=RequestContext(request))
    

@login_required
def addNewCourse(request):
    user=request.user
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    courseId=""
    role="admin"
    username=user.username
    if "courseId" in request.POST:
        courseId=request.POST["courseId"]
    if "courseName" in request.POST:
        courseName=request.POST["courseName"]
    if "teaId" in request.POST:
       	teaId=request.POST["teaId"]
    if "description" in request.POST:
       	description=request.POST["description"]
    if Course.objects.filter(course_code=courseId):
	info="course already exist!!"
    else:
	u=User.objects.filter(username=teaId)
				
	if u:
            user=u[0]
	    t=Teacher.objects.filter(user=user)[0]
	    log.info("add course teacher!!!yy"+t.user.username)
	    course=Course(course_code=courseId,course_name=courseName,description=description)
	    course.save()
	    course.teacher.add(t)
	else:
	    u=User(username=teaId)
	    u.save()
	    t=Teacher(user=u)
	    t.save()
			
	    log.info("add course teacher!!!yy"+t.user.username)
	    course=Course(course_code=courseId,course_name=courseName,description=description)
	    course.save()
	    course.teacher.add(t)
        courselist=Course.objects.all()
    log_detail = LogDetail(manager = request.user.manager,detail = u'添加课程'+courseId)
    log_detail.save()
    return render_to_response("allcourse.html",
                       { "courseList" : courselist,
                        "role":role,
                        "username":username} ,
                        context_instance=RequestContext(request)) 

@login_required
def bootAll(request):
    user=request.user
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    courseId=""
    role="admin"
    username=user.username
    courseId=request.GET['cid']
    if len(courseId)==1:
        courseId="0"+courseId
    session=vm_status.create_session("http://192.178.1.100","root","123456")
    vm_status.change_vm_list_status(session,courseId,"Running")
    log_detail = LogDetail(manager = user.manager,detail = '对课程'+courseId+u'执行全部开机操作')
    log_detail.save()
    courselist=Course.objects.all()
    return render_to_response("allcourse.html",
                        { "courseList" : courselist,
                         "role":role,
                         "username":username} ,
                        context_instance=RequestContext(request))
@login_required
def rebootAll(request):
    user=request.user
    if not checkUser(user)=='manager':
        return HttpResponse(u'权限不足，禁止访问')
    courseId=''
    persion = user.manager
    role='admin'
    username=user.username
    courseId = request.GET['cid']
    if len(courseId)==1:
        courseId = '0'+courseId
    session = vm_status.create_session('http://192.178.1.100','root','123456')
    vm_status.change_vm_list_status(session,courseId,"Reboot")
    log_detail = LogDetail(manager = user.manager,detail = '对课程'+courseId+u'执行全部重启操作')
    log_detail.save()
    courselist=Course.objects.all()
    return render_to_response("allcourse.html",
                        { "courseList" : courselist,
                         "role":role,
                         "username":username} ,
                        context_instance=RequestContext(request))
@login_required
def shutdownAll(request):
    user=request.user
    if not checkUser(user)=='manager':
       return HttpResponse(u'权限不足，禁止访问')
    courseId=""
    role="admin"
    username=user.username
    courseId=request.GET['cid']
    if len(courseId)==1:
      courseId="0"+courseId
    session=vm_status.create_session("http://192.178.1.100","root","123456")
    vm_status.change_vm_list_status(session,courseId,"Halted")
    log_detail = LogDetail(manager = user.manager,detail = '对课程'+courseId+u'执行全部开机操作')
    log_detail.save()
    courselist=Course.objects.all()
    return render_to_response("allcourse.html",
                        { "courseList" : courselist,
                         "role":role,
                         "username":username} ,
                        context_instance=RequestContext(request))
@login_required
def check(request):
	id_num=request.REQUEST.get('id')
	status=request.REQUEST.get('status')
	e=request.REQUEST.get('e')
	msg='None'	
	if(status=='s'):
		stulist=Student.objects.all()
	
		for x in range(len(stulist)):
			e_id_num=stulist[x].user.username		
			if (id_num==e_id_num):
				s_name=stulist[x].name
				if(e=='0'):
					msg='该学生已存在,其姓名为：'+s_name
				else:
					msg=u''
				return HttpResponse(msg)
		if(e=='1'):
			msg='该学生不存在，请先创建'	
		else:
			msg=u''
		return HttpResponse(msg)
	elif(status=='t'):
		teclist=Teacher.objects.all()
		
		for x in range(len(teclist)):
			e_id_num=teclist[x].user.username
			if (id_num==e_id_num):
				t_name=teclist[x].name
				if(e=='0'):
					msg='该教师已存在,其姓名为:'+t_name
				else:
					msg=''					
				return HttpResponse(msg)
		if(e=='1'):
			msg='该教师不存在，请先创建'		
		else:			
			msg=u''
		return HttpResponse(msg)
	else:
		course_list=Course.objects.all()
		for x in range(len(course_list)):
			e_id_num=course_list[x].course_code
			if(id_num==e_id_num):
				c_name=course_list[x].course_name
				msg='该课程已存在，其名为：'+c_name
				return HttpResponse(msg)
		msg=''
		return HttpResponse(msg)
		
