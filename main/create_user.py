from django.http import JsonResponse
from csv import reader
from django.contrib.auth.decorators import user_passes_test

from .models import NewUser



#http://127.0.0.1:8000/userdata/

@user_passes_test(lambda user: user.is_superuser)
def userdata(request):
    with open(r'D:\Python\tickets\main\templates\user.csv', 'r') as csv_file:
        csvf = reader(csv_file)
        data = []
        for username, password,wh, *__ in csvf:
            user = NewUser(user=username, wh=wh)
            # user = NewUser()
            user.set_password(password)
            user.is_active=True
            user.is_courier=True
            data.append(user)
        NewUser.objects.bulk_create(data)
    
    return JsonResponse('user csv is now working', safe=False)