from setup.ventana import configurarVentana
from setup.estado import configurarColoresYEstado
from setup.ui import crear_interfaz
from setup.currency import CurrencyConverter

def configurar_app(app):
    configurarVentana(app)
    configurarColoresYEstado(app)
    app.converter = CurrencyConverter(app)
    crear_interfaz(app)