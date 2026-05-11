import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoviewer.settings')
django.setup()

from mapapp.models import CelQrN1
from mapapp.views import api_celda_detalle
from django.test import RequestFactory

factory = RequestFactory()
request = factory.get('/api/celdas/1/')
celda = CelQrN1.objects.first()

response = api_celda_detalle(request, celda.id)
with open('celda_response.json', 'wb') as f:
    f.write(response.content)
