from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .restapis import get_dealers_from_cf, get_dealer_reviews_by_id_from_cf, get_dealer_from_cf_by_id, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

def about(request):
    return render(request, 'djangoapp/about.html', {})

def contact(request):
    return render(request, 'djangoapp/contact.html', {})

def login_request(request):
    context = {}

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/djangoapp/')
        else:
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

def logout_request(request):
    logout(request)
    return render(request, 'djangoapp/logout.html', {})

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            print("User already exists!")

        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect("/djangoapp/")
        else:
            return render(request, 'djangoapp/registration.html', context)


def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = 'https://eu-de.functions.appdomain.cloud/api/v1/web/8d8b4315-8096-4d5c-babb-c0a7a3f1326e/dealership-package/get-dealership'
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context = {"dealerships": get_dealers_from_cf(url)}
        return render(request, 'djangoapp/index.html', context)

def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = 'https://eu-de.functions.appdomain.cloud/api/v1/web/8d8b4315-8096-4d5c-babb-c0a7a3f1326e/dealership-package/get-review'
        context = {"reviews":  get_dealer_reviews_by_id_from_cf(url, dealer_id), "dealerId": dealer_id}
        return render(request, 'djangoapp/dealer_details.html', context)


def add_review(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/8d8b4315-8096-4d5c-babb-c0a7a3f1326e/dealership-package/get-dealership"
        dealer = get_dealer_from_cf_by_id(url, dealer_id)
        cars = CarModel.objects.filter(dealerid=dealer_id)
        context["cars"] = cars
        context["dealer"] = dealer
        return render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/8d8b4315-8096-4d5c-babb-c0a7a3f1326e/dealership-package/post-review"      
        if 'purchasecheck' in request.POST:
            was_purchased = True
        else:
            was_purchased = False
        cars = CarModel.objects.filter(dealerid=dealer_id)
        for car in cars:
            if car.id == int(request.POST['car']):
                review_car = car  
        review = {}
        review["time"] = datetime.utcnow().isoformat()
        review["name"] = request.POST['name']
        review["dealership"] = dealer_id
        review["review"] = request.POST['content']
        review["purchase"] = was_purchased
        review["purchase_date"] = request.POST['purchasedate']
        review["car_make"] = review_car.carmake.name
        review["car_model"] = review_car.name
        review["car_year"] = review_car.year.strftime("%Y")
        json_payload = {}
        json_payload["review"] = review
        response = post_request(url, json_payload)
        print(response)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
