from django.db import models
from django.contrib.auth.models import User

class Organ(models.Model):
    blood_group = models.CharField(max_length=3)
    organ = models.CharField(max_length=50)
    organ_date_time = models.DateTimeField()
    smoke = models.BooleanField()
    alcohol = models.BooleanField()
    drug = models.BooleanField()
    avg_sleep = models.PositiveIntegerField()
    daily_exercise = models.PositiveIntegerField()
    donor = models.OneToOneField('userauth.Donor', on_delete=models.CASCADE)

    def __str__(self):
        return self.organ


class Post(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.OneToOneField('userauth.Recipient', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='images/', blank=True, null=True)
    done = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    




# Create your models here.

class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor')   
    phone_number = models.CharField(max_length=15)
    birthday = models.DateField()
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=10)
    health_card_number = models.CharField(max_length=12)

    def __str__(self):
        return self.user.username

class Recipient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recipient')
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=10)
    state = models.CharField(max_length=50)
    health_card_number = models.CharField(max_length=12)
    birthday = models.DateField()
    blood_group = models.CharField(max_length=3)
    organ = models.CharField(max_length=50)

    

    def __str__(self):
        return self.user.username
