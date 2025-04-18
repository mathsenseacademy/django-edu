from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status

@api_view(['GET','POST'])
def test_host(request):
        return JsonResponse({"result": 'This is starter'}, status = status.HTTP_200_OK) 
