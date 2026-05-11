import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoviewer.settings')
django.setup()

with connection.cursor() as cur:
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='datos' AND table_name='fotos_trasladadas'")
    print("Columns:", cur.fetchall())
    
    cur.execute("SELECT * FROM datos.fotos_trasladadas LIMIT 1")
    print("Sample row:", cur.fetchone())
