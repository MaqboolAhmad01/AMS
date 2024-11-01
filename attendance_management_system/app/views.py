from django.utils import timezone
from .forms import UserForm, TeamForm, AttendanceForm,SetNewPassword,LoginForm,PasswordResetForm  
from .models import User, Team, Attendance
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from allauth.socialaccount.models import SocialApp
from requests import post,get
from django.conf import settings
import json
def get_user_info(access_token):
    user_info_response = get(settings.USER_INFO_URL, 
                              headers={'Authorization': f'Bearer {access_token}'})
    return user_info_response.json()  # 


def authenticate_user(request,user_info):
    email = user_info['email']
    user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})
    login(request, user,backend=settings.AUTHENTICATION_BACKENDS[0]) 
class GoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = settings.ACCESS_TOKEN_URL
    authorize_url = settings.AUTHORIZATION_URL
class GoogleLogin(View):
    def get(self, request, *args, **kwargs):
        try:
            app = SocialApp.objects.get(provider=GoogleProvider.id)
            redirect_uri = request.build_absolute_uri(f"/accounts/google/login/callback/")
            scope = 'profile email'
            url = f"{GoogleOAuth2Adapter.authorize_url}?client_id={app.client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code&access_type=online&prompt=select_account"
            return HttpResponseRedirect(url)
        except SocialApp.DoesNotExist:
            return HttpResponseRedirect("/")
class GoogleCallback(View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')  # Get the authorization code from the query
        try:
            app = SocialApp.objects.get(provider=GoogleProvider.id)  # Get your app's details
            token_response = post(
                GoogleOAuth2Adapter.access_token_url,
                data={
                    'code': code,
                    'client_id': app.client_id,
                    'client_secret': app.secret,
                    'redirect_uri': request.build_absolute_uri("/accounts/google/login/callback/"),
                    'grant_type': 'authorization_code'
                }
            )
            token_data = token_response.json()
            access_token = token_data['access_token']  # Extract access token
            # Use access token to get user info...
            user_info = get_user_info(access_token=access_token)
            authenticate_user(request=request,user_info=user_info)
            return redirect('dashboard')
        except Exception as e:
           
            return HttpResponseRedirect("/")  

class UserView(View):
    template_name = 'app/user_form.html'  

    def get(self, request, pk=None):
        if pk and request.path.endswith('/update/'):  
            user = get_object_or_404(User, pk=pk)
            form = UserForm(instance=user)
            return render(request, self.template_name, {'form': form})  
        elif pk:  
            user = get_object_or_404(User, pk=pk)
            return render(request, 'app/user_detail.html', {'user': user})  
        elif request.path.endswith('/create/'):
            form = UserForm()
            return render(request, self.template_name, {'form': form})  
        elif request.path.endswith('/users/'):
            users = User.objects.all()
            return render(request, 'app/user_list.html', {'users': users})


    def post(self, request, pk=None):
        if pk and request.path.endswith('/update/'): 
            user = get_object_or_404(User, pk=pk)
            form = UserForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect('user_update', pk=user.pk)
        elif pk and request.path.endswith('/delete/'):
        

            user = get_object_or_404(User,pk=pk)
            user.delete()
            return redirect('user_list')
        else:  
            form = UserForm(request.POST)
            if form.is_valid():
                form.save()
            return render(request, self.template_name, {'form': form})


class login_view(View):
    def post(self,request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user,backend=settings.AUTHENTICATION_BACKENDS[1])
                return redirect('dashboard') 
            else:
                form.add_error(None, 'Invalid username or password.')
        return render(request,'app/login.html',{'form':form})
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = LoginForm()
    
        return render(request, 'app/login.html', {'form': form}) 

@login_required  
def dashboard_view(request):
    username = request.user.username 
    return render(request, 'app/dashboard.html',{'username':username}) 

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def magic_link(request):
    if request.method == 'POST':
        return redirect('https://mail.google.com')
    return render(request, 'app/magic_link_sent.html') 
   
def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
    
                # Generate reset link
                reset_link = request.build_absolute_uri(
                reverse('set_new_password', kwargs={'uidb64': uid, 'token': token})
                )

                send_mail(
                    'Password Reset Request',
                    f'Please click the link to reset your password: {reset_link}',
                    'hamzach12882@gmail.com',
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'A password reset link has been sent to your email.')
                return redirect('magic_link')
            except User.DoesNotExist:
                messages.error(request, 'Email not found.')
    else:
        form = PasswordResetForm()

    return render(request, 'app/reset_password.html', {'form': form})

def set_new_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetNewPassword(request.POST)
            if form.is_valid():
            # Handle the reset password form here
                new_password = form.cleaned_data['new_password']
                confirm_password = form.cleaned_data['confirm_password']

                if new_password and confirm_password and new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    return redirect('login')
                else:
                    return render(request, 'app/set_new_password.html', {'error': 'Passwords do not match.'})
        form = SetNewPassword()
        return render(request, 'app/set_new_password.html', {'uidb64': uidb64, 'token': token,'form':form})
    else:
        # Invalid token
        return render(request, 'app/reset_password_invalid.html')
    
@login_required
def check_in_view(request):
    if request.method == 'POST':
        user = request.user  # Get the current user
        current_date = timezone.now().date() 
        check_in  = timezone.now().time() # Get today's date
       

        # Check if the user has already checked in today
        attendance = Attendance.objects.create(
            user=user,
            date=current_date,
            status= 'present',  
            day=timezone.now().strftime('%A'),
            check_in=check_in,  
            extra_hours= 0.0,
            total_hours= 0.0
        )

        
        attendance.save()

        return JsonResponse({'message': 'Check-in successful', 'attendance_id': attendance.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
def check_out_view(request):
    if request.method == 'POST':
        user = request.user  # Get the current user
        data = json.loads(request.body)
        # Extract variables from the parsed data
        attendance_id = data.get('attendance_id')
        current_date = timezone.now().date()  # Get today's date

        try:
            # Get today's attendance record for the user
            
            attendance = Attendance.objects.get(id=attendance_id)
            


            # Set the current time as the check-out time
            attendance.check_out = timezone.now().time()
            

            # Calculate total hours worked and extra hours if needed
            if attendance.check_in:
                
                check_in_time = timezone.datetime.combine(current_date, attendance.check_in)
                check_out_time = timezone.datetime.combine(current_date, attendance.check_out)
                total_hours = (check_out_time - check_in_time).total_seconds() / 3600  # Convert to hours

                # Assuming a normal workday of 9 hours for extra hours calculation
                if total_hours > 9:
                    attendance.extra_hours = total_hours - 9
                else:
                    attendance.extra_hours = 0

                attendance.total_hours = total_hours

            attendance.save()  # Save the updated attendance record

            return JsonResponse({'message': 'Check-out successful', 'check_out_time': str(attendance.check_out)})
        except Attendance.DoesNotExist:
            return JsonResponse({'error': 'No check-in record found for today.'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@require_GET
def attendance_view(request,timeframe):
    user = request.user
    now = timezone.now()
    current_date = timezone.now().date()
    total_time = 0

    if timeframe == 'day':
        attendances = Attendance.objects.filter(user=user,date=current_date)
        if not attendances:
            return JsonResponse({"error":"no attendance record found"})
        for attendance in attendances:
            check_in_datetime = timezone.datetime.combine(current_date, attendance.check_in)
            
            if not attendance.check_out:        
                total_time = total_time + (now - check_in_datetime).total_seconds()
            else:
                check_out_datetime = timezone.datetime.combine(current_date, attendance.check_out)
                total_time = total_time + (check_out_datetime - check_in_datetime).total_seconds()
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)



        return JsonResponse({'labels': ['today'], 'data': [total_time],'total_time':{'hours':hours,'minutes':minutes,'seconds':seconds}})
    return JsonResponse({"error":"not day"})
def create_team(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('team_list')  
    else:
        form = TeamForm()
    return render(request, 'app/create_team.html', {'form': form})

def create_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('attendance_list')  
    else:
        form = AttendanceForm()
    return render(request, 'app/create_attendance.html', {'form': form})

def user_list(request):
    users = User.objects.all()
    return render(request, 'app/user_list.html', {'users': users})

def team_list(request):
    teams = Team.objects.all()
    return render(request, 'app/team_list.html', {'teams': teams})

def attendance_list(request):
    attendance_records = Attendance.objects.all()
    return render(request, 'app/attendance_list.html', {'attendance_records': attendance_records})
