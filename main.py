# Tkinter viene instalado con Python, solo hay que importarlo
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class AplicacionFinanciera:
    def __init__(self):

        # ventana principal
        self.ventana = tk.Tk()
        self.ventana.title("Tracker Financiero Personal")
        self.ventana.geometry("800x600")
        
        self.color_positivo ="#4CAF50"  # Verde
        self.color_negativo = "#F44336"  # Rojo
        self.color_neutro ="#9E9E9E"    # Gris
        
        self.datos = self.cargar_datos()
        
        self.crear_interfaz()
        
    def cargar_datos(self):
        """Carga los datos desde el archivo JSON"""
        try:
            with open("datos.json", "r") as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            return []
    
    def guardar_datos(self):
        """Guarda los datos en el archivo JSON"""
        with open("datos.json", "w") as archivo:
            json.dump(self.datos, archivo, indent=2)
    
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
    
    def agregar_registro(self):
        """Agrega un nuevo registro"""
        try:
            fecha = self.entrada_fecha.get()
            monto = float(self.entrada_monto.get())
            moneda = self.moneda_var.get()
            
            # Validar fecha
            datetime.strptime(fecha, "%Y-%m-%d")
            
            # Determinar estado
            if monto > 0:
                estado = "POSITIVO"
            elif monto < 0:
                estado = "NEGATIVO"
            else:
                estado = "NEUTRO"
            
            # Crear registro
            registro = {
                "fecha": fecha,
                "monto": monto,
                "moneda": moneda,
                "estado": estado
            }
            
            # Agregar a datos
            self.datos.append(registro)
            
            # Guardar en archivo
            self.guardar_datos()
            
            # Actualizar tabla
            self.actualizar_tabla()
            self.actualizar_estadisticas()
            
            # Limpiar campos
            self.entrada_monto.delete(0, tk.END)
            
            messagebox.showinfo("Éxito", "✅ Registro agregado correctamente")
            
        except ValueError as e:
            messagebox.showerror("Error", "❌ Por favor, ingresa datos válidos")

    def borrar_registro(self):
        """Borra el registro seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "⚠️ Por favor, selecciona un registro para borrar")
            return
        
        indice = self.tabla.index(seleccion[0])
        
        # Confirmar borrado
        confirmar = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas borrar este registro?")
        if confirmar:
            # Borrar del listado de datos
            del self.datos[indice]
            
            # Guardar en archivo
            self.guardar_datos()
            
            # Actualizar tabla y estadísticas
            self.actualizar_tabla()
            self.actualizar_estadisticas()
            
    
    def actualizar_tabla(self):
        """Actualiza la tabla con los datos actuales"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Ordenar datos por fecha (más reciente primero)
        datos_ordenados = sorted(self.datos, key=lambda x: x["fecha"], reverse=True)
        
        # Agregar datos a la tabla
        for registro in datos_ordenados:
            # Determinar color según el estado
            tags = ()
            if registro["monto"] > 0:
                tags = ("positivo",)
            elif registro["monto"] < 0:
                tags = ("negativo",)
            else:
                tags = ("neutro",)
            
            self.tabla.insert(
                "",
                "end",
                values=(
                    registro["fecha"],
                    f"${abs(registro['monto']):.2f}",
                    registro["moneda"],
                    registro["estado"]
                ),
                tags=tags
            )
        
        # Configurar colores
        self.tabla.tag_configure("positivo", foreground=self.color_positivo)
        self.tabla.tag_configure("negativo", foreground=self.color_negativo)
        self.tabla.tag_configure("neutro", foreground=self.color_neutro)
    
    def crear_estadisticas(self):
        """Crea el panel de estadísticas"""
        frame_estadisticas = tk.Frame(self.ventana, bg="#2C3E50", padx=20, pady=10)
        frame_estadisticas.pack(fill="x", padx=20, pady=10)
        
        # Etiquetas para estadísticas
        self.lbl_total = tk.Label(
            frame_estadisticas,
            text="Total: $0.00",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#2C3E50"
        )
        self.lbl_total.pack(side="left", padx=20)
        
        self.lbl_promedio = tk.Label(
            frame_estadisticas,
            text="Promedio diario: $0.00",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#2C3E50"
        )
        self.lbl_promedio.pack(side="left", padx=20)
        
        self.lbl_dias = tk.Label(
            frame_estadisticas,
            text="Días registrados: 0",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#2C3E50"
        )
        self.lbl_dias.pack(side="left", padx=20)
        
        # Calcular estadísticas iniciales
        self.actualizar_estadisticas()
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas"""
        if not self.datos:
            total = 0
            promedio = 0
            dias = 0
        else:
            # Calcular total
            total = sum(registro["monto"] for registro in self.datos)
            
            # Calcular promedio
            promedio = total / len(self.datos)
            
            # Contar días únicos
            fechas = set(registro["fecha"] for registro in self.datos)
            dias = len(fechas)
        
        # Actualizar etiquetas
        color_total = self.color_positivo if total >= 0 else self.color_negativo
        self.lbl_total.config(text=f"Total: ${total:.2f}", fg=color_total)
        
        color_promedio = self.color_positivo if promedio >= 0 else self.color_negativo
        self.lbl_promedio.config(text=f"Promedio diario: ${promedio:.2f}", fg=color_promedio)
        
        self.lbl_dias.config(text=f"Días registrados: {dias}")

    def mostrar_calendario(self):
        """Muestra un calendario con las ganancias"""
        calendario_ventana = tk.Toplevel(self.ventana)
        calendario_ventana.title("Calendario de Ganancias")
        calendario_ventana.geometry("600x400")
        
        # Título
        tk.Label(
            calendario_ventana,
            text="📅 Calendario de Ganancias",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Frame para el calendario
        frame_calendario = tk.Frame(calendario_ventana)
        frame_calendario.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Organizar datos por fecha
        datos_por_fecha = {}
        for registro in self.datos:
            fecha = registro["fecha"]
            if fecha not in datos_por_fecha:
                datos_por_fecha[fecha] = []
            datos_por_fecha[fecha].append(registro)
        
        # Mostrar fechas con ganancias
        for fecha, registros in sorted(datos_por_fecha.items(), reverse=True)[:30]:  # Últimos 30 días
            total_dia = sum(r["monto"] for r in registros)
            
            # Determinar color
            if total_dia > 0:
                color = self.color_positivo
                emoji = "💰"
            elif total_dia < 0:
                color = self.color_negativo
                emoji = "🔴"
            else:
                color = self.color_neutro
                emoji = "⚪"
            
            # Crear etiqueta para el día
            dia_frame = tk.Frame(frame_calendario)
            dia_frame.pack(fill="x", pady=2)
            
            tk.Label(
                dia_frame,
                text=f"{emoji} {fecha}",
                width=15,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                dia_frame,
                text=f"${total_dia:+.2f}",
                fg=color,
                font=("Arial", 10, "bold")
            ).pack(side="left", padx=10)
            
            # Mostrar detalles al pasar el mouse
            detalles = ", ".join([f"${r['monto']} {r['moneda']}" for r in registros])
            tk.Label(
                dia_frame,
                text=f"({detalles})",
                fg="#7F8C8D",
                font=("Arial", 8)
            ).pack(side="left")

    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.ventana.mainloop()

# Crear y ejecutar la aplicación
if __name__ == "__main__":
    app = AplicacionFinanciera()
    app.ejecutar()