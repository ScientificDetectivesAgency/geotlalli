import os
import psycopg2
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# --- CONFIGURATION ---
DB_CONFIG = {
    "dbname": "costas",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost"
}

SOURCE_DIR = r"C:\Users\eurekastein\OneDrive\Documentos\01_PROYECTOS_ACTUALES\GEOEMPRENDIMIENTO\datos\Fotos GPS"
DEST_DIR = r"C:\Users\eurekastein\OneDrive\Documentos\01_PROYECTOS_ACTUALES\GEOEMPRENDIMIENTO\fotos\fotos"

# --- HELPERS ---
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
    try:
        gps_latitude = gps_info.get("GPSLatitude")
        gps_latitude_ref = gps_info.get("GPSLatitudeRef")
        gps_longitude = gps_info.get("GPSLongitude")
        gps_longitude_ref = gps_info.get("GPSLongitudeRef")

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N": lat = -lat
            lon = convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E": lon = -lon
            return lat, lon
    except:
        pass
    return None, None

# --- MAIN ---
def main():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Connected to DB.")

        files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(('.jpg', '.jpeg'))]
        total = len(files)
        print(f"Found {total} photos to process.")

        count = 0
        for filename in files:
            source_path = os.path.join(SOURCE_DIR, filename)
            webp_name = os.path.splitext(filename)[0] + ".webp"
            dest_path = os.path.join(DEST_DIR, webp_name)

            try:
                with Image.open(source_path) as img:
                    # 1. Extract GPS
                    exif = img._getexif()
                    gps_info = get_gps_data(exif)
                    lat, lon = get_lat_lon(gps_info)

                    if lat is None or lon is None:
                        print(f"Skipping {filename}: No GPS data.")
                        continue

                    # 2. Convert to WebP
                    if not os.path.exists(dest_path):
                        img.save(dest_path, "webp", optimize=True, quality=80)

                    # 3. Database Update with Spatial Join
                    # We look for the nearest 'cod_name' from datos.tc_qr_n3
                    cur.execute("""
                        INSERT INTO datos.fotos_trasladadas (nombre_archivo, latitud, longitud, geom, cod_name)
                        SELECT %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), cod_name
                        FROM datos.tc_qr_n3
                        ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                        LIMIT 1
                    """, (webp_name, lat, lon, lon, lat, lon, lat))
                    
                    count += 1
                    if count % 20 == 0:
                        print(f"Processed {count}/{total} photos...")
                        conn.commit()

            except Exception as e:
                print(f"Error processing {filename}: {e}")

        conn.commit()
        print(f"\nSUCCESS: Processed {count} photos.")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Fatal Error: {e}")

if __name__ == "__main__":
    main()
