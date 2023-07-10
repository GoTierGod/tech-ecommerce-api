from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view()
def home(request):
    return Response({"message": "Bad request"}, status=400)
