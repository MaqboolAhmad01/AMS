import uuid
from django.db import models

# Create your models here.
from django.db import models
from.custom_types import CustomPosition,Status,UserRole
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Team(models.Model):
    

    name = models.CharField(max_length=100)
    room_number = models.IntegerField(null=True,blank=True)
    total_strength = models.IntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    
    def create_superuser(self ,email,username,  password=None, **extra_fields):
        """
        Creates and saves a superuser. Additional fields like first_name, last_name are not required.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        print("superuser executed")

        email = self.normalize_email(email)
        user = self.model(email=email,username=username, **extra_fields)
        user.set_password(password) 
        user.save()
        return user
    
class BaseUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    role = models.CharField(max_length=100, choices=UserRole.choices)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = UserManager()
    
    class Meta:
        abstract = True 


class User(BaseUser):
   


    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    profile_photo = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(max_length=200)
    joined_at = models.DateField(null=True)
    position = models.CharField(max_length=100, choices=CustomPosition.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True,blank=True)


    def save(self, *args, **kwargs):
        # Check if password is in the fields and is not already hashed
        if self.pk is None or not self._state.adding:  # New or updating instance
            if self.password and not self.password.startswith('pbkdf2_sha256$'):  # Check if password is plain text
                self.set_password(self.password)  # Hash the password using set_password method
        
        # Call the superclass's save method to save the user
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class Attendance(models.Model):
    

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices,null=True,blank=True)
    day = models.CharField(max_length=20)
    check_in = models.TimeField(null=True,blank=True)
    check_out = models.TimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    extra_hours = models.FloatField()
    approved_hours = models.FloatField(default=0.0)
    total_hours = models.FloatField()
    

    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    def clean(self):
        if self.status == 'absent':
            if self.check_in is not None or self.check_out is not None:
                raise ValidationError("Check-in and check-out times must be null if status is absent.")
        else:
            if not self.check_in or not self.check_out:
                raise ValueError("cannot be empty")
            if self.check_in >= self.check_out:
                raise ValueError("Check out time cannot be before check in time")
        
    
    def save(self, *args, **kwargs):

        if self.check_in and self.check_out:
            check_in_datetime = datetime.combine(self.date, self.check_in)
            check_out_datetime = datetime.combine(self.date, self.check_out)
            total_hours_worked = (check_out_datetime - check_in_datetime).total_seconds() / 3600
            
            self.total_hours = total_hours_worked
            if total_hours_worked > 9:
                self.extra_hours = total_hours_worked - 9
            else:
                self.extra_hours = 0

        super(Attendance, self).save(*args, **kwargs)