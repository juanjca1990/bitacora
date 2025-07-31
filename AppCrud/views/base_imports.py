# Base imports for all view files
from collections import defaultdict
import datetime
import locale
import json
import io
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django import forms
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from django.contrib import messages
from django.core.mail import send_mail
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from AppCrud.models import Estado, Job, Contacto, Aviso, Bitacora, Empresa, Registro, Servidor, User, VisualEmpresa
from AppCrud.forms import (JobForm, EmailForm, ContactoForm, AvisoForm, BitacoraForm, 
                           RegistroForm, RegistroUsuarioForm, ServidorForm, UserEditForm, 
                           EmpresaVisualForm, AsignarAdminForm)
