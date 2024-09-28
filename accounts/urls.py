from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('login', views.login_view, name='login'),   ## accounts/login (accounts come from main urls.py)
    path('register', views.register, name='register'),  ## accounts/register
    path('logout', views.logout_view, name='logout'),        ## accounts/logout
    # path('dashboard', views.dashboard, name='dashboard'),   ## accounts/dashboard
    # path('agents/<str:pk>/', views.agents, name='agents'),   ## accounts/agents
    # path('verify-email/', views.verifyEmail, name='verify_email'),
    # path('verify-otp/', views.verifyOTP, name='verify_otp'),
    # path('forget-password/', views.forgetPassword, name='forget_password'),
    # path('reset-password/', views.resetPassword, name='reset_password'),
]