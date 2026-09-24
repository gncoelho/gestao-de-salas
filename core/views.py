from django.shortcuts import render, redirect
from .models import Sala
from .forms import SalaForm

def sala_list(request):
    salas = Sala.objects.all()
    return render(request, 'core/sala_list.html', {'salas': salas})

def sala_create(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sala_list')
    else:
        form = SalaForm()
    return render(request, 'core/sala_form.html', {'form': form})
