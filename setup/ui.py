
import tkinter as tk
from tkinter import ttk
from datetime import datetime


def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        
        # Título
        titulo = tk.Label(
            self.ventana,
            text="💰 TRACKER FINANCIERO PERSONAL",
            font=("Arial", 20, "bold"),
            fg="#2C3E50"
        )
        titulo.pack(pady=20)
        
        # Frame para ingresar datos
        frame_ingreso = tk.Frame(self.ventana, bg="#ECF0F1", padx=20, pady=20)
        frame_ingreso.pack(pady=10, fill="x")
        
        # Etiquetas y campos de entrada
        tk.Label(frame_ingreso, text="Fecha (YYYY-MM-DD):", bg="#ECF0F1").grid(row=0, column=0, sticky="w")
        self.entrada_fecha = tk.Entry(frame_ingreso, width=20)
        self.entrada_fecha.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(frame_ingreso, text="Monto:", bg="#ECF0F1").grid(row=1, column=0, sticky="w")
        self.entrada_monto = tk.Entry(frame_ingreso, width=20)
        self.entrada_monto.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_ingreso, text="Moneda:", bg="#ECF0F1").grid(row=2, column=0, sticky="w")
        self.moneda_var = tk.StringVar(value="USD")
        tk.Radiobutton(frame_ingreso, text="USD", variable=self.moneda_var, value="USD", bg="#ECF0F1").grid(row=2, column=1, sticky="w")
        tk.Radiobutton(frame_ingreso, text="ARS", variable=self.moneda_var, value="ARS", bg="#ECF0F1").grid(row=2, column=2, sticky="w")
        
        # Botón para agregar
        btn_agregar = tk.Button(
            frame_ingreso,
            text="➕ Agregar Registro",
            command=self.agregar_registro,
            bg="#3498DB",
            fg="white",
            font=("Arial", 10, "bold")
        )
        btn_agregar.grid(row=3, column=0, columnspan=3, pady=10)


        # Boton para borrar
        btn_borrar = tk.Button(
            frame_ingreso,
            text="❌ Borrar Registro",
            command=self.borrar_registro,
            bg="#E74C3C",
            fg="white",
            font=("Arial", 10, "bold")
        )
        btn_borrar.grid(row=4, column=0, columnspan=3, pady=10)

        # Boton calendario
        btn_calendario = tk.Button(
            frame_ingreso,
            text="📅 Ver Calendario",
            command=self.mostrar_calendario,
            bg="#9B59B6",
            fg="white",
            font=("Arial", 10, "bold")
        )
        btn_calendario.grid(row=3, column=3, columnspan=2, pady=10, padx=10)
        
        # Frame para mostrar datos
        frame_datos = tk.Frame(self.ventana)
        frame_datos.pack(pady=20, fill="both", expand=True, padx=20)
        
        # Tabla para mostrar registros
        self.tabla = ttk.Treeview(
            frame_datos,
            columns=("Fecha", "Monto", "Moneda", "Estado"),
            show="headings",
            height=15
        )
        
        # Configurar columnas
        self.tabla.heading("Fecha", text="📅 Fecha")
        self.tabla.heading("Monto", text="💰 Monto")
        self.tabla.heading("Moneda", text="💱 Moneda")
        self.tabla.heading("Estado", text="📊 Estado")
        
        self.tabla.column("Fecha", width=150)
        self.tabla.column("Monto", width=100)
        self.tabla.column("Moneda", width=80)
        self.tabla.column("Estado", width=100)
        
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_datos, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar elementos
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar datos en la tabla
        self.actualizar_tabla()
        
        # Estadísticas
        self.crear_estadisticas()