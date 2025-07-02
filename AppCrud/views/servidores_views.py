from .base_imports import *

@login_required
def servidores(request):
    empresa = request.user.empresa
    servidores = Servidor.objects.filter(empresa=empresa)
    servidores_con_registros = []
    for servidor in servidores:
        registros = Registro.objects.filter(servidor=servidor)
        servidores_con_registros.append({
            'servidor': servidor,
            'registros': registros
        })
    return render(request, "AppCrud/servidores.html", {"servidores_con_registros": servidores_con_registros})

@login_required
def servidorForm(request):
    if request.method == 'POST':
        form = ServidorForm(request.POST)
        if form.is_valid():
            servidor = form.save(commit=False)
            servidor.empresa = request.user.empresa  # Asigna la empresa del usuario
            servidor.save()
            form.save_m2m()
            return redirect('servidores')
    else:
        form = ServidorForm()
    return render(request, "AppCrud/servidorForm.html", {"formulario": form})

@login_required
def borrarServidor(request, id):
    servidor = Servidor.objects.get(id=id)
    servidor.delete()
    return redirect('servidores')

@login_required
def quitar_registro_servidor(request, servidor_id, registro_id):
    servidor = Servidor.objects.get(id=servidor_id)
    registro = Registro.objects.get(id=registro_id)
    servidor.registos.remove(registro)
    return redirect('servidores')

@login_required
def editar_servidor(request, servidor_id):
    servidor = Servidor.objects.get(id=servidor_id)
    if request.method == 'POST':
        form = ServidorForm(request.POST, instance=servidor)
        if form.is_valid():
            form.save()
            return redirect('servidores')  # Cambia 'servidores' por el nombre de tu vista de lista
    else:
        form = ServidorForm(instance=servidor)
    return render(request, 'AppCrud/editarServidor.html', {'form': form, 'servidor': servidor})
