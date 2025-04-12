from django.core.serializers import serialize
from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from .serializers import EmployeeSerializer
from .models import Employee
from rest_framework import generics, permissions, status
from rest_framework.views import APIView


# class EmployeeApi(generics.GenericAPIView):
#     def post(self, request, *args, **kwargs):
#         employees = Employee.objects.all()
#         serializer = EmployeeSerializer(employees, many=True)
#
#         return Response({
#             'data': serializer.data
#         })


class EmployeeListApi(APIView):

    permission_classes = [permissions.IsAuthenticated,]
    authentication_classes = [TokenAuthentication,]  #Authentication Token ea4a266f8702f86f49df705757a6ae421c4327b4 kirirtilsa keyin ishlaydi
                                                     # yani token berilgandan keyin listni chiqarib beradi
    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)

        response = {
            'data': serializer.data,
            'status': status.HTTP_200_OK,
            'message': 'Employee list',
        }
        return Response(response)