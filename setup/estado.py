import json
import os

def configurarColoresYEstado(app):
    # Colores modernos para tema oscuro
    app.color_fondo = "#121212"
    app.color_fondo_secundario = "#1E1E1E"
    app.color_fondo_terciario = "#2D2D2D"
    app.color_borde = "#404040"
    app.color_texto = "#FFFFFF"
    app.color_texto_secundario = "#B0B0B0"
    
    # Colores para estados financieros
    app.color_positivo = "#4CAF50"  # Verde vibrante
    app.color_positivo_claro = "#A5D6A7"
    app.color_negativo = "#F44336"  # Rojo vibrante
    app.color_negativo_claro = "#EF9A9A"
    app.color_neutro = "#9E9E9E"    # Gris
    app.color_acento = "#BB86FC"    # Morado moderno
    app.color_acento_secundario = "#03DAC6"  # Turquesa
    
    # Colores para botones
    app.color_boton_agregar = "#2196F3"      # Azul
    app.color_boton_borrar = "#FF5252"       # Rojo claro
    app.color_boton_calendario = "#9C27B0"   # Morado
    app.color_boton_neutral = "#6200EE"      # Morado oscuro
    
    app.datos = cargar_datos(app)
    app.configuracion = cargar_configuracion(app)

def cargar_datos(app):
    """Carga los datos desde el archivo JSON"""
    try:
        with open("datos.json", "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []

def cargar_configuracion(app):
    """Carga la configuración de la aplicación"""
    config_file = "config.json"
    config_default = {
        "moneda_principal": "ARS",  # Moneda local por defecto
        "balance_total": 0.0,
        "tasa_manual_usd": 1500.0,   # Tasa manual para USD si la API falla
        "tasa_manual_eur": 1020.0   # Tasa manual para EUR
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = json.load(f)
                # Asegurarse de que todas las claves existan
                for key, value in config_default.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            return config_default
    except Exception as e:
        print(f"Error cargando configuración: {e}")
        return config_default

def guardar_configuracion(app):
    """Guarda la configuración de la aplicación"""
    try:
        with open("config.json", "w") as f:
            json.dump(app.configuracion, f, indent=2)
    except Exception as e:
        print(f"Error guardando configuración: {e}")
