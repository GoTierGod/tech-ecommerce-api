from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User


# Create your views here.
@api_view()
def welcome(request):
    return Response(User.objects.get(pk=1).username)
