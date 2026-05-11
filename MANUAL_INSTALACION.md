# Manual de Instalación y Despliegue - Visor Geográfico Costero

Este manual proporciona las instrucciones necesarias para instalar el proyecto desde cero en ambientes de desarrollo (Windows) y producción (Linux).

---

## 1. Prerrequisitos Comunes

- **Python**: Versión 3.10 o superior.
- **PostgreSQL**: Versión 15 o superior.
- **PostGIS**: Extensión espacial para PostgreSQL instalada y activada.

---

## 2. Configuración en Ambiente de Desarrollo (Windows)

Sigue estos pasos para configurar el proyecto en una máquina local con Windows.

### A. Instalación de Dependencias del Sistema
1. **Instalar PostgreSQL + PostGIS**: Descarga el instalador de [EnterpriseDB](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads). Asegúrate de incluir el componente **Application Stack Builder** para instalar la extensión **PostGIS** después de instalar Postgres.
2. **Instalar OSGeo4W**: Requerido por GeoDjango para manejar datos espaciales.
   - Descarga el instalador desde [osgeo.org](https://www.osgeo.org/projects/osgeo4w/).
   - Selecciona "Express Desktop Install" e incluye **GDAL**.
   - Por defecto se instalará en `C:\OSGeo4W`.

### B. Restauración de la Base de Datos
1. Crea una base de datos llamada `costas` en tu servidor local de Postgres.
2. Abre una terminal y habilita la extensión espacial:
   ```sql
   CREATE EXTENSION postgis;
   ```
3. Restaura el archivo `playas.tar` proporcionado:
   ```bash
   pg_restore -U postgres -d costas -v "ruta/hacia/playas.tar"
   ```

### C. Configuración del Proyecto
1. Clona el repositorio y entra al directorio:
   ```bash
   cd GEOEMPRENDIMIENTO
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### D. Verificación de Rutas GeoDjango
En `geoviewer/settings.py`, asegúrate de que las rutas a los binarios de OSGeo4W sean correctas para tu usuario:
```python
os.environ['PATH'] = r'C:\TUPATH\OSGeo4W\bin;' + os.environ.get('PATH', '')
GDAL_LIBRARY_PATH = r'C:\TUPATH\OSGeo4W\bin\gdalXXX.dll'
GEOS_LIBRARY_PATH = r'C:\TUPATH\OSGeo4W\bin\geos_c.dll'
```

---

## 3. Despliegue en Ambiente de Producción (Linux / Ubuntu)

Para producción, recomendamos un stack basado en **Nginx** y **Gunicorn**.

### A. Instalación de Librerías del Sistema
```bash
sudo apt update
sudo apt install python3-pip python3-venv libpq-dev postgresql postgresql-contrib postgis gdal-bin libgdal-dev
```

### B. Configuración de Gunicorn (Systemd)
Crea un archivo de servicio en `/etc/systemd/system/gunicorn.service`:
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=tu_usuario
Group=www-data
WorkingDirectory=/home/tu_usuario/GEOEMPRENDIMIENTO
ExecStart=/home/tu_usuario/GEOEMPRENDIMIENTO/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          geoviewer.wsgi:application

[Install]
WantedBy=multi-user.target
```

### C. Configuración de Nginx
Crea un archivo de configuración en `/etc/nginx/sites-available/geoviewer`:
```nginx
server {
    listen 80;
    server_name tu_dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/tu_usuario/GEOEMPRENDIMIENTO;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

---

## 4. Notas de Seguridad Críticas
Para producción, **siempre** actualiza los siguientes valores en `settings.py` (o usa un archivo `.env`):
- `DEBUG = False`
- `ALLOWED_HOSTS = ['tu_dominio.com']`
- `SECRET_KEY`: Genera una nueva clave única.
- **Base de Datos**: Usa credenciales seguras (no 'postgres'/'postgres').

---

## 5. Contacto y Soporte
Para actualizaciones de la lógica del mapa o estilos CSS, referirse a los archivos:
- `static/css/styles.css`: Estilos visuales.
- `mapapp/templates/index.html`: Lógica de Leaflet y markers.
