import json

def configurarColoresYEstado(app):
    app.color_positivo ="#4CAF50"  
    app.color_negativo = "#F44336"  
    app.color_neutro ="#9E9E9E"
    app.datos = cargar_datos(app)

def cargar_datos(app):
        """Carga los datos desde el archivo JSON"""
        try:
            with open("datos.json", "r") as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            return []