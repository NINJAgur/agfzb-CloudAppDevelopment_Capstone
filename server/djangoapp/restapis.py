import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

def get_dealer_from_cf_by_id(url, dealer_id):
    for dealer in get_dealers_from_cf(url) :
        if dealer.id == dealer_id:
            return dealer
    return None

def get_dealer_reviews_by_id_from_cf(url, dealerId):
    results = []
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        reviews = json_result

        for review in reviews:
            review_obj = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                purchase=review["purchase"],
                review=review["review"],
                purchase_date=review["purchase_date"],
                car_make=review["car_make"],
                car_model=review["car_model"],
                car_year=review["car_year"],
                sentiment=analyze_review_sentiments(review["review"]),
                )
            results.append(review_obj)

    return results

def analyze_review_sentiments(dealer_review, **kwargs):
    api_key = "gVy2jBoOU3Wim-X8PROU7mOPmoV0yWMm1UOVoQi0a9iy"
    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/a423f9b7-ef6c-4f6e-a6dc-a2f64a9aafac"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2023-08-13', authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze(
        text=dealer_review, 
        language='en', 
        features=Features(
        sentiment=SentimentOptions(targets=[dealer_review]))).get_result()
    label = json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    return(label)

def post_request(url, json_payload, **kwargs):
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        status_code = response.status_code
        json_data = json.loads(response.text)
        return json_data
    except:
        print("Failed")

