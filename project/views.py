from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser


@permission_classes([IsAuthenticated, IsAdminUser])
@api_view(["GET"])
def routes(request: Request):
    return Response({"message": "Made by @GoTierGod."}, status=200)
