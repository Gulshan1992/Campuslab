from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework.response import Response
import json
from rest_framework.views import APIView
from django.contrib import auth
from account.models import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .serializers import AccountSerializer,DestinationsSerializer
import requests

# Create your views here.
@api_view(['POST', 'GET'])
def UserRegistrationView(request):
    if request.method == 'POST':
        website = request.POST.get('website')
        email = request.data.get('email')
        name = request.data.get('name')
        accountID = request.data.get('accountID')
        website = request.data.get('website', '')  # Optional field
        # Validate if email, name, or accountID already exists
        if Account.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if Account.objects.filter(name=name).exists():
            return JsonResponse({'message': 'Name already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if Account.objects.filter(accountID=accountID).exists():
            return JsonResponse({'message': 'Account ID already exists'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        return JsonResponse({'message': 'GET method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST', 'GET'])
def DestinationView(request):
    if request.method == 'POST':
        serializer = DestinationsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        account_id = request.query_params.get('account_id')
        if not account_id:
            return JsonResponse({'message': 'Account ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            account = Account.objects.get(account_id=account_id)
        except Account.DoesNotExist:
            return JsonResponse({'message': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        destinations = account.destinations.all()
        serializer = DestinationsSerializer(destinations, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def IncomingDataView(request):
    # Get the app_secret_token from query parameters
    app_secret_token = request.query_params.get('app_secret_token')
    # Check if app_secret_token is provided
    if not app_secret_token:
        return JsonResponse({'message': 'Unauthenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    # app_secret_token is not JSON; it's a plain string
    token = app_secret_token
    # Try to get the account with the given token
    try:
        account = Account.objects.get(app_secret_token=token)
        accountid = account.id
    except Account.DoesNotExist:
        return JsonResponse({'message': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
    # Parse the body of the request as JSON
    data = request.data  # Since request.data is already parsed JSON
    if not isinstance(data, dict):
        return JsonResponse({'message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
    destinations = Destinations.objects.filter(account_id=accountid)
    # Iterate through the destinations and send data accordingly
    # Process the data and send it to destinations
    for destination in destinations:
        headers = destination.headers
        headers['Content-Type'] = 'application/json'
        if destination.http_method.upper() == 'GET':
            response = requests.get(destination.url, params=data, headers=headers)
        elif destination.http_method.upper() in ['POST', 'PUT']:
            response = requests.post(destination.url, json=data, headers=headers)
        else:
            return JsonResponse({'message': 'Invalid HTTP method'}, status=status.HTTP_400_BAD_REQUEST)
        
        if response.status_code != 200:
            return JsonResponse({'message': 'Failed to send data to one or more destinations'}, status=response.status_code)
    
    return JsonResponse({'message': 'Data successfully sent to all destinations'}, status=status.HTTP_200_OK)



@api_view(['POST'])
def AccountDeleteView(request):
    # Extract the account_id from the query parameters
    account_id = request.query_params.get('account_id')
    if not account_id:
        return JsonResponse({'error': 'account_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    # Check if the account exists
    account = get_object_or_404(Account, id=account_id)
    # Check if any destinations are associated with the account
    destinations_exist = Destinations.objects.filter(account_id=account_id).exists()
    if destinations_exist:
        # Delete the account
        account.delete()
        return JsonResponse({'message': 'Account and its destinations deleted successfully'}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'message': 'Account does not exist'}, status=status.HTTP_404_NOT_FOUND)
    


