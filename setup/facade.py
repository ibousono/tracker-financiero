from setup.ventana import configurarVentana
from setup.estado import configurarColoresYEstado
from setup.ui import crear_interfaz

def configurar_app(app):
    configurarVentana(app)
    configurarColoresYEstado(app)    
    crear_interfaz(app)