import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoviewer.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'datos' AND table_name = 'subcel_qr_n2' ORDER BY ordinal_position")
    columns = cursor.fetchall()
    print("Columns for datos.subcel_qr_n2:")
    for col in columns:
        print(f" - {col[0]}: {col[1]}")
