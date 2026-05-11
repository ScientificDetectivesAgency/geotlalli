import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoviewer.settings')
django.setup()

from mapapp.models import CelQrN1

celda = CelQrN1.objects.first()
if celda:
    print(f"C_eros: {celda.c_eros}")
    print(f"Protcons: {celda.protcons}")
    print(f"Aprovsos: {celda.aprovsos}")
else:
    print("No celdas found")
