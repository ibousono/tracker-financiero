import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

from setup.facade import configurar_app

class AplicacionFinanciera:
    def __init__(self):
        # configura la ventana, los colores y carga los datos 
        configurar_app(self)
    
    def guardar_datos(self):
        """Guarda los datos en el archivo JSON"""
        with open("datos.json", "w") as archivo:
            json.dump(self.datos, archivo, indent=2)
    
    def agregar_registro(self):
        """Agrega un nuevo registro"""
        try:
            fecha = self.entrada_fecha.get()
            monto = float(self.entrada_monto.get())
            moneda = self.moneda_var.get()
            
            # Validar fecha
            datetime.strptime(fecha, "%Y-%m-%d")
            
            if monto > 0:
                estado = "POSITIVO"
            elif monto < 0:
                estado = "NEGATIVO"
            else:
                estado = "NEUTRO"
            
            registro = {
                "fecha": fecha,
                "monto": monto,
                "moneda": moneda,
                "estado": estado
            }
            
            self.datos.append(registro)
            self.aplicarCambios()
            
            # Limpiar campos
            self.entrada_monto.delete(0, tk.END)
            
        except ValueError as e:
            messagebox.showerror("Error", "❌ Por favor, ingresa datos válidos")

    def borrar_registro(self):
        """Borra el registro seleccionado"""

        # self.tabla.selection() devuelve una tupla con los items seleccionados
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "⚠️ Por favor, selecciona un registro para borrar")
            return
        
        indice = self.tabla.index(seleccion[0])
        
        confirmar = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas borrar este registro?")
        if confirmar:

            del self.datos[indice]
            self.aplicarCambios()

    def aplicarCambios(self):
        """Aplica los cambios: guarda datos, actualiza tabla y estadísticas"""
        self.guardar_datos()
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
        """Muestra un calendario mensual con las ganancias por día"""
        calendario_ventana = tk.Toplevel(self.ventana)
        calendario_ventana.title("Calendario Mensual de Ganancias")
        calendario_ventana.geometry("800x600")
        
        # Frame principal
        main_frame = tk.Frame(calendario_ventana)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título con mes y año
        titulo_frame = tk.Frame(main_frame)
        titulo_frame.pack(fill="x", pady=(0, 10))
        
        # Botones para navegar entre meses
        btn_anterior = tk.Button(titulo_frame, text="←", font=("Arial", 12))
        btn_anterior.pack(side="left", padx=5)
        
        self.mes_calendario = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        lbl_mes = tk.Label(
            titulo_frame,
            textvariable=self.mes_calendario,
            font=("Arial", 16, "bold")
        )
        lbl_mes.pack(side="left", expand=True)
        
        btn_siguiente = tk.Button(titulo_frame, text="→", font=("Arial", 12))
        btn_siguiente.pack(side="left", padx=5)
        
        # Frame para el calendario
        frame_calendario = tk.Frame(main_frame)
        frame_calendario.pack(fill="both", expand=True)
        
        # Organizar datos por fecha
        self.datos_por_fecha = {}
        for registro in self.datos:
            fecha = registro["fecha"]
            if fecha not in self.datos_por_fecha:
                self.datos_por_fecha[fecha] = []
            self.datos_por_fecha[fecha].append(registro)
        
        # Crear encabezados de días de la semana
        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for i, dia in enumerate(dias_semana):
            lbl_dia = tk.Label(
                frame_calendario,
                text=dia,
                font=("Arial", 10, "bold"),
                bg="#3498DB",
                fg="white",
                relief="raised",
                width=15,
                height=2
            )
            lbl_dia.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
        
        # Hacer que las columnas se expandan uniformemente
        for i in range(7):
            frame_calendario.columnconfigure(i, weight=1)
        
        # Mostrar el mes actual
        self.actualizar_calendario(frame_calendario, btn_anterior, btn_siguiente)
        
        # Asignar comandos a los botones
        btn_anterior.config(command=lambda: self.cambiar_mes(frame_calendario, btn_anterior, btn_siguiente, -1))
        btn_siguiente.config(command=lambda: self.cambiar_mes(frame_calendario, btn_anterior, btn_siguiente, 1))
    
    def actualizar_calendario(self, frame_calendario, btn_anterior, btn_siguiente):
        """Actualiza el calendario con el mes actual"""
        # Limpiar el frame del calendario (excepto los encabezados)
        for widget in frame_calendario.winfo_children():
            if widget.grid_info()["row"] > 0:
                widget.destroy()
        
        # Obtener el año y mes actual
        ano_mes = self.mes_calendario.get()
        ano, mes = map(int, ano_mes.split("-"))
        
        # Obtener el primer día del mes y el número de días
        import calendar
        primer_dia = calendar.monthrange(ano, mes)[0]
        num_dias = calendar.monthrange(ano, mes)[1]
        
        # Llenar el calendario
        fila = 1
        columna = primer_dia  # 0=Lunes, 1=Martes, etc.
        
        for dia in range(1, num_dias + 1):
            fecha_str = f"{ano}-{mes:02d}-{dia:02d}"
            
            # Crear frame para el día
            dia_frame = tk.Frame(
                frame_calendario,
                relief="solid",
                borderwidth=1,
                bg="white"
            )
            dia_frame.grid(row=fila, column=columna, sticky="nsew", padx=1, pady=1)
            
            # Número del día
            lbl_numero = tk.Label(
                dia_frame,
                text=str(dia),
                font=("Arial", 10, "bold"),
                bg="white"
            )
            lbl_numero.pack(anchor="nw", padx=2, pady=2)
            
            # Mostrar ganancias si hay datos para este día
            if fecha_str in self.datos_por_fecha:
                total_dia = sum(r["monto"] for r in self.datos_por_fecha[fecha_str])
                
                # Determinar color y emoji
                if total_dia > 0:
                    color = self.color_positivo
                    emoji = "💰"
                    texto = f"{emoji} +${total_dia:.2f}"
                elif total_dia < 0:
                    color = self.color_negativo
                    emoji = "🔴"
                    texto = f"{emoji} -${abs(total_dia):.2f}"
                else:
                    color = self.color_neutro
                    emoji = "⚪"
                    texto = f"{emoji} ${total_dia:.2f}"
                
                # Etiqueta con el total
                lbl_total = tk.Label(
                    dia_frame,
                    text=texto,
                    font=("Arial", 8),
                    fg=color,
                    bg="white"
                )
                lbl_total.pack(fill="x", padx=2)
                
                # Tooltip con detalles
                detalles = "\n".join([f"${r['monto']:+.2f} {r['moneda']}" for r in self.datos_por_fecha[fecha_str]])
                
                def crear_tooltip(widget, texto_detalles, fecha=fecha_str):
                    tooltip = tk.Toplevel(widget.winfo_toplevel())
                    tooltip.wm_overrideredirect(True)
                    tooltip.wm_geometry(f"+{widget.winfo_rootx()+20}+{widget.winfo_rooty()+20}")
                    
                    label = tk.Label(
                        tooltip,
                        text=f"{fecha}\n{texto_detalles}",
                        background="lightyellow",
                        relief="solid",
                        borderwidth=1,
                        font=("Arial", 9),
                        padx=5,
                        pady=5
                    )
                    label.pack()
                    
                    # Hacer que el tooltip desaparezca después de un tiempo
                    tooltip.after(3000, tooltip.destroy)
                
                # Asignar eventos para el tooltip
                dia_frame.bind("<Enter>", lambda e, w=dia_frame, d=detalles, f=fecha_str: crear_tooltip(w, d, f))
            
            # Ajustar posición para el siguiente día
            columna += 1
            if columna > 6:
                columna = 0
                fila += 1
        
        # Hacer que todas las filas se expandan uniformemente
        for i in range(1, fila + 1):
            frame_calendario.rowconfigure(i, weight=1)
    
    def cambiar_mes(self, frame_calendario, btn_anterior, btn_siguiente, delta):
        """Cambia el mes en el calendario"""
        ano_mes_actual = self.mes_calendario.get()
        ano, mes = map(int, ano_mes_actual.split("-"))
        
        # Calcular nuevo mes
        mes += delta
        if mes > 12:
            mes = 1
            ano += 1
        elif mes < 1:
            mes = 12
            ano -= 1
        
        # Actualizar variable y calendario
        self.mes_calendario.set(f"{ano}-{mes:02d}")
        self.actualizar_calendario(frame_calendario, btn_anterior, btn_siguiente)

    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.ventana.mainloop()

if __name__ == "__main__":
    app = AplicacionFinanciera()
    app.ejecutar()
