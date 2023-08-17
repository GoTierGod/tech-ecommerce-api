from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


@permission_classes([IsAuthenticated, IsAdminUser])
@api_view(["GET"])
def routes(request):
    routes = ["api/", "api/token/", "api/token/refresh/", "api/token/blacklist/"]

    return Response(routes, status=200)
