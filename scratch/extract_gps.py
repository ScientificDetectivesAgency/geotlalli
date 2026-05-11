import os
import psycopg2
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_gps_data(exif_data):
    gps_info = {}
    if not exif_data:
        return None

    for tag, value in exif_data.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            for t in value:
                sub_decoded = GPSTAGS.get(t, t)
                gps_info[sub_decoded] = value[t]

    return gps_info

def convert_to_degrees(value):
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(gps_info):
    if not gps_info:
        return None, None

    lat = None
    lon = None

    gps_latitude = gps_info.get("GPSLatitude")
    gps_latitude_ref = gps_info.get("GPSLatitudeRef")
    gps_longitude = gps_info.get("GPSLongitude")
    gps_longitude_ref = gps_info.get("GPSLongitudeRef")

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = convert_to_degrees(gps_latitude)
        if gps_latitude_ref != "N":
            lat = -lat

        lon = convert_to_degrees(gps_longitude)
        if gps_longitude_ref != "E":
            lon = -lon

    return lat, lon

try:
    # DB Connection
    conn = psycopg2.connect(dbname="costas", user="postgres", password="postgres", host="localhost")
    cur = conn.cursor()

    # Create table
    cur.execute("CREATE SCHEMA IF NOT EXISTS datos;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS datos.fotos (
            id SERIAL PRIMARY KEY,
            nombre_archivo TEXT,
            latitud DOUBLE PRECISION,
            longitud DOUBLE PRECISION,
            geom GEOMETRY(Point, 4326)
        );
    """)
    conn.commit()

    photo_dir = r"c:\Users\eurekastein\OneDrive\Documentos\01_PROYECTOS_ACTUALES\GEOEMPRENDIMIENTO\fotos\fotos"

    count = 0
    for filename in os.listdir(photo_dir):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            filepath = os.path.join(photo_dir, filename)
            try:
                with Image.open(filepath) as img:
                    exif = img._getexif()
                    gps_info = get_gps_data(exif)
                    lat, lon = get_lat_lon(gps_info)
                    
                    if lat is not None and lon is not None:
                        # Check if already exists
                        cur.execute("SELECT id FROM datos.fotos WHERE nombre_archivo = %s", (filename,))
                        if cur.fetchone():
                            continue

                        cur.execute("""
                            INSERT INTO datos.fotos (nombre_archivo, latitud, longitud, geom)
                            VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                        """, (filename, lat, lon, lon, lat))
                        count += 1
                        if count % 10 == 0:
                            print(f"Processed {count} photos...")
                    else:
                        pass
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    conn.commit()
    print(f"Successfully processed {count} new photos.")
    cur.close()
    conn.close()

except Exception as e:
    print(f"DB Error: {e}")
