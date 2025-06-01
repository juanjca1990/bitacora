from django.db import models
from django.contrib.auth.models import AbstractUser
from colorfield.fields import ColorField
from django.utils.timezone import now


    
class VisualEmpresa(models.Model):
    colorPrimario = ColorField(default='#FF0000')
    colorSecundario = ColorField( default='#FF0000')
    logo = models.ImageField(upload_to = "images/")
    def __str__(self) -> str:
        return "Visual"
    
class Empresa(models.Model):
    nombre = models.CharField(max_length=40)
    visual_empresa = models.ForeignKey(VisualEmpresa, on_delete=models.CASCADE)
    def __str__(self) -> str:
        return self.nombre
    
class Registro(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.nombre} - {self.descripcion}"
    
class Servidor(models.Model):
    nombre = models.CharField(max_length=100)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="servidores")
    registos = models.ManyToManyField(Registro, blank=True)
    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre} - {self.registos.all()}"
    
class Estado(models.Model):
    OPCIONES_VERIFICACION = [
        ('desconocido', 'desconocido'),
        ('bien', 'Bien'),
        ('fallo', 'Fallo'),
        ('no_verificado', 'No Verificado'),
    ]
    tipo_verificacion = models.CharField(max_length=20, choices=OPCIONES_VERIFICACION, default='none')
    descripcion = models.TextField(blank=True, null=True)
    registro_verificado = models.ForeignKey(Registro, on_delete=models.CASCADE, related_name="estados")
    fecha = models.DateField(default=now)
    servidor = models.ForeignKey(Servidor, on_delete=models.CASCADE, related_name="estados")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="estados")
    class Meta:
        unique_together = ('registro_verificado', 'fecha', 'empresa', 'servidor') # registro por fecha y por empresa

    def __str__(self):
        return f"{self.registro_verificado.nombre} - {self.tipo_verificacion} - {self.fecha}"

class User(AbstractUser):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)  # Permitir nulos
    class Meta:
         
        permissions = (
            ("empresa_admin", "Puede crear y editar bitacoras de su empresa."),
        )

# Create your models here.
class Job(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    ambiente = models.CharField(max_length=40)
    nombre = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=80, blank=True)
    def __str__(self) -> str:
        
        return self.nombre

class Contacto(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=40)
    mail = models.CharField(max_length=40)
    telefono = models.CharField(max_length=40)
    def __str__(self) -> str:
        return self.nombre

class Aviso(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    ambiente = models.CharField(max_length=40)
    inicio = models.CharField(max_length=40)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE)
    def __str__(self) -> str:
        return f"{ self.inicio} -- {self.contacto}"

class Bitacora(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    ambiente = models.CharField(max_length=40)
    periodo = models.CharField(max_length=40)
    dias = models.CharField(max_length=40)
    inicio = models.CharField(max_length=40)
    impacto = models.CharField(max_length=40)
    tiempo_estimado = models.CharField(max_length=40)
    si_cancela = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=40)
    def __str__(self) -> str:
        return self.inicio



