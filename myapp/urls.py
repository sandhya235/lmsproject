from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', home_view, name='index'),
    
    # Admin Paths
    path('adminclick/', adminclick_view, name='adminclick'),
    path('adminclick/adminsignup/', adminsignup_view, name='adminsignup'),
    path('adminclick/adminlogin/', adminlogin_view, name='adminlogin'),
    path('adminafterlogin/', admin_after_login_view, name='adminafterlogin'),

    path('adminafterlogin/addbook/', addbook_view, name='addbook'),
    path('adminafterlogin/viewbook/', viewbook_view, name='viewbook'),
    path('adminafterlogin/issuebook/', issuebook_view, name='issuebook'),
    path('adminafterlogin/viewissuedbook/', viewissuedbook_view, name='viewissuedbook'),
    path('adminafterlogin/viewstudent/', viewstudent_view, name='viewstudent'),

    # Student Paths
    path('studentclick/', studentclick_view, name='studentclick'),
    path('studentclick/studentsignup/', studentsignup_view, name='studentsignup'),
    path('studentclick/studentlogin', studentlogin_view, name='studentlogin'),
    path('studentafterlogin/', student_after_login_view, name='studentafterlogin'),

    # View issued books for students
    path("view-issued-books/", viewissuedbookbystudent, name="viewissuedbookbystudent"),

    path('logout/', logout_view, name='logout'),
    path('logoutstudent/', logoutstudent_view, name='logoutstudent'),
    path('studentlogout/', logoutstudent_view, name='logoutstudent'),
    path('adminlogout/', logout_view, name='adminlogout'),
    path('success-page/',success_page,name='success-page'),
    path('adminafterlogin/deletebook/<int:book_id>/', deletebook_view, name='deletebook'),
    path('adminafterlogin/deletestudent/<int:student_id>/', delete_student_view, name='deletestudent'),
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
        name='password_reset'),

    # Password reset email sent page
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
        name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
        name='password_reset_confirm'),
    
    path('reset/done/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
        name='password_reset_complete'),
    

    path('password-reset/', CustomPasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('delete-issued-book/<int:issued_book_id>/', delete_issued_book_view, name='delete_issued_book'),

]