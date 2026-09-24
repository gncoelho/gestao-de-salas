from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, login_not_required
from django.shortcuts import redirect, render

from .forms import CadastroUsuarioForm


@login_required
def welcome(request):
    return render(request, 'webapp/welcome.html')


@login_not_required
def cadastro(request):
    if request.user.is_authenticated:
        return redirect('welcome')

    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('welcome')
    else:
        form = CadastroUsuarioForm()

    return render(request, 'webapp/cadastro.html', {'form': form})
