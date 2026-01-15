import json

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

def cargar_datos(app):
    """Carga los datos desde el archivo JSON"""
    try:
        with open("datos.json", "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []