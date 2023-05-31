from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User


# Create your views here.
@api_view()
def welcome(request):
    data = {"user": User.objects.get(pk=1).username}
    return Response(data, content_type="application/json", status=200)
