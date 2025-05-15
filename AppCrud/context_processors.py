from django.contrib.auth import get_user_model

def lista_usuarios(request):
    User = get_user_model()
    return {'users': User.objects.all()}