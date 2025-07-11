from django import forms
from AppCrud.models import Contacto, Job, User, Empresa
from django.contrib.auth.forms import  UserCreationForm
from django.forms import ModelForm, formsets
from .models import Empresa, Registro, Servidor, VisualEmpresa, Contacto, Job

class JobForm(forms.Form):
    empresa = forms.ModelChoiceField(queryset=Empresa.objects.none(), label="Empresa", to_field_name="nombre",
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    ambiente = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # retrieve the user from kwargs
        super(JobForm, self).__init__(*args, **kwargs)
        if user and user.is_superuser:
            self.fields['empresa'].queryset = Empresa.objects.all()
        elif user and user.empresa:
            user_empresa = user.empresa
            self.fields['empresa'].queryset = Empresa.objects.filter(nombre=user_empresa)

class EmpresaVisualForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre']

    colorPrimario = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color'}),
        required=False
    )
    colorSecundario = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color'}),
        required=False
    )
    logo = forms.ImageField(required=True)  # Cambiado a obligatorio


class ContactoForm(forms.Form):
    
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
        label='',
        max_length=255,
    )
    mail = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        label='',
        max_length=255,
    )
    empresa = forms.ModelChoiceField(queryset=Empresa.objects.none(), label="Empresa", to_field_name="nombre",
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
        label='',
        max_length=255,
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # retrieve the user from kwargs
        super(ContactoForm, self).__init__(*args, **kwargs)
        if user and user.is_superuser:
            self.fields['empresa'].queryset = Empresa.objects.all()
        elif user and user.empresa:
            user_empresa = user.empresa
            self.fields['empresa'].queryset = Empresa.objects.filter(nombre=user_empresa)

class AvisoForm(forms.Form):
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.none(),
        label="Empresa",
        to_field_name="nombre",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    ambiente = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255,
    )
    inicio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fecha de inicio'}),
        max_length=255,
    )
    contacto = forms.ModelChoiceField(
        queryset=Contacto.objects.all(),
        label="Contacto",
        to_field_name="nombre",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    job = forms.ModelChoiceField(
        queryset=Job.objects.none(),
        label="Job",
        to_field_name="nombre",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # retrieve the user from kwargs
        super(AvisoForm, self).__init__(*args, **kwargs)
        if user and user.is_superuser:
            self.fields['empresa'].queryset = Empresa.objects.all()
            self.fields['job'].queryset = Job.objects.all()
        elif user and user.empresa:
            user_empresa = user.empresa
            self.fields['empresa'].queryset = Empresa.objects.filter(nombre=user_empresa)
            self.fields['job'].queryset = Job.objects.filter(empresa=user_empresa)


class BitacoraForm(forms.Form):
    job = forms.ModelChoiceField(
        queryset=Job.objects.none(),
        label="Job",
        widget=forms.Select(attrs={'id':'id_job','class': 'form-control'}),
    )
    periodo = forms.ChoiceField(choices=(('Diario','Diario'),('Semanal','Semanal'),('Monthly','Mensual'),('Anual','Anual'),('Otro','Otro')), widget=forms.RadioSelect(attrs={'id': 'id_periodo'}))
    other_periodo = forms.CharField(required=False, widget=forms.TextInput(attrs={'id': 'id_other_periodo', 'disabled': 'disabled'}))
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'id':'id_descripcion','class': 'form-control', 'rows': 3}),
    )
    dias = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Lunes'}),
        max_length=255,
    )
    inicio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hora de inicio'}),
        max_length=255,
    )
    impacto = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Impacto si cancela'}),
    )
    tiempo_estimado = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3:00'}),
        max_length=255,
    )
    si_cancela = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '¿Que hacer si cancela?'}),
        max_length=255,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # retrieve the user from kwargs
        super(BitacoraForm, self).__init__(*args, **kwargs)
        if user and user.is_superuser:
            self.fields['job'].queryset = Job.objects.all()
        elif user and user.empresa:
            user_empresa = user.empresa
            self.fields['job'].queryset = Job.objects.filter(empresa__nombre=user_empresa)
        periodo_value = self.initial.get('periodo', '')  # Get the initial value of 'periodo' field
        periodo_choices = [choice[0] for choice in self.fields['periodo'].choices]
        if periodo_value not in periodo_choices:
            self.initial['other_periodo'] = periodo_value
            
            self.initial['periodo'] = periodo_value
            self.fields['other_periodo'].widget.attrs['disabled'] = False  # Enable 'other_periodo' field
            


class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(),
        label="Empresa",
        to_field_name="nombre",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False  # Hacer opcional
    )
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "empresa"]
        help_texts = {k: "" for k in fields}

class UserEditForm(UserCreationForm):
    email = forms.EmailField(label="Email Usuario", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='Modificar Nombre', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Modificar Apellido', widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ["email", "password1", "password2", "first_name", "last_name"]
        help_texts = {k: "" for k in fields}

class EmailForm(forms.Form):
    asunto = forms.CharField(
        label="Asunto", 
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mensaje = forms.CharField(
        label="Mensaje", 
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    
    
    
class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
        }
        
class ServidorForm(forms.ModelForm):
    class Meta:
        model = Servidor
        fields = ['nombre', 'registos']  # Quita 'empresa' de los fields
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'registos': forms.CheckboxSelectMultiple(),
        }

class AsignarAdminForm(forms.Form):
    usuario = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Usuario",
        widget=forms.Select(attrs={'class': 'form-control select2'})  # Puedes usar select2 para mejor búsqueda
    )
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(),
        label="Empresa",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


