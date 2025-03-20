from django.db import models
from django.contrib.auth.models import AbstractUser
from colorfield.fields import ColorField


    
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

class User(AbstractUser):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    class Meta:
         
        permissions = (
            ("empresa_admin","Puede crear y editar bitacoras de su empresa."),)

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
    
