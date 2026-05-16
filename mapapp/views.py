from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from .models import PuntoCosta, DatosPlayas, TcQrN3, CelQrN1, SubcelQrN2
import json
import re
import os
from django.conf import settings

# ─── Shared HTML helper functions ────────────────────────────────────────────

def card_simple(title, val):
    """White card used inside accordion-body for structured data."""
    return (
        f"<div class='data-item' style='margin-bottom:10px; background:#ffffff; "
        f"border-radius:6px; padding:8px 10px;'>"
        f"<div style='font-size: 0.65rem; color: #64748b; text-transform: uppercase; "
        f"font-weight: 600; display: block; margin-bottom: 2px; letter-spacing: 0.05em;'>{title}</div>"
        f"<div style='color: #1e293b; font-size: 0.9rem; font-weight: 400;'>{val or 'No disponible'}</div>"
        f"</div>"
    )

def text_to_list(text):
    """Convert numbered-list text to HTML list with light color for dark accordion body."""
    if not text or text.strip().lower() in ('no disponible', 'sin lineamiento', ''):
        return "<p class='empty-state-small'>No disponible</p>"
    parts = re.split(r'(?=\b\d+\.\s+)', text)
    items = [p.strip() for p in parts if p.strip()]
    if len(items) <= 1:
        items = [p.strip() for p in re.split(r'\.\s+', text) if p.strip()]
    if not items:
        return f"<p style='font-size:0.85rem; color:#f1f5f9; line-height:1.6; text-align:justify;'>{text}</p>"
    list_items = "".join(
        f"<li style='margin-bottom:15px; line-height:1.6; text-align:justify; padding-right:5px;'>{item}</li>"
        for item in items
    )
    return f"<ul style='padding:0; margin:0; font-size:0.85rem; color:#f1f5f9; list-style:none;'>{list_items}</ul>"

def lineamiento_item(title, content):
    """Nested accordion item for a single lineamiento section."""
    return f"""
        <div class="nested-accordion-item">
            <div class="nested-header">
                <span>{title}</span>
                <i class="fas fa-plus"></i>
            </div>
            <div class="nested-body">
                {text_to_list(content)}
            </div>
        </div>
        """

# ─────────────────────────────────────────────────────────────────────────────

def landing(request):
    return render(request, 'mapapp/landing.html')

def mapa(request):
    return render(request, 'mapapp/index.html')

def mapa_v2(request):
    return render(request, 'mapapp/index_v2.html')

def acerca(request):
    return render(request, 'mapapp/acerca.html')

def api_puntos(request):
    features = []
    
    # Puntos desde la tabla datos_playas (únicamente base real)
    playas = DatosPlayas.objects.all()
    for playa in playas:
        if playa.geom_init:
            features.append({
                "type": "Feature",
                "geometry": json.loads(playa.geom_init.geojson),
                "properties": {
                    "identificador": playa.id,
                    "tipo": "playa",
                    "nombre": playa.nombre_tramo or "Playa Desconocida",
                    "tipo_playa": playa.tipo_playa or "No especificado",
                }
            })
    
    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })

def api_punto_detalle(request, pk):
    punto = get_object_or_404(PuntoCosta, pk=pk)
    fotos = punto.fotos.all()
    fotos_data = [{"url": request.build_absolute_uri(f.imagen.url), "leyenda": f.leyenda or ""} for f in fotos if f.imagen]
    
    data = {
        "id": punto.id,
        "nombre": punto.nombre,
        "descripcion": punto.descripcion or "No hay descripción disponible para este punto.",
        "fotos": fotos_data
    }
    return JsonResponse(data)

def api_playa_detalle(request, pk):
    playa = get_object_or_404(DatosPlayas, pk=pk)
    
    # Construir un formato elegante con tarjetas por cada columna garantizando los títulos
    def fix_encoding(text):
        if not text: return text
        try:
            return text.encode('latin1').decode('utf-8', 'ignore')
        except:
            return str(text)

    def fmt(val): return fix_encoding(val) if val else 'No disponible'
    def card(title, val): 
        return f"<div class='data-card' style='background:#f8fafc; border:1px solid #cbd5e1; padding:12px; border-radius:8px; margin-bottom:8px;'><div class='data-title' style='font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; font-weight: 600;'>{title}</div><div class='data-val' style='font-weight: 500; color: #1e293b; font-size: 0.95rem;'>{val}</div></div>"

    detalles = f"""
    <div class="cards-container">
        {card("Nombre del tramo", fmt(playa.nombre_tramo))}
        {card("Longitud(km)", fmt(playa.long))}
        {card("Tipo geomorfológico", fmt(playa.tipo_geomorfo))}
        {card("Subtipo detallado", fmt(playa.subtipo_detallado))}
        {card("Tipo de playa", fmt(playa.tipo_playa))}
        {card("Nivel de energía", fmt(playa.nivel_energia))}
        {card("Dir. dominante transporte litoral", fmt(playa.dir_dominante))}
        {card("Magnitud estimada transporte (m³/año)", fmt(playa.mag_estimada))}
        {card("Fuentes de sedimento", fmt(playa.fuentes_sedimento))}
        {card("Sumideros de sedimento", fmt(playa.sumideros_sedimento))}
        {card("Balance sedimentario (m³/año)", fmt(playa.balance_sedimentario))}
        {card("Estructuras costeras de ingeniería", fmt(playa.est_costeras))}
        {card("Evidencia erosión/acreción", fmt(playa.ev_erosion))}
        {card("Influencia arrecifal", fmt(playa.influ_arrecifal))}
        {card("Influencia manglar/laguna", fmt(playa.influ_manglar))}
        {card("Presión antrópica", fmt(playa.pres_antropic))}
        {card("Conectividad", fmt(playa.conectividad))}
        {card("Incertidumbre", fmt(playa.incertidumbre))}
        {card("Tipo de soporte", fmt(playa.tipo_soporte))}
    </div>
    """
    
    fotos_data = []
    fotos_dir = os.path.join(settings.BASE_DIR, 'fotos', 'fotos')
    if os.path.exists(fotos_dir):
        for file in os.listdir(fotos_dir):
            if str(pk) in file and file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                fotos_data.append({
                    "url": f"/api/fotos/{file}",
                    "leyenda": f"{playa.nombre_tramo}"
                })
    
    data = {
        "id": playa.id,
        "nombre": playa.nombre_tramo or "Tramo de Playa",
        "descripcion": detalles,
        "fotos": fotos_data
    }
    return JsonResponse(data)


def api_tramos(request):
    features = []
    tramos = TcQrN3.objects.all()
    for tramo in tramos:
        if tramo.geom:
            features.append({
                "type": "Feature",
                "geometry": json.loads(tramo.geom.geojson),
                "properties": {
                    "id": tramo.id,
                    "name": tramo.name or "Tramo Sin Nombre",
                    "cod_name": tramo.cod_name or "N/A",
                    "celda": tramo.celda or "N/A",
                    "subcelda": tramo.subcelda or "N/A",
                    "tipo": tramo.tipo or "N/A",
                }
            })
    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })

def api_tramo_detalle(request, pk):
    tramo = get_object_or_404(TcQrN3, pk=pk)
    
    def card(title, val):
        return f"<div class='data-card' style='background:#f8fafc; border:1px solid #cbd5e1; padding:12px; border-radius:8px; margin-bottom:8px;'><div class='data-title' style='font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; font-weight: 600;'>{title}</div><div class='data-val' style='font-weight: 500; color: #1e293b; font-size: 0.95rem;'>{val or 'No disponible'}</div></div>"

    def card_simple(title, val):
        return f"<div class='data-item' style='margin-bottom:10px; background:#ffffff; border-radius:6px; padding:8px 10px;'><div style='font-size: 0.65rem; color: #64748b; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 2px; letter-spacing: 0.05em;'>{title}</div><div style='color: #1e293b; font-size: 0.9rem; font-weight: 400;'>{val or 'No disponible'}</div></div>"

    niveles_analisis = f"""
    <div class="section-content">
        {card_simple("Código Celda-Subcelda-Tramo", tramo.cod_name)}
        {card_simple("Celda", tramo.celda)}
        {card_simple("Subcelda", tramo.subcelda)}
    </div>
    """

    datos_generales = f"""
    <div class="section-content">
        {card_simple("Tipo", tramo.tipo)}
        {card_simple("Longitud del tramo (km)", tramo.longitud)}
        {card_simple("Acceso", tramo.ac_calle)}
        {card_simple("Tipo geomorfológico", tramo.t_geomo)}
        {card_simple("Subtipo geomorfológico", tramo.subtipo)}
        {card_simple("Tipo de playa", tramo.t_playa)}
        {card_simple("Nivel energético oleaje", tramo.n_energi)}
        {card_simple("Dirección transporte litoral", tramo.d_t_lito)}
        {card_simple("Magnitud transporte (m³/año)", tramo.magn_m3a)}
        {card_simple("Fuente sedimentaria", tramo.fuentsed)}
        {card_simple("Sumidero sedimentario", tramo.sumidero)}
        {card_simple("Balance sedimentario (m³/año)", tramo.bal_m3a)}
        {card_simple("Estado conservación", tramo.est_cost)}
        {card_simple("Tasa erosión/acreción (m/año)", tramo.eros_acr)}
        {card_simple("Infraestructura arrecifal", tramo.inf_arre)}
        {card_simple("Infraestructura manglar", tramo.inf_mang)}
        {card_simple("Presión antrópica", tramo.p_antrop)}
        {card_simple("Conectividad sedimentaria", tramo.conectiv)}
        {card_simple("Incertidumbre técnica", tramo.incertid)}
        {card_simple("Calidad de evidencia", tramo.evidenci)}
        {card_simple("Municipios", tramo.municip)}
        {card_simple("ANPs", tramo.anps)}
    </div>
    """


    lineamientos = f"""
    <div class="nested-accordion-container" style="display: flex; flex-direction: column; gap: 4px; margin-top: 10px;">
        {lineamiento_item("1. Control de Erosión", tramo.c_eros)}
        {lineamiento_item("2. Protección y Conservación", tramo.protcons)}
        {lineamiento_item("3. Aprovechamiento Sostenible", tramo.aprovsos)}
        {lineamiento_item("4. Infraestructura Costera", tramo.infcost)}
        {lineamiento_item("5. Gestión de Riesgos", tramo.gesries)}
        {lineamiento_item("6. Gobernanza y Gestión", tramo.gobgest)}
    </div>
    """

    # Obtener fotos relacionadas por cod_name (nombre y coordenadas)
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre_archivo, latitud, longitud FROM datos.fotos_trasladadas WHERE cod_name = %s", [tramo.cod_name])
        photos = [{"nombre": row[0].replace('.JPG', '.webp').replace('.jpg', '.webp'), "lat": row[1], "lon": row[2]} for row in cursor.fetchall()]

    return JsonResponse({
        "id": tramo.id,
        "name": tramo.name,
        "cod_name": tramo.cod_name,
        "niveles_analisis": niveles_analisis,
        "datos_generales": datos_generales,
        "lineamientos": lineamientos,
        "photos": photos
    })

def api_celdas(request):
    celdas = CelQrN1.objects.all()
    features = []
    for c in celdas:
        features.append({
            "type": "Feature",
            "properties": {
                "id": c.id,
                "codigo": c.codigo,
                "nombre": c.nombre
            },
            "geometry": json.loads(c.geom.geojson) if c.geom else None
        })
    return JsonResponse({"type": "FeatureCollection", "features": features})

def api_celda_detalle(request, pk):
    celda = get_object_or_404(CelQrN1, pk=pk)

    niveles_analisis = f"""
    <div class="section-content">
        {card_simple("Código de Celda", celda.codigo)}
        {card_simple("Nombre de la Celda", celda.nombre)}
        {card_simple("Número de Subceldas", celda.n_sub)}
        {card_simple("Subceldas que componen la celda", celda.subceldas)}
    </div>
    """

    datos_generales = f"""
    <div class="section-content">
        {card_simple("Número de Tramos", celda.n_tramo)}
        {card_simple("Longitud convoluta de costa (km)", celda.lon_km)}
        {card_simple("Tramos que componen la celda", celda.tramos)}
        {card_simple("Caracterización del sistema costero", celda.sistema)}
        {card_simple("Procesos sedimentarios dominantes", celda.procesos)}
        {card_simple("Estado del sistema arrecifal mesoamericano", celda.arrecife)}
        {card_simple("Estado del manglar", celda.manglar)}
        {card_simple("Asunto principal de la celda", celda.asuprinc)}
        {card_simple("Estado general de conservación", celda.estconsv)}
        {card_simple("Tipos geomorfológicos presentes", celda.t_geomos)}
        {card_simple("Municipios intersectados", celda.municip)}
        {card_simple("Áreas naturales protegidas intersectadas", celda.anps)}
    </div>
    """

    lineamientos = f"""
    <div class="nested-accordion-container" style="display: flex; flex-direction: column; gap: 4px; margin-top: 10px;">
        {lineamiento_item("1. Control de Erosión", celda.c_eros)}
        {lineamiento_item("2. Protección y Conservación", celda.protcons)}
        {lineamiento_item("3. Aprovechamiento Sostenible", celda.aprovsos)}
        {lineamiento_item("4. Infraestructura Costera", celda.infcost)}
        {lineamiento_item("5. Gestión de Riesgos", celda.gesries)}
        {lineamiento_item("6. Gobernanza y Gestión", celda.gobgest)}
    </div>
    """

    from django.db import connection
    photos = []
    if celda.codigo:
        with connection.cursor() as cursor:
            # Match photos where cod_name starts with the cell code (e.g. 'QR-I')
            # Assuming format 'QR-I-1' or 'QR-I_something' or just exact match
            cursor.execute("SELECT nombre_archivo, latitud, longitud FROM datos.fotos_trasladadas WHERE cod_name LIKE %s", [f"{celda.codigo}%"])
            photos = [{"nombre": row[0].replace('.JPG', '.webp').replace('.jpg', '.webp'), "lat": row[1], "lon": row[2]} for row in cursor.fetchall()]

    return JsonResponse({
        "id": celda.id,
        "name": celda.nombre or f"Celda {celda.codigo}",
        "codigo": celda.codigo,
        "niveles_analisis": niveles_analisis,
        "datos_generales": datos_generales,
        "lineamientos": lineamientos,
        "photos": photos
    })

def serve_foto(request, filename):
    foto_path = os.path.join(settings.BASE_DIR, 'fotos', 'fotos', filename)
    if os.path.exists(foto_path):
        return FileResponse(open(foto_path, 'rb'), content_type='image/jpeg')
    return HttpResponse(status=404)


def api_subceldas(request):
    subceldas = SubcelQrN2.objects.all()
    features = []
    for s in subceldas:
        features.append({
            "type": "Feature",
            "properties": {
                "id": s.id,
                "codigo": s.codigo,
                "nombre": s.nombre,
                "celda": s.celda,
            },
            "geometry": json.loads(s.geom.geojson) if s.geom else None
        })
    return JsonResponse({"type": "FeatureCollection", "features": features})


def api_subcelda_detalle(request, pk):
    subcelda = get_object_or_404(SubcelQrN2, pk=pk)

    niveles_analisis = f"""
    <div class="section-content">
        {card_simple("Código de Subcelda", subcelda.codigo)}
        {card_simple("Código de Celda Padre", subcelda.celda)}
        {card_simple("Nombre de la Subcelda", subcelda.nombre)}
        {card_simple("Nombre de la Celda Padre", subcelda.nomcelda)}
    </div>
    """

    datos_generales = f"""
    <div class="section-content">
        {card_simple("Número de Tramos", subcelda.n_tramo)}
        {card_simple("Longitud convoluta de costa (km)", subcelda.lon_km)}
        {card_simple("Tramos que componen la subcelda", subcelda.tramos)}
        {card_simple("Arquetipo doctrinal predominante", subcelda.arquetip)}
        {card_simple("Caracterización de la subcelda", subcelda.caracter)}
        {card_simple("Tipos geomorfológicos presentes", subcelda.t_geomos)}
        {card_simple("Municipios intersectados", subcelda.municip)}
        {card_simple("Áreas naturales protegidas intersectadas", subcelda.anps)}
        {card_simple("Lineamientos de control de erosión (vista completa)", subcelda.c_eros)}
    </div>
    """

    lineamientos = f"""
    <div class="nested-accordion-container" style="display: flex; flex-direction: column; gap: 4px; margin-top: 10px;">
        {lineamiento_item("1. Protección y Conservación", subcelda.protcons)}
        {lineamiento_item("2. Aprovechamiento Sostenible", subcelda.aprovsos)}
        {lineamiento_item("3. Infraestructura Costera", subcelda.infcost)}
        {lineamiento_item("4. Gestión de Riesgos", subcelda.gesries)}
        {lineamiento_item("5. Gobernanza y Gestión", subcelda.gobgest)}
    </div>
    """

    from django.db import connection
    photos = []
    if subcelda.codigo:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT nombre_archivo, latitud, longitud FROM datos.fotos_trasladadas WHERE cod_name LIKE %s",
                [f"{subcelda.codigo}%"]
            )
            photos = [{"nombre": row[0].replace('.JPG', '.webp').replace('.jpg', '.webp'), "lat": row[1], "lon": row[2]} for row in cursor.fetchall()]

    return JsonResponse({
        "id": subcelda.id,
        "name": subcelda.nombre or f"Subcelda {subcelda.codigo}",
        "codigo": subcelda.codigo,
        "niveles_analisis": niveles_analisis,
        "datos_generales": datos_generales,
        "lineamientos": lineamientos,
        "photos": photos
    })
