from django.conf.urls import url

from . import views

urlpatterns = [
    url('^login/$', views.login),
    url('^resend-otp/$', views.resend_otp),
    url('^verify-otp/$', views.verify_otp),
    url('^forget-password/$', views.forget_password),
    url('^reset-password/$', views.reset_password),
    url('^add-user/$', views.add_user),
    url('^list/$', views.get_user_list),
    url('^delete/$', views.delete_user),
    url('^details/$', views.get_details),

]
