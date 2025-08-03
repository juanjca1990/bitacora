from .base_imports import *

@login_required
def transacciones(request):
    registros = Registro.objects.all()
    # Buscador
    query = request.GET.get('q', '')
    if query:
        registros = registros.filter(nombre__icontains=query) | registros.filter(descripcion__icontains=query)
    # Paginación - Add explicit ordering to avoid pagination warning
    registros = registros.order_by('id')
    paginator = Paginator(registros, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "AppCrud/registros.html", {
        "registros": page_obj,
        "query": query,
    })

def registroForm(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            registro = Registro(nombre=form.cleaned_data.get("nombre"),
                               descripcion=form.cleaned_data.get("descripcion"))
            registro.save()
            return redirect('transacciones')
    else:
        form = RegistroForm()
    return render(request, "AppCrud/registroForm.html", {"formulario": form})

def borrarRegistro(request, id):
    registro = Registro.objects.get(id=id)
    registro.delete()
    return redirect('transacciones')
