import tkinter as tk

def configurarVentana(app):
    app.ventana = tk.Tk()
    app.ventana.title("💰 Tracker Financiero Personal")
    app.ventana.state("zoomed") 
    app.ventana.configure(bg="#121212")
    
    # Hacer la ventana un poco responsiva
    app.ventana.minsize(900, 600)
    
    # Icono (opcional - necesitarías un archivo .ico)
    # app.ventana.iconbitmap('icono.ico')