
# backend/donation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('organ/', views.OrganDonorView.as_view()),
    path('find-matches/', views.FindOrganMatchesView.as_view()),
    path('compatibility/', views.CompatibilityCheckView.as_view()),
    path('available-donors/', views.AvailableDonorsView.as_view()),
    path('author/', views.PostAuthor.as_view()),
    path('', views.PostEveryone.as_view()),
    path('signup/donor/', views.DonorSignUp.as_view()),
    path('signup/recipient/', views.RecipientSignUp.as_view()),
    path('get/', views.GETRecipient.as_view()),
    # path('login/', views.Login.as_view(), name='login'),
]
