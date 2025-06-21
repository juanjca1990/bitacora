from django.contrib.auth import get_user_model

def lista_usuarios(request):
    User = get_user_model()
    # Solo superusers o staff
    return {'users': User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True)}