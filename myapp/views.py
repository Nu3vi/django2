from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response


def hola_mundo(request):
    return HttpResponse("¡Hola mundo desde Django!")

class HolaMundoAPIView(APIView):
    def get(self, request):
        return Response({"mensaje": "¡Hola mundo desde la API REST!", "hola":"gaaa"})