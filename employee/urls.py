from .views import EmployeeListApi #EmployeeApi
from django.urls import path

urlpatterns = [
    # path('', EmployeeApi.as_view(), name="employeeapi"),
    path('', EmployeeListApi.as_view(), name="employeelist")
]