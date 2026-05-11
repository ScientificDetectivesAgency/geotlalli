from django.contrib.gis.db import models

class PuntoCosta(models.Model):
    nombre = models.CharField(max_length=200, help_text="Nombre del punto o ubicación")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción o detalles relevantes")
    geom = models.PointField(srid=4326, help_text="Coordenadas exactas en la línea de costa")
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Punto de Costa"
        verbose_name_plural = "Puntos de Costa"

class FotoPunto(models.Model):
    punto = models.ForeignKey(PuntoCosta, related_name='fotos', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='fotos_costa/')
    leyenda = models.CharField(max_length=255, blank=True, null=True, help_text="Pie de foto opcional")
    subida_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.punto.nombre}"

class DatosPlayas(models.Model):
    id = models.CharField(primary_key=True)
    nombre_tramo = models.CharField(blank=True, null=True)
    coord_init = models.CharField(blank=True, null=True)
    coord_final = models.CharField(blank=True, null=True)
    long = models.CharField(blank=True, null=True)
    tipo_geomorfo = models.CharField(blank=True, null=True)
    subtipo_detallado = models.CharField(blank=True, null=True)
    tipo_playa = models.CharField(blank=True, null=True)
    nivel_energia = models.CharField(blank=True, null=True)
    dir_dominante = models.CharField(blank=True, null=True)
    mag_estimada = models.CharField(blank=True, null=True)
    fuentes_sedimento = models.CharField(blank=True, null=True)
    sumideros_sedimento = models.CharField(blank=True, null=True)
    balance_sedimentario = models.CharField(blank=True, null=True)
    est_costeras = models.CharField(blank=True, null=True)
    ev_erosion = models.CharField(blank=True, null=True)
    influ_arrecifal = models.CharField(blank=True, null=True)
    influ_manglar = models.CharField(blank=True, null=True)
    pres_antropic = models.CharField(blank=True, null=True)
    conectividad = models.CharField(blank=True, null=True)
    incertidumbre = models.CharField(blank=True, null=True)
    tipo_soporte = models.CharField(blank=True, null=True)
    geom_init = models.PointField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'datos_playas'


class TcQrN3(models.Model):
    id = models.IntegerField(primary_key=True)
    geom = models.MultiLineStringField(srid=4326)
    fid = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    x_inicio = models.FloatField(blank=True, null=True)
    y_inicio = models.FloatField(blank=True, null=True)
    x_fin = models.FloatField(blank=True, null=True)
    y_fin = models.FloatField(blank=True, null=True)
    celda = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=255, blank=True, null=True)
    cod_name = models.CharField(max_length=255, blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    ac_calle = models.CharField(max_length=255, blank=True, null=True)
    subcelda = models.CharField(max_length=255, blank=True, null=True)
    t_geomo = models.CharField(max_length=255, blank=True, null=True)
    subtipo = models.CharField(max_length=255, blank=True, null=True)
    t_playa = models.CharField(max_length=255, blank=True, null=True)
    n_energi = models.CharField(max_length=255, blank=True, null=True)
    d_t_lito = models.CharField(max_length=255, blank=True, null=True)
    magn_m3a = models.CharField(max_length=255, blank=True, null=True)
    fuentsed = models.CharField(max_length=255, blank=True, null=True)
    sumidero = models.CharField(max_length=255, blank=True, null=True)
    bal_m3a = models.CharField(max_length=255, blank=True, null=True)
    est_cost = models.CharField(max_length=255, blank=True, null=True)
    eros_acr = models.CharField(max_length=255, blank=True, null=True)
    inf_arre = models.CharField(max_length=255, blank=True, null=True)
    inf_mang = models.CharField(max_length=255, blank=True, null=True)
    p_antrop = models.CharField(max_length=255, blank=True, null=True)
    conectiv = models.CharField(max_length=255, blank=True, null=True)
    incertid = models.CharField(max_length=255, blank=True, null=True)
    evidenci = models.CharField(max_length=255, blank=True, null=True)
    municip = models.CharField(max_length=255, blank=True, null=True)
    anps = models.CharField(max_length=255, blank=True, null=True)
    c_eros = models.CharField(max_length=255, blank=True, null=True)
    protcons = models.CharField(max_length=255, blank=True, null=True)
    aprovsos = models.CharField(max_length=255, blank=True, null=True)
    infcost = models.CharField(max_length=255, blank=True, null=True)
    gesries = models.CharField(max_length=255, blank=True, null=True)
    gobgest = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'datos"."tc_qr_n3'


class CelQrN1(models.Model):
    id = models.IntegerField(primary_key=True)
    geom = models.MultiPolygonField(srid=4326, blank=True, null=True)
    fid = models.BigIntegerField(blank=True, null=True)
    codigo = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    n_sub = models.IntegerField(blank=True, null=True)
    n_tramo = models.IntegerField(blank=True, null=True)
    lon_km = models.FloatField(blank=True, null=True)
    subceldas = models.CharField(max_length=255, blank=True, null=True)
    tramos = models.CharField(max_length=255, blank=True, null=True)
    sistema = models.CharField(max_length=255, blank=True, null=True)
    procesos = models.CharField(max_length=255, blank=True, null=True)
    arrecife = models.CharField(max_length=255, blank=True, null=True)
    manglar = models.CharField(max_length=255, blank=True, null=True)
    asuprinc = models.CharField(max_length=255, blank=True, null=True)
    estconsv = models.CharField(max_length=255, blank=True, null=True)
    t_geomos = models.CharField(max_length=255, blank=True, null=True)
    municip = models.CharField(max_length=255, blank=True, null=True)
    anps = models.CharField(max_length=255, blank=True, null=True)
    c_eros = models.CharField(max_length=255, blank=True, null=True)
    protcons = models.CharField(max_length=255, blank=True, null=True)
    aprovsos = models.CharField(max_length=255, blank=True, null=True)
    infcost = models.CharField(max_length=255, blank=True, null=True)
    gesries = models.CharField(max_length=255, blank=True, null=True)
    gobgest = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'datos"."cel_qr_n1'


class SubcelQrN2(models.Model):
    id = models.IntegerField(primary_key=True)
    geom = models.MultiPolygonField(srid=4326, blank=True, null=True)
    codigo = models.CharField(max_length=255, blank=True, null=True)
    celda = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    nomcelda = models.CharField(max_length=255, blank=True, null=True)
    n_tramo = models.CharField(max_length=255, blank=True, null=True)
    lon_km = models.CharField(max_length=255, blank=True, null=True)
    tramos = models.CharField(max_length=255, blank=True, null=True)
    arquetip = models.CharField(max_length=255, blank=True, null=True)
    caracter = models.CharField(max_length=255, blank=True, null=True)
    t_geomos = models.CharField(max_length=255, blank=True, null=True)
    municip = models.CharField(max_length=255, blank=True, null=True)
    anps = models.CharField(max_length=255, blank=True, null=True)
    c_eros = models.CharField(max_length=255, blank=True, null=True)
    protcons = models.CharField(max_length=255, blank=True, null=True)
    aprovsos = models.CharField(max_length=255, blank=True, null=True)
    infcost = models.CharField(max_length=255, blank=True, null=True)
    gesries = models.CharField(max_length=255, blank=True, null=True)
    gobgest = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'datos"."subcel_qr_n2'
