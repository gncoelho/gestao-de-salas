from datetime import datetime
from django.shortcuts import render

def welcome(request):
    context = {
        'year': datetime.now().year,
    }
    return render(request, 'core/welcome.html', context)
