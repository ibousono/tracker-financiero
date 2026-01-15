import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
import calendar

from setup.facade import configurar_app

class AplicacionFinanciera:
    def __init__(self):
        # configura la ventana, los colores y carga los datos 
        configurar_app(self)
    
    def configurar_estilos(self):
        """Configura estilos adicionales para widgets"""
        pass
    
    def on_enter(self, event, widget, color):
        """Efecto hover para botones"""
        widget.config(bg=self.aumentar_brightness(color, 20))
    
    def on_leave(self, event, widget, color):
        """Efecto hover para botones"""
        widget.config(bg=color)
    
    def aumentar_brightness(self, hex_color, factor):
        """Aumenta el brillo de un color hex"""
        # Convertir hex a RGB
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Aumentar brillo
        rgb = tuple(min(255, c + factor) for c in rgb)
        
        # Convertir de nuevo a hex
        return '#%02x%02x%02x' % rgb
    
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
        """Crea el panel de estadísticas moderno"""
        # Frame para estadísticas
        stats_frame = tk.Frame(
            self.ventana,
            bg=self.color_fondo_secundario,
            relief="flat",
            highlightbackground=self.color_borde,
            highlightthickness=1,
            padx=25,
            pady=20
        )
        stats_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        # Título
        tk.Label(
            stats_frame,
            text="📈 ESTADÍSTICAS",
            font=("Segoe UI", 14, "bold"),
            fg=self.color_acento,
            bg=self.color_fondo_secundario
        ).pack(anchor="w", pady=(0, 15))
        
        # Contenedor para las métricas
        metrics_container = tk.Frame(stats_frame, bg=self.color_fondo_secundario)
        metrics_container.pack(fill="x")
        
        # Métricas
        metrics = [
            ("Total", "lbl_total", "$0.00"),
            ("Promedio Diario", "lbl_promedio", "$0.00"),
            ("Días Registrados", "lbl_dias", "0"),
            ("Balance", "lbl_balance", "$0.00")
        ]
        
        for i, (titulo, attr_name, valor_default) in enumerate(metrics):
            metric_frame = tk.Frame(metrics_container, bg=self.color_fondo_secundario)
            metric_frame.pack(side="left", fill="x", expand=True, padx=(0, 30))
            
            # Título de la métrica
            tk.Label(
                metric_frame,
                text=titulo,
                font=("Segoe UI", 10),
                fg=self.color_texto_secundario,
                bg=self.color_fondo_secundario
            ).pack(anchor="w", pady=(0, 5))
            
            # Valor de la métrica
            valor_label = tk.Label(
                metric_frame,
                text=valor_default,
                font=("Segoe UI", 18, "bold"),
                fg="white",
                bg=self.color_fondo_secundario
            )
            valor_label.pack(anchor="w")
            
            # Asignar a la instancia
            setattr(self, attr_name, valor_label)
        
        # Calcular estadísticas iniciales
        self.actualizar_estadisticas()
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas"""
        if not self.datos:
            total = 0
            promedio = 0
            dias = 0
            balance = 0
        else:
            # Calcular total
            total = sum(registro["monto"] for registro in self.datos)
            
            # Calcular promedio
            promedio = total / len(self.datos)
            
            # Contar días únicos
            fechas = set(registro["fecha"] for registro in self.datos)
            dias = len(fechas)
            
            # Calcular balance (positivo/negativo)
            balance = total
        
        # Actualizar etiquetas con colores
        color_total = self.color_positivo if total >= 0 else self.color_negativo
        self.lbl_total.config(text=f"${total:+.2f}", fg=color_total)
        
        color_promedio = self.color_positivo if promedio >= 0 else self.color_negativo
        self.lbl_promedio.config(text=f"${promedio:+.2f}", fg=color_promedio)
        
        self.lbl_dias.config(text=f"{dias}")
        
        color_balance = self.color_positivo if balance >= 0 else self.color_negativo
        self.lbl_balance.config(text=f"${balance:+.2f}", fg=color_balance)

    def mostrar_calendario(self):
        """Muestra un calendario mensual con las ganancias por día"""
        calendario_ventana = tk.Toplevel(self.ventana)
        calendario_ventana.title("📅 Calendario Mensual")
        calendario_ventana.geometry("900x650")
        calendario_ventana.configure(bg=self.color_fondo)
        
        # Hacer la ventana un poco responsiva
        calendario_ventana.minsize(850, 600)
        
        # Frame principal con padding
        main_frame = tk.Frame(calendario_ventana, bg=self.color_fondo)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Header del calendario
        header_frame = tk.Frame(
            main_frame,
            bg=self.color_fondo_secundario,
            height=70
        )
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Título del calendario
        titulo_calendario = tk.Label(
            header_frame,
            text="📅 CALENDARIO FINANCIERO",
            font=("Segoe UI", 16, "bold"),
            fg=self.color_acento,
            bg=self.color_fondo_secundario
        )
        titulo_calendario.pack(side="left", padx=25, pady=20)
        
        # Frame para controles de navegación
        controles_frame = tk.Frame(header_frame, bg=self.color_fondo_secundario)
        controles_frame.pack(side="right", padx=25, pady=20)
        
        # Botón anterior
        btn_anterior = tk.Button(
            controles_frame,
            text="←",
            font=("Segoe UI", 12, "bold"),
            bg=self.color_boton_neutral,
            fg="white",
            relief="flat",
            borderwidth=0,
            width=3,
            cursor="hand2"
        )
        btn_anterior.pack(side="left", padx=5)
        
        # Label del mes actual
        self.mes_calendario = tk.StringVar(value=datetime.now().strftime("%B %Y"))
        
        lbl_mes = tk.Label(
            controles_frame,
            textvariable=self.mes_calendario,
            font=("Segoe UI", 14, "bold"),
            fg=self.color_texto,
            bg=self.color_fondo_secundario
        )
        lbl_mes.pack(side="left", padx=20)
        
        # Botón siguiente
        btn_siguiente = tk.Button(
            controles_frame,
            text="→",
            font=("Segoe UI", 12, "bold"),
            bg=self.color_boton_neutral,
            fg="white",
            relief="flat",
            borderwidth=0,
            width=3,
            cursor="hand2"
        )
        btn_siguiente.pack(side="left", padx=5)
        
        # Aplicar efectos hover a los botones
        btn_anterior.bind("<Enter>", lambda e, b=btn_anterior: self.on_enter(e, b, self.color_boton_neutral))
        btn_anterior.bind("<Leave>", lambda e, b=btn_anterior: self.on_leave(e, b, self.color_boton_neutral))
        btn_siguiente.bind("<Enter>", lambda e, b=btn_siguiente: self.on_enter(e, b, self.color_boton_neutral))
        btn_siguiente.bind("<Leave>", lambda e, b=btn_siguiente: self.on_leave(e, b, self.color_boton_neutral))
        
        # Frame para el calendario
        frame_calendario = tk.Frame(
            main_frame,
            bg=self.color_fondo_secundario,
            relief="flat",
            highlightbackground=self.color_borde,
            highlightthickness=1
        )
        frame_calendario.pack(fill="both", expand=True)
        
        # Organizar datos por fecha
        self.datos_por_fecha = {}
        for registro in self.datos:
            fecha = registro["fecha"]
            if fecha not in self.datos_por_fecha:
                self.datos_por_fecha[fecha] = []
            self.datos_por_fecha[fecha].append(registro)
        
        # Frame para los encabezados de días
        header_dias_frame = tk.Frame(frame_calendario, bg=self.color_fondo_secundario)
        header_dias_frame.pack(fill="x", padx=10, pady=(15, 5))
        
        # Crear encabezados de días de la semana
        dias_semana = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
        for i, dia in enumerate(dias_semana):
            lbl_dia = tk.Label(
                header_dias_frame,
                text=dia,
                font=("Segoe UI", 10, "bold"),
                bg=self.color_fondo_secundario,
                fg=self.color_texto_secundario,
                width=12,
                height=2
            )
            lbl_dia.pack(side="left", fill="both", expand=True, padx=1)
        
        # Frame para la cuadrícula del calendario
        grid_frame = tk.Frame(frame_calendario, bg=self.color_fondo_secundario)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        # Hacer que las columnas se expandan uniformemente
        for i in range(7):
            grid_frame.columnconfigure(i, weight=1)
        
        # Mostrar el mes actual
        self.actualizar_calendario(grid_frame, btn_anterior, btn_siguiente)
        
        # Asignar comandos a los botones
        btn_anterior.config(command=lambda: self.cambiar_mes(grid_frame, btn_anterior, btn_siguiente, -1))
        btn_siguiente.config(command=lambda: self.cambiar_mes(grid_frame, btn_anterior, btn_siguiente, 1))
        
        # Leyenda en la parte inferior
        leyenda_frame = tk.Frame(main_frame, bg=self.color_fondo)
        leyenda_frame.pack(fill="x", pady=(15, 0))
        
        # Crear leyenda
        leyendas = [
            (self.color_positivo, "💰 Ganancias"),
            (self.color_negativo, "🔴 Pérdidas"),
            (self.color_neutro, "⚪ Neutral"),
            (self.color_acento, "📅 Hoy")
        ]
        
        for color, texto in leyendas:
            leyenda_item = tk.Frame(leyenda_frame, bg=self.color_fondo)
            leyenda_item.pack(side="left", padx=15)
            
            # Círculo de color
            tk.Frame(
                leyenda_item,
                width=12,
                height=12,
                bg=color,
                relief="solid",
                borderwidth=1
            ).pack(side="left", padx=(0, 5))
            
            # Texto
            tk.Label(
                leyenda_item,
                text=texto,
                font=("Segoe UI", 9),
                fg=self.color_texto_secundario,
                bg=self.color_fondo
            ).pack(side="left")

    def actualizar_calendario(self, grid_frame, btn_anterior, btn_siguiente):
        """Actualiza el calendario con el mes actual"""
        # Limpiar el frame del calendario
        for widget in grid_frame.winfo_children():
            widget.destroy()
        
        # Obtener el año y mes actual
        mes_texto = self.mes_calendario.get()
        ano_actual = datetime.now().year
        mes_actual = datetime.now().month
        
        # Convertir texto del mes a número
        meses = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        
        # Si tenemos texto del mes, usarlo; de lo contrario, usar el actual
        if " " in mes_texto:
            nombre_mes, ano_str = mes_texto.split()
            mes = meses.get(nombre_mes, mes_actual)
            ano = int(ano_str)
        else:
            mes = mes_actual
            ano = ano_actual
        
        # Obtener el primer día del mes y el número de días
        import calendar
        primer_dia = calendar.monthrange(ano, mes)[0]
        num_dias = calendar.monthrange(ano, mes)[1]
        
        # Ajustar primer_dia para que 0=Lunes (calendario usa 0=Lunes por defecto)
        
        # Llenar el calendario
        fila = 0
        columna = primer_dia
        
        # Rellenar días vacíos al inicio del mes
        for i in range(primer_dia):
            dia_vacio = tk.Frame(
                grid_frame,
                bg=self.color_fondo_secundario,
                relief="flat",
                height=80
            )
            dia_vacio.grid(row=fila, column=i, sticky="nsew", padx=1, pady=1)
        
        # Crear los días del mes
        for dia in range(1, num_dias + 1):
            fecha_str = f"{ano}-{mes:02d}-{dia:02d}"
            
            # Determinar si es hoy
            hoy = datetime.now()
            es_hoy = (hoy.year == ano and hoy.month == mes and hoy.day == dia)
            
            # Crear frame para el día
            bg_color = self.color_acento if es_hoy else self.color_fondo_terciario
            border_color = self.color_acento if es_hoy else self.color_borde
            
            dia_frame = tk.Frame(
                grid_frame,
                bg=bg_color,
                relief="solid",
                borderwidth=1,
                highlightbackground=border_color,
                highlightthickness=1
            )
            dia_frame.grid(row=fila, column=columna, sticky="nsew", padx=1, pady=1)
            
            # Configurar el grid para que se expanda
            grid_frame.rowconfigure(fila, weight=1)
            grid_frame.columnconfigure(columna, weight=1)
            
            # Número del día
            numero_color = "white" if es_hoy else self.color_texto
            lbl_numero = tk.Label(
                dia_frame,
                text=str(dia),
                font=("Segoe UI", 10, "bold"),
                bg=bg_color,
                fg=numero_color
            )
            lbl_numero.pack(anchor="nw", padx=5, pady=5)
            
            # Mostrar ganancias si hay datos para este día
            if fecha_str in self.datos_por_fecha:
                total_dia = sum(r["monto"] for r in self.datos_por_fecha[fecha_str])
                
                # Determinar color y emoji
                if total_dia > 0:
                    color = self.color_positivo
                    emoji = "💰"
                    texto = f"{emoji} +{abs(total_dia):.0f}"
                elif total_dia < 0:
                    color = self.color_negativo
                    emoji = "🔴"
                    texto = f"{emoji} -{abs(total_dia):.0f}"
                else:
                    color = self.color_neutro
                    emoji = "⚪"
                    texto = f"{emoji} 0"
                
                # Etiqueta con el total
                lbl_total = tk.Label(
                    dia_frame,
                    text=texto,
                    font=("Segoe UI", 9, "bold"),
                    fg=color,
                    bg=bg_color
                )
                lbl_total.pack(fill="x", padx=5, pady=2)
                
                # Tooltip con detalles
                detalles = "\n".join([f"${r['monto']:+.2f} {r['moneda']}" for r in self.datos_por_fecha[fecha_str]])
                
                def crear_tooltip(widget, fecha, texto_detalles, total):
                    tooltip = tk.Toplevel(widget.winfo_toplevel())
                    tooltip.wm_overrideredirect(True)
                    tooltip.wm_geometry(f"+{widget.winfo_rootx()+20}+{widget.winfo_rooty()+20}")
                    
                    frame_tooltip = tk.Frame(
                        tooltip,
                        bg=self.color_fondo_terciario,
                        relief="solid",
                        borderwidth=1
                    )
                    frame_tooltip.pack()
                    
                    # Título
                    tk.Label(
                        frame_tooltip,
                        text=f"📅 {fecha}",
                        font=("Segoe UI", 10, "bold"),
                        bg=self.color_fondo_terciario,
                        fg=self.color_texto
                    ).pack(padx=10, pady=(5, 0))
                    
                    # Total del día
                    color_total = self.color_positivo if total > 0 else self.color_negativo if total < 0 else self.color_neutro
                    tk.Label(
                        frame_tooltip,
                        text=f"Total: ${total:+.2f}",
                        font=("Segoe UI", 11, "bold"),
                        bg=self.color_fondo_terciario,
                        fg=color_total
                    ).pack(padx=10, pady=(2, 5))
                    
                    # Separador
                    tk.Frame(
                        frame_tooltip,
                        height=1,
                        bg=self.color_borde
                    ).pack(fill="x", padx=5, pady=2)
                    
                    # Detalles
                    tk.Label(
                        frame_tooltip,
                        text="Transacciones:",
                        font=("Segoe UI", 9),
                        bg=self.color_fondo_terciario,
                        fg=self.color_texto_secundario
                    ).pack(padx=10, pady=(5, 0))
                    
                    for r in self.datos_por_fecha[fecha]:
                        color_trans = self.color_positivo if r["monto"] > 0 else self.color_negativo if r["monto"] < 0 else self.color_neutro
                        tk.Label(
                            frame_tooltip,
                            text=f"  ${r['monto']:+.2f} {r['moneda']}",
                            font=("Segoe UI", 9),
                            bg=self.color_fondo_terciario,
                            fg=color_trans
                        ).pack(anchor="w", padx=20, pady=1)
                    
                    # Hacer que el tooltip desaparezca después de un tiempo
                    tooltip.after(5000, tooltip.destroy)
                
                # Asignar eventos para el tooltip
                dia_frame.bind(
                    "<Enter>", 
                    lambda e, w=dia_frame, f=fecha_str, d=detalles, t=total_dia: 
                    crear_tooltip(w, f, d, t)
                )
            
            # Ajustar posición para el siguiente día
            columna += 1
            if columna > 6:
                columna = 0
                fila += 1
        
        # Rellenar días vacíos al final del mes
        while columna < 7:
            dia_vacio = tk.Frame(
                grid_frame,
                bg=self.color_fondo_secundario,
                relief="flat",
                height=80
            )
            dia_vacio.grid(row=fila, column=columna, sticky="nsew", padx=1, pady=1)
            columna += 1
    
    def cambiar_mes(self, grid_frame, btn_anterior, btn_siguiente, delta):
        """Cambia el mes en el calendario"""
        mes_texto = self.mes_calendario.get()
        
        # Convertir texto del mes a componentes
        if " " in mes_texto:
            nombre_mes, ano_str = mes_texto.split()
            ano = int(ano_str)
            
            meses = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            
            # Encontrar el índice del mes actual
            mes_index = meses.index(nombre_mes)
            
            # Calcular nuevo mes
            nuevo_mes_index = mes_index + delta
            if nuevo_mes_index >= len(meses):
                nuevo_mes_index = 0
                ano += 1
            elif nuevo_mes_index < 0:
                nuevo_mes_index = len(meses) - 1
                ano -= 1
            
            # Actualizar texto del mes
            self.mes_calendario.set(f"{meses[nuevo_mes_index]} {ano}")
        
        # Actualizar calendario
        self.actualizar_calendario(grid_frame, btn_anterior, btn_siguiente)
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.ventana.mainloop()

if __name__ == "__main__":
    app = AplicacionFinanciera()
    app.ejecutar()