from .base_imports import *

def obtener_fecha(request):
    hoy = now().date()
    vista = request.GET.get('vista', 'semana')  # Por defecto vista semanal
    url = reverse('monitoreo', args=[hoy.strftime("%Y-%m-%d")])
    params = f"?vista={vista}"
    return redirect(url + params)

def cambiarFechaMonitor_admin(request):
    mes = int(request.GET.get('mes', date.today().month))
    anio = int(request.GET.get('anio', date.today().year))
    empresa_id = request.GET.get('empresa_id')
    servidor_id = request.GET.get('servidor_id')
    admin = request.GET.get('admin')

    nueva_fecha = date(anio, mes, 1)

    url = reverse('monitoreo_admin', args=[nueva_fecha.strftime("%Y-%m-%d")])
    params = f"?empresa_id={empresa_id}"
    if servidor_id:
        params += f"&servidor_id={servidor_id}"
    return redirect(url + params)

def cambiarFechaMonitor_otros(request):
    mes = int(request.GET.get('mes', date.today().month))
    anio = int(request.GET.get('anio', date.today().year))
    empresa_id = request.GET.get('empresa_id')
    servidor_id = request.GET.get('servidor_id')
    admin = request.GET.get('admin')

    nueva_fecha = date(anio, mes, 1)

    url = reverse('monitoreo', args=[nueva_fecha.strftime("%Y-%m-%d")])
    params = ""
    if servidor_id:
        params = f"?servidor_id={servidor_id}"
    return redirect(url + params)

def cambiarSemanaMonitor_admin(request):
    fecha_actual = request.GET.get('fecha')
    direccion = request.GET.get('direccion')  # 'anterior' o 'siguiente'
    empresa_id = request.GET.get('empresa_id')
    servidor_id = request.GET.get('servidor_id')
    
    if fecha_actual:
        fecha_base = datetime.strptime(fecha_actual, "%Y-%m-%d").date()
    else:
        fecha_base = date.today()
    
    if direccion == 'anterior':
        nueva_fecha = fecha_base - timedelta(weeks=1)
    elif direccion == 'siguiente':
        nueva_fecha = fecha_base + timedelta(weeks=1)
    else:
        nueva_fecha = fecha_base
    
    url = reverse('monitoreo_admin', args=[nueva_fecha.strftime("%Y-%m-%d")])
    params = f"?empresa_id={empresa_id}&vista=semana"
    if servidor_id:
        params += f"&servidor_id={servidor_id}"
    return redirect(url + params)

def cambiarSemanaMonitor_otros(request):
    fecha_actual = request.GET.get('fecha')
    direccion = request.GET.get('direccion')  # 'anterior' o 'siguiente'
    servidor_id = request.GET.get('servidor_id')
    
    if fecha_actual:
        fecha_base = datetime.strptime(fecha_actual, "%Y-%m-%d").date()
    else:
        fecha_base = date.today()
    
    if direccion == 'anterior':
        nueva_fecha = fecha_base - timedelta(weeks=1)
    elif direccion == 'siguiente':
        nueva_fecha = fecha_base + timedelta(weeks=1)
    else:
        nueva_fecha = fecha_base
    
    url = reverse('monitoreo', args=[nueva_fecha.strftime("%Y-%m-%d")])
    params = "?vista=semana"
    if servidor_id:
        params += f"&servidor_id={servidor_id}"
    return redirect(url + params)

def cambiarMesMonitor_admin(request):
    mes = int(request.GET.get('mes', date.today().month))
    anio = int(request.GET.get('anio', date.today().year))
    empresa_id = request.GET.get('empresa_id')
    servidor_id = request.GET.get('servidor_id')
    
    nueva_fecha = date(anio, mes, 1)

    url = reverse('monitoreo_admin', args=[nueva_fecha.strftime("%Y-%m-%d")])
    params = f"?empresa_id={empresa_id}"
    if servidor_id:
        params += f"&servidor_id={servidor_id}"
    return redirect(url + params)
    
def cambiarMesMonitor_otros(request):
    mes = int(request.GET.get('mes', date.today().month))
    anio = int(request.GET.get('anio', date.today().year))
    servidor_id = request.GET.get('servidor_id')
    
    nueva_fecha = date(anio, mes, 1)

    url = reverse('monitoreo', args=[nueva_fecha.strftime("%Y-%m-%d")])
    params = ""
    if servidor_id:
        params = f"?servidor_id={servidor_id}"
    return redirect(url + params)

def obtener_fecha_monitor_admin(request):
    hoy = now().date()
    vista = request.GET.get('vista', 'semana')  # Por defecto vista semanal
    url = reverse('monitoreo_admin', args=[hoy.strftime("%Y-%m-%d")])
    params = f"?vista={vista}"
    return redirect(url + params)

def habilitar_deshabilitar_edicion_admin(request):
    # Obtener la fecha actual desde el referer o usar fecha de hoy por defecto
    fecha_actual = request.GET.get('fecha', date.today().strftime("%Y-%m-%d"))
    empresa_id = request.GET.get('empresa_id')
    servidor_id = request.GET.get('servidor_id')
    
    if request.session["bloquear_edicion"] == True:
        print("Edición habilitada")
        request.session["bloquear_edicion"] = False
        messages.success(request, "Edición habilitada.")
    else:
        request.session["bloquear_edicion"] = True
        print("Edición deshabilitada")
        messages.warning(request, "Edición deshabilitada. No se pueden modificar los estados.")
    
    # Construir la URL con los parámetros preservados
    url = reverse('monitoreo_admin', args=[fecha_actual])
    params = "?vista=semana"
    if empresa_id:
        params += f"&empresa_id={empresa_id}"
    if servidor_id:
        params += f"&servidor_id={servidor_id}"
    
    return redirect(url + params)

def habilitar_deshabilitar_edicion_otros(request):
    # Obtener la fecha actual desde el referer o usar fecha de hoy por defecto
    fecha_actual = request.GET.get('fecha', date.today().strftime("%Y-%m-%d"))
    servidor_id = request.GET.get('servidor_id')
    
    if request.session["bloquear_edicion"] == True:
        print("Edición habilitada")
        request.session["bloquear_edicion"] = False
        messages.success(request, "Edición habilitada.")
    else:
        request.session["bloquear_edicion"] = True
        print("Edición deshabilitada")
        messages.warning(request, "Edición deshabilitada. No se pueden modificar los estados.")

    # Construir la URL con los parámetros preservados
    url = reverse('monitoreo', args=[fecha_actual])
    params = "?vista=semana"
    if servidor_id:
        params += f"&servidor_id={servidor_id}"
    
    return redirect(url + params)

@login_required
def monitoreo_admin(request, hoy):
    empresas = Empresa.objects.all().order_by('nombre')
    empresa_id = request.GET.get('empresa_id')
    # Siempre usar vista semanal
    vista_tipo = 'semana'
    
    if empresa_id:
        empresa = Empresa.objects.get(id=empresa_id)
    else:
        empresa = empresas.first()
        empresa_id = empresa.id if empresa else None

    # Obtén todos los servidores de la empresa seleccionada
    todos_los_servidores = Servidor.objects.filter(empresa=empresa)
    servidor_id = request.GET.get('servidor_id')

    # Si no hay servidor_id o no existe en la empresa actual, selecciona el primero
    if not servidor_id:
        if todos_los_servidores.exists():
            servidor_id = todos_los_servidores.first().id
            servidores = todos_los_servidores.filter(id=servidor_id)
        else:
            servidores = todos_los_servidores.none()
            servidor_id = None
    elif not todos_los_servidores.filter(id=servidor_id).exists():
        # Si el servidor_id no pertenece a la empresa actual, selecciona el primero
        if todos_los_servidores.exists():
            servidor_id = todos_los_servidores.first().id
            servidores = todos_los_servidores.filter(id=servidor_id)
        else:
            servidores = todos_los_servidores.none()
            servidor_id = None
    else:
        servidores = todos_los_servidores.filter(id=servidor_id)
        servidor_id = int(servidor_id)

    hoy = datetime.strptime(hoy, "%Y-%m-%d").date()
    
    # Siempre vista semanal
    # Obtener el inicio de la semana (lunes)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    dias_periodo = [inicio_semana + timedelta(days=i) for i in range(7)]
    
    # Calcular semana anterior y siguiente
    semana_anterior = inicio_semana - timedelta(weeks=1)
    semana_siguiente = inicio_semana + timedelta(weeks=1)
    
    # Calcular mes anterior y siguiente para navegación de meses
    # Usamos la fecha actual (hoy) para calcular los meses, no el inicio de semana
    fecha_actual_mes = hoy.replace(day=1)
    fecha_mes_anterior = fecha_actual_mes - relativedelta(months=1)
    fecha_mes_siguiente = fecha_actual_mes + relativedelta(months=1)
    
    mes_actual = hoy.month
    anio_actual = hoy.year
    mes_anterior = fecha_mes_anterior.month
    anio_anterior = fecha_mes_anterior.year
    mes_siguiente = fecha_mes_siguiente.month
    anio_siguiente = fecha_mes_siguiente.year
    
    # Obtener nombre del mes en español
    meses_nombres = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    mes_nombre = meses_nombres.get(mes_actual, 'Mes')

    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '')

    dias_semana = [dia.strftime('%A')[0].upper() for dia in dias_periodo]

    estados = Estado.objects.filter(fecha__range=(inicio_semana, fin_semana), empresa=empresa).select_related('registro_verificado')

    estados_dict = defaultdict(lambda: defaultdict(dict))
    for estado in estados:
        estados_dict[estado.servidor.id][estado.registro_verificado.id][estado.fecha] = estado

    registros_por_servidor = defaultdict(list)
    for servidor in servidores:
        for registro in servidor.registos.all():
            fila = {
                "registro": registro,
                "estados": [
                    estados_dict[servidor.id][registro.id].get(dia, None)
                    for dia in dias_periodo
                ]
            }
            registros_por_servidor[servidor].append(fila)
    registros_por_servidor = dict(sorted(registros_por_servidor.items(), key=lambda x: x[0].nombre))
    
    # Verifica si la edición está bloqueada
    if request.session["bloquear_edicion"] == True:
        hoy_real = now().date()
        dias_no_modificables = [
            dia.weekday() in [5, 6] or dia <= (hoy_real - timedelta(days=7))
            for dia in dias_periodo
        ]
    else:
        dias_no_modificables = [dia.weekday() in [5, 6] for dia in dias_periodo]
    
    dias = list(zip(dias_periodo, dias_semana))

    return render(request, "AppCrud/monitor_admin.html", {
        "empresas": empresas,
        "empresa": empresa,
        "servidores": todos_los_servidores,  # Para el select, muestra todos los servidores de la empresa
        "servidor_id": servidor_id,
        "registros_por_servidor": registros_por_servidor,
        "dias": dias,
        "dias_semana": dias_semana,
        "dias_no_modificables": dias_no_modificables,
        "empresa_id": int(empresa_id) if empresa_id else None,
        "vista_tipo": vista_tipo,
        "dias_periodo": dias_periodo,
        "inicio_semana": inicio_semana,
        "fin_semana": fin_semana,
        "semana_anterior": semana_anterior,
        "semana_siguiente": semana_siguiente,
        "fecha_actual": hoy,
        "fecha_hoy": date.today(),
        "mes_anterior": mes_anterior,
        "anio_anterior": anio_anterior,
        "mes_siguiente": mes_siguiente,
        "anio_siguiente": anio_siguiente,
        "mes_actual": mes_actual,
        "anio_actual": anio_actual,
        "mes_nombre": mes_nombre,
    })

@login_required
def monitoreo(request, hoy):
    usuario = request.user
    if not usuario.empresa:
        return render(request, "AppCrud/monitoreo.html", {
            "error": "No tiene empresa asociada. Contacte al administrador."
        })

    empresa = Empresa.objects.get(nombre=usuario.empresa.nombre)
    servidores = Servidor.objects.filter(empresa=empresa)

    servidor_id = request.GET.get('servidor_id')
    if not servidor_id and servidores.exists():
        servidor_id = servidores.first().id
    if servidor_id:
        servidores = servidores.filter(id=servidor_id)

    hoy = datetime.strptime(hoy, "%Y-%m-%d").date()
    
    # Siempre vista semanal - Obtener el inicio de la semana (lunes)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    dias_periodo = [inicio_semana + timedelta(days=i) for i in range(7)]
    
    # Calcular semana anterior y siguiente
    semana_anterior = inicio_semana - timedelta(weeks=1)
    semana_siguiente = inicio_semana + timedelta(weeks=1)
    
    # Calcular mes anterior y siguiente para navegación de meses
    fecha_actual_mes = hoy.replace(day=1)
    fecha_mes_anterior = fecha_actual_mes - relativedelta(months=1)
    fecha_mes_siguiente = fecha_actual_mes + relativedelta(months=1)
    
    mes_actual = hoy.month
    anio_actual = hoy.year
    mes_anterior = fecha_mes_anterior.month
    anio_anterior = fecha_mes_anterior.year
    mes_siguiente = fecha_mes_siguiente.month
    anio_siguiente = fecha_mes_siguiente.year
    
    # Obtener nombre del mes en español
    meses_nombres = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    mes_nombre = meses_nombres.get(mes_actual, 'Mes')

    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '')

    dias_semana = [dia.strftime('%A')[0].upper() for dia in dias_periodo]

    estados = Estado.objects.filter(fecha__range=(inicio_semana, fin_semana), empresa=empresa).select_related('registro_verificado')

    estados_dict = defaultdict(lambda: defaultdict(dict))
    for estado in estados:
        estados_dict[estado.servidor.id][estado.registro_verificado.id][estado.fecha] = estado

    registros_por_servidor = defaultdict(list)

    for servidor in servidores:
        for registro in servidor.registos.all():
            fila = {
                "registro": registro,
                "estados": [
                    estados_dict[servidor.id][registro.id].get(dia, None)
                    for dia in dias_periodo
                ]
            }
            registros_por_servidor[servidor].append(fila)

    registros_por_servidor = dict(sorted(registros_por_servidor.items(), key=lambda x: x[0].nombre))

    # Verifica si la edición está bloqueada
    if request.session.get("bloquear_edicion", False):
        hoy_real = now().date()
        dias_no_modificables = [
            dia.weekday() in [5, 6] or dia <= (hoy_real - timedelta(days=7))
            for dia in dias_periodo
        ]
    else:
        dias_no_modificables = [dia.weekday() in [5, 6] for dia in dias_periodo]

    return render(request, "AppCrud/monitoreo.html", {
        "registros_por_servidor": registros_por_servidor,
        "dias_periodo": dias_periodo,
        "dias_semana": dias_semana,
        "dias_no_modificables": dias_no_modificables,
        "fecha_actual": hoy,
        "fecha_hoy": date.today(),
        "inicio_semana": inicio_semana,
        "fin_semana": fin_semana,
        "mes_actual": mes_actual,
        "anio_actual": anio_actual,
        "mes_anterior": mes_anterior,
        "anio_anterior": anio_anterior,
        "mes_siguiente": mes_siguiente,
        "anio_siguiente": anio_siguiente,
        "mes_nombre": mes_nombre,
        "empresa": empresa,
        "servidores": Servidor.objects.filter(empresa=empresa),
        "servidor_id": int(servidor_id) if servidor_id else None,
    })

@csrf_exempt
def registrarEstado(request):
    if request.method == "POST":
        try:
            print("Estoy en el try de registrarEstado")
            data = json.loads(request.body)
            registro_id = data.get("registro_id")
            print("registro_id:", registro_id)
            fecha = data.get("fecha")
            verificacion = data.get("tipo_verificacion")
            print("tipo verificacion:", verificacion)
            servidor_id = data.get("servidor_id")
            print("servidor_id:", servidor_id)
            empresa_id = data.get("empresa_id")
            print("empresa_id:", empresa_id)

            # Obtener objetos
            registro = Registro.objects.get(id=registro_id)
            servidor = Servidor.objects.get(id=servidor_id)
            empresa = Empresa.objects.get(id=empresa_id)
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()

            # Buscar o crear estado
            estado, created = Estado.objects.get_or_create(
                registro_verificado=registro,
                servidor=servidor,
                empresa=empresa,
                fecha=fecha_obj,
                defaults={
                    'tipo_verificacion': verificacion,
                    'descripcion': ''
                }
            )

            if not created:
                estado.tipo_verificacion = verificacion
                estado.save()

            return JsonResponse({"success": True})

        except Exception as e:
            print(f"Error en registrarEstado: {e}")
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})

@csrf_exempt
def registrarDescripcion(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            registro_id = data.get("registro_id")
            fecha = data.get("fecha")
            descripcion = data.get("descripcion")
            servidor_id = data.get("servidor_id")
            empresa_id = data.get("empresa_id")

            # Obtener objetos
            registro = Registro.objects.get(id=registro_id)
            servidor = Servidor.objects.get(id=servidor_id)
            empresa = Empresa.objects.get(id=empresa_id)
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()

            # Buscar o crear estado
            estado, created = Estado.objects.get_or_create(
                registro_verificado=registro,
                servidor=servidor,
                empresa=empresa,
                fecha=fecha_obj,
                defaults={
                    'tipo_verificacion': 'exito',
                    'descripcion': descripcion
                }
            )

            if not created:
                estado.descripcion = descripcion
                estado.save()

            return JsonResponse({"success": True})

        except Exception as e:
            print(f"Error en registrarDescripcion: {e}")
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})

def imprimirRegistroMes(request, mes, anio, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    servidores = Servidor.objects.filter(empresa=empresa)
    registros = Registro.objects.filter(servidor__in=servidores)

    # Filtrar estados with "fallo" o que tengan algún comentario (descripcion no vacía)
    estados = Estado.objects.filter(
        registro_verificado__in=registros,
        fecha__year=anio,
        fecha__month=mes
    ).filter(
        Q(tipo_verificacion="fallo") | (~Q(descripcion__isnull=True) & ~Q(descripcion__exact=""))
    ).select_related('registro_verificado', 'servidor')

    # Ordenar por servidor, luego por registro y luego por fecha
    estados = estados.order_by('servidor__nombre', 'registro_verificado__nombre', 'fecha')

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)

    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleTitle = styles["Title"]

    # Título con el nombre de la empresa
    elements = [Paragraph(str(empresa.nombre), styleTitle), Spacer(1, 12)]

    data = [["Servidor", "Registro", "Descripción", "Comentario", "Estado", "Fecha"]]

    for estado in estados:
        data.append([
            estado.servidor.nombre,
            estado.registro_verificado.nombre,
            estado.registro_verificado.descripcion,
            estado.descripcion or "",
            estado.tipo_verificacion,
            estado.fecha.strftime("%d/%m/%Y")
        ])

    table = Table(data, colWidths=[80, 80, 200, 200, 80, 80])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    elements.append(table)
    pdf.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Registro_{mes}_{anio}.pdf")

def imprimirRegistroMesCompleto(request, mes, anio, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    servidores = Servidor.objects.filter(empresa=empresa)
    registros = Registro.objects.filter(servidor__in=servidores)

    # Obtener todos los estados del mes y año indicados, sin filtro
    estados = Estado.objects.filter(
        registro_verificado__in=registros,
        fecha__year=anio,
        fecha__month=mes
    ).select_related('registro_verificado', 'servidor')

    # Ordenar por servidor, luego por registro y luego por fecha
    estados = estados.order_by('servidor__nombre', 'registro_verificado__nombre', 'fecha')

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)

    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleTitle = styles["Title"]

    # Título con el nombre de la empresa
    elements = [Paragraph(f"Registro Completo - {empresa.nombre}", styleTitle), Spacer(1, 12)]

    data = [["Servidor", "Registro", "Descripción", "Comentario", "Estado", "Fecha"]]

    for estado in estados:
        data.append([
            estado.servidor.nombre,
            estado.registro_verificado.nombre,
            estado.registro_verificado.descripcion,
            estado.descripcion or "",
            estado.tipo_verificacion,
            estado.fecha.strftime("%d/%m/%Y")
        ])

    table = Table(data, colWidths=[80, 80, 200, 200, 80, 80])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    elements.append(table)
    pdf.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Registro_Completo_{mes}_{anio}.pdf")
