import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
import calendar

from setup.facade import configurar_app
#Definicion de constantes
FUENTE = "Segoe UI"

class AplicacionFinanciera:
    def __init__(self):
        # configura la ventana, los colores y carga los datos 
        configurar_app(self)

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
    

    #Manejo de registros
    def agregar_registro(self):
        """Agrega un nuevo registro con conversión automática"""
        try:
            fecha = self.entrada_fecha.get()
            monto = float(self.entrada_monto.get())
            moneda = self.moneda_var.get()
            
            # Validar fecha
            datetime.strptime(fecha, "%Y-%m-%d")
            
            # Obtener moneda principal
            moneda_principal = self.configuracion.get("moneda_principal", "ARS")
            
            # Convertir a moneda principal
            monto_convertido = self.converter.convert(monto, moneda, moneda_principal)
            
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
                "monto_convertido": monto_convertido,
                "moneda_principal": moneda_principal,
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


    #Panel de estadisticas (el que esta en la parte inferior)
    def crear_estadisticas(self):
        """Crea el panel de estadísticas"""
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
            font=(FUENTE, 14, "bold"),
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
                font=(FUENTE, 10),
                fg=self.color_texto_secundario,
                bg=self.color_fondo_secundario
            ).pack(anchor="w", pady=(0, 5))
            
            # Valor de la métrica
            valor_label = tk.Label(
                metric_frame,
                text=valor_default,
                font=(FUENTE, 18, "bold"),
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


    #CALENDARIO
    def mostrar_calendario(self):
        """Muestra un calendario mensual con las ganancias por día"""

        if not hasattr(self, 'tooltip_actual'):
            self.tooltip_actual = None

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
            font=(FUENTE, 16, "bold"),
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
            font=(FUENTE, 12, "bold"),
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
            font=(FUENTE, 14, "bold"),
            fg=self.color_texto,
            bg=self.color_fondo_secundario
        )
        lbl_mes.pack(side="left", padx=20)
        
        # Botón siguiente
        btn_siguiente = tk.Button(
            controles_frame,
            text="→",
            font=(FUENTE, 12, "bold"),
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
                font=(FUENTE, 10, "bold"),
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
                font=(FUENTE, 9),
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
        primer_dia_semana, num_dias = calendar.monthrange(ano, mes)
        
        # Ajustar primer_dia para que 0=Lunes (calendario usa 0=Lunes por defecto en Python)
        # calendar.monthrange devuelve: 0=Lunes, 1=Martes, ..., 6=Domingo
        
        # Llenar el calendario
        fila = 0
        columna = primer_dia_semana
        
        # Rellenar días vacíos al inicio del mes
        for i in range(primer_dia_semana):
            dia_vacio = tk.Frame(
                grid_frame,
                bg=self.color_fondo_secundario,
                relief="flat",
                height=80
            )
            dia_vacio.grid(row=fila, column=i, sticky="nsew", padx=1, pady=1)
            grid_frame.rowconfigure(fila, weight=1)
            grid_frame.columnconfigure(i, weight=1)
        
        # Organizar datos por fecha (asegurarnos de que esté actualizado)
        self.datos_por_fecha = {}
        for registro in self.datos:
            fecha = registro["fecha"]
            if fecha not in self.datos_por_fecha:
                self.datos_por_fecha[fecha] = []
            self.datos_por_fecha[fecha].append(registro)
        
        # Variable para almacenar tooltips
        self.tooltips = {}
        
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
            dia_frame.grid_propagate(False)
            
            # Configurar el grid para que se expanda
            grid_frame.rowconfigure(fila, weight=1)
            grid_frame.columnconfigure(columna, weight=1)
            
            # Número del día
            numero_color = "white" if es_hoy else self.color_texto
            lbl_numero = tk.Label(
                dia_frame,
                text=str(dia),
                font=(FUENTE, 10, "bold"),
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
                    font=(FUENTE, 9, "bold"),
                    fg=color,
                    bg=bg_color
                )
                lbl_total.pack(fill="x", padx=5, pady=2)
                
                # Función para crear tooltip
                def crear_tooltip(event, fecha=fecha_str, total=total_dia, widget=dia_frame):
                    # Destruir tooltip existente si hay uno
                    if hasattr(self, 'tooltip_actual') and self.tooltip_actual:
                        try:
                            self.tooltip_actual.destroy()
                        except:
                            pass
                    
                    # Crear nuevo tooltip
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
                        font=(FUENTE, 10, "bold"),
                        bg=self.color_fondo_terciario,
                        fg=self.color_texto
                    ).pack(padx=10, pady=(5, 0))
                    
                    # Total del día
                    color_total = self.color_positivo if total > 0 else self.color_negativo if total < 0 else self.color_neutro
                    tk.Label(
                        frame_tooltip,
                        text=f"Total: ${total:+.2f}",
                        font=(FUENTE, 11, "bold"),
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
                    if fecha in self.datos_por_fecha:
                        tk.Label(
                            frame_tooltip,
                            text="Transacciones:",
                            font=(FUENTE, 9),
                            bg=self.color_fondo_terciario,
                            fg=self.color_texto_secundario
                        ).pack(padx=10, pady=(5, 0))
                        
                        for r in self.datos_por_fecha[fecha]:
                            color_trans = self.color_positivo if r["monto"] > 0 else self.color_negativo if r["monto"] < 0 else self.color_neutro
                            tk.Label(
                                frame_tooltip,
                                text=f"  ${r['monto']:+.2f} {r['moneda']}",
                                font=(FUENTE, 9),
                                bg=self.color_fondo_terciario,
                                fg=color_trans
                            ).pack(anchor="w", padx=20, pady=1)
                    
                    # Guardar referencia al tooltip
                    self.tooltip_actual = tooltip
                    
                    # Función para destruir tooltip
                    def destruir_tooltip(event=None):
                        if hasattr(self, 'tooltip_actual') and self.tooltip_actual:
                            try:
                                self.tooltip_actual.destroy()
                                self.tooltip_actual = None
                            except:
                                pass
                    
                    # Configurar eventos para cerrar tooltip
                    tooltip.bind("<Leave>", destruir_tooltip)
                    frame_tooltip.bind("<Leave>", destruir_tooltip)
                    
                    # También cerrar después de 3 segundos por si acaso
                    tooltip.after(3000, destruir_tooltip)
                
                # Función para ocultar tooltip
                def ocultar_tooltip(event=None):
                    if hasattr(self, 'tooltip_actual') and self.tooltip_actual:
                        try:
                            self.tooltip_actual.destroy()
                            self.tooltip_actual = None
                        except:
                            pass
                
                # Asignar eventos al frame del día
                dia_frame.bind("<Enter>", crear_tooltip)
                dia_frame.bind("<Leave>", ocultar_tooltip)
                lbl_numero.bind("<Enter>", crear_tooltip)
                lbl_numero.bind("<Leave>", ocultar_tooltip)
                if 'lbl_total' in locals():
                    lbl_total.bind("<Enter>", crear_tooltip)
                    lbl_total.bind("<Leave>", ocultar_tooltip)
            
            # Ajustar posición para el siguiente día
            columna += 1
            if columna > 6:
                columna = 0
                fila += 1
        
        # Rellenar días vacíos al final del mes
        ultima_fila = fila
        if columna < 7:
            for i in range(columna, 7):
                dia_vacio = tk.Frame(
                    grid_frame,
                    bg=self.color_fondo_secundario,
                    relief="flat",
                    height=80
                )
                dia_vacio.grid(row=ultima_fila, column=i, sticky="nsew", padx=1, pady=1)
                grid_frame.rowconfigure(ultima_fila, weight=1)
                grid_frame.columnconfigure(i, weight=1)
    
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
    

    #Monedas y emoticones
    def mostrar_todas_monedas(self):
        """Muestra todas las monedas disponibles en un menú emergente"""
        if not hasattr(self, 'converter'):
            return
        
        monedas = self.converter.get_all_currencies()
        
        menu = tk.Menu(self.ventana, tearoff=0, bg=self.color_fondo_secundario, fg=self.color_texto)
        
        for moneda in monedas:
            emoji = self.obtener_emoji_moneda(moneda)
            menu.add_command(
                label=f"{emoji} {moneda}", 
                command=lambda m=moneda: self.seleccionar_moneda(m)
            )
        
        # Mostrar el menú cerca del botón
        try:
            menu.tk_popup(self.ventana.winfo_pointerx(), self.ventana.winfo_pointery())
        finally:
            menu.grab_release()

    def obtener_emoji_moneda(self, moneda):
        """Devuelve el emoji correspondiente a la moneda"""
        emojis = {
            "USD": "💵",
            "ARS": "🇦🇷",
            "EUR": "💶",
        }
        return emojis.get(moneda, "💱")

    def seleccionar_moneda(self, moneda):
        """Selecciona una moneda del menú"""
        self.moneda_var.set(moneda)


    #Esta es la ventana de configuracion del balance(la que aparece al apretar el boton de balance)
    def mostrar_configuracion_balance(self):
        """Muestra la ventana de configuración del balance"""
        config_window = tk.Toplevel(self.ventana)
        config_window.title("⚙️ Configurar Balance")
        config_window.geometry("800x800")
        config_window.configure(bg=self.color_fondo)
        config_window.resizable(False, False)
        
        # Centrar ventana
        config_window.transient(self.ventana)
        config_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(config_window, bg=self.color_fondo, padx=30, pady=25)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        tk.Label(
            main_frame,
            text="⚙️ CONFIGURAR BALANCE",
            font=(FUENTE, 16, "bold"),
            fg=self.color_acento,
            bg=self.color_fondo
        ).pack(pady=(0, 25))
        
        # ===== SECCIÓN 1: BALANCE TOTAL ACTUAL =====
        tk.Label(
            main_frame,
            text="📊 BALANCE TOTAL ACTUAL",
            font=(FUENTE, 12, "bold"),
            fg=self.color_texto,
            bg=self.color_fondo
        ).pack(anchor="w", pady=(0, 10))
        
        # Calcular balance total actual (inicial + transacciones)
        moneda_actual = self.configuracion.get("moneda_principal", "ARS")
        balance_inicial = float(self.configuracion.get("balance_total", 0))
        
        # Calcular total de transacciones convertidas
        total_transacciones = 0
        for registro in self.datos:
            monto = float(registro.get("monto", 0))
            moneda_registro = registro.get("moneda", "USD")
            
            # Convertir si es necesario
            if moneda_registro != moneda_actual:
                if hasattr(self, 'converter'):
                    monto_convertido = self.converter.convert(monto, moneda_registro, moneda_actual)
                else:
                    # Conversión simple si no hay converter
                    tasas = {"USD": 1.0, "ARS": 950.0, "EUR": 0.92}
                    if moneda_registro in tasas and moneda_actual in tasas:
                        monto_convertido = monto * (tasas[moneda_actual] / tasas[moneda_registro])
                    else:
                        monto_convertido = monto
            else:
                monto_convertido = monto
            
            total_transacciones += monto_convertido
        
        # Balance total actual
        balance_total_actual = balance_inicial + total_transacciones
        
        # Frame para mostrar balances
        balances_frame = tk.Frame(main_frame, bg=self.color_fondo_secundario, padx=20, pady=15)
        balances_frame.pack(fill="x", pady=(0, 20))
        
        # Balance inicial
        tk.Label(
            balances_frame,
            text="Balance inicial:",
            font=(FUENTE, 10),
            fg=self.color_texto_secundario,
            bg=self.color_fondo_secundario
        ).pack(anchor="w")
        
        tk.Label(
            balances_frame,
            text=f"${balance_inicial:+,.2f} {moneda_actual}",
            font=(FUENTE, 11),
            fg=self.color_texto_secundario,
            bg=self.color_fondo_secundario
        ).pack(anchor="w", pady=(2, 10))
        
        # Transacciones
        tk.Label(
            balances_frame,
            text=f"Transacciones ({len(self.datos)}):",
            font=(FUENTE, 10),
            fg=self.color_texto_secundario,
            bg=self.color_fondo_secundario
        ).pack(anchor="w")
        
        color_transacciones = self.color_positivo if total_transacciones >= 0 else self.color_negativo
        tk.Label(
            balances_frame,
            text=f"${total_transacciones:+,.2f} {moneda_actual}",
            font=(FUENTE, 11),
            fg=color_transacciones,
            bg=self.color_fondo_secundario
        ).pack(anchor="w", pady=(2, 10))
        
        # Separador
        tk.Frame(
            balances_frame,
            height=1,
            bg=self.color_borde
        ).pack(fill="x", pady=5)
        
        # Balance total actual
        tk.Label(
            balances_frame,
            text="Balance total actual:",
            font=(FUENTE, 11, "bold"),
            fg=self.color_texto,
            bg=self.color_fondo_secundario
        ).pack(anchor="w")
        
        color_total = self.color_positivo if balance_total_actual >= 0 else self.color_negativo
        tk.Label(
            balances_frame,
            text=f"${balance_total_actual:+,.2f} {moneda_actual}",
            font=(FUENTE, 16, "bold"),
            fg=color_total,
            bg=self.color_fondo_secundario
        ).pack(anchor="w", pady=(5, 0))
        
        # ===== SECCIÓN 2: CONFIGURAR NUEVO BALANCE INICIAL =====
        tk.Label(
            main_frame,
            text="⚙️ CONFIGURAR NUEVO BALANCE INICIAL",
            font=(FUENTE, 12, "bold"),
            fg=self.color_texto,
            bg=self.color_fondo
        ).pack(anchor="w", pady=(20, 10))
        
        # Frame para nueva configuración
        new_frame = tk.Frame(main_frame, bg=self.color_fondo, pady=10)
        new_frame.pack(fill="x")
        
        # Moneda principal
        tk.Label(
            new_frame,
            text="Tu moneda principal:",
            font=(FUENTE, 11),
            fg=self.color_texto_secundario,
            bg=self.color_fondo
        ).pack(anchor="w", pady=(5, 10))
        
        moneda_principal_var = tk.StringVar(value=moneda_actual)
        
        moneda_frame = tk.Frame(new_frame, bg=self.color_fondo)
        moneda_frame.pack(anchor="w", fill="x", pady=(0, 20))
        
        # Botones de radio para moneda
        monedas = [("USD", "💵 USD"), ("ARS", "🇦🇷 ARS"), ("EUR", "💶 EUR")]
        
        for moneda, texto in monedas:
            btn = tk.Radiobutton(
                moneda_frame,
                text=texto,
                variable=moneda_principal_var,
                value=moneda,
                font=(FUENTE, 10),
                fg=self.color_texto_secundario,
                bg=self.color_fondo,
                selectcolor=self.color_fondo,
                activebackground=self.color_fondo,
                activeforeground=self.color_acento,
                indicatoron=0,
                width=10,
                relief="raised",
                borderwidth=1
            )
            btn.pack(side="left", padx=(0, 10))
        
        # Nuevo balance inicial
        tk.Label(
            new_frame,
            text="Nuevo balance inicial:",
            font=(FUENTE, 11),
            fg=self.color_texto_secundario,
            bg=self.color_fondo
        ).pack(anchor="w", pady=(5, 10))
        
        # Frame para entrada
        entrada_frame = tk.Frame(new_frame, bg=self.color_fondo)
        entrada_frame.pack(anchor="w", fill="x")
        
        # Campo para nuevo balance
        nuevo_balance_var = tk.StringVar()
        nuevo_balance_entry = tk.Entry(
            entrada_frame,
            textvariable=nuevo_balance_var,
            font=(FUENTE, 14),
            bg=self.color_fondo_terciario,
            fg=self.color_texto,
            relief="flat",
            insertbackground=self.color_texto,
            borderwidth=1,
            width=25
        )
        nuevo_balance_entry.pack(side="left", padx=(0, 10))
        
        # Label para moneda
        moneda_label = tk.Label(
            entrada_frame,
            text=moneda_principal_var.get(),
            font=(FUENTE, 14),
            fg=self.color_texto,
            bg=self.color_fondo
        )
        moneda_label.pack(side="left")
        
        # Instrucción
        tk.Label(
            new_frame,
            text="Este es el dinero que tienes actualmente, sin contar las transacciones.",
            font=(FUENTE, 9),
            fg=self.color_texto_secundario,
            bg=self.color_fondo
        ).pack(anchor="w", pady=(5, 0))
        
        # Función para actualizar label de moneda
        def actualizar_moneda_label(*args):
            moneda_label.config(text=moneda_principal_var.get())
        
        moneda_principal_var.trace("w", actualizar_moneda_label)
        
        # ===== SECCIÓN 3: BOTONES =====
        botones_frame = tk.Frame(main_frame, bg=self.color_fondo)
        botones_frame.pack(fill="x", pady=(25, 0))
        
        # Función para guardar cambios
        def guardar_cambios():
            try:
                # Obtener y validar el nuevo balance
                nuevo_balance_str = nuevo_balance_var.get()
                if not nuevo_balance_str:
                    messagebox.showwarning("Advertencia", "⚠️ Por favor, ingresa un valor para el balance inicial")
                    nuevo_balance_entry.focus_set()
                    return
                
                nuevo_balance = float(nuevo_balance_str)
                moneda_principal = moneda_principal_var.get()
                
                # Actualizar configuración
                self.configuracion["moneda_principal"] = moneda_principal
                self.configuracion["balance_total"] = nuevo_balance
                
                # Guardar en el archivo config.json
                try:
                    with open("config.json", "w") as f:
                        json.dump(self.configuracion, f, indent=2)
                except Exception as e:
                    messagebox.showerror("Error", f"❌ Error guardando configuración: {str(e)}")
                    return
                
                # Actualizar la interfaz
                self.actualizar_balance_total()
                self.actualizar_tabla()
                
                messagebox.showinfo("Éxito", "✅ Balance inicial actualizado correctamente\n\nRecuerda: El balance total incluye este valor más todas tus transacciones.")
                config_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "❌ Por favor, ingresa un número válido")
                nuevo_balance_entry.focus_set()
            except Exception as e:
                messagebox.showerror("Error", f"❌ Error inesperado: {str(e)}")
        
        # Botón Guardar
        btn_guardar = tk.Button(
            botones_frame,
            text="💾 GUARDAR CAMBIOS",
            command=guardar_cambios,
            font=(FUENTE, 12, "bold"),
            bg=self.color_boton_agregar,
            fg="white",
            relief="flat",
            padx=30,
            pady=12,
            cursor="hand2"
        )
        btn_guardar.pack(side="left", padx=(0, 15))
        
        # Botón Cancelar
        btn_cancelar = tk.Button(
            botones_frame,
            text="Cancelar",
            command=config_window.destroy,
            font=(FUENTE, 11),
            bg=self.color_fondo_terciario,
            fg=self.color_texto,
            relief="flat",
            padx=30,
            pady=10,
            cursor="hand2"
        )
        btn_cancelar.pack(side="left")
        
        # Efectos hover
        btn_guardar.bind("<Enter>", lambda e, b=btn_guardar: self.on_enter(e, b, self.color_boton_agregar))
        btn_guardar.bind("<Leave>", lambda e, b=btn_guardar: self.on_leave(e, b, self.color_boton_agregar))
        btn_cancelar.bind("<Enter>", lambda e, b=btn_cancelar: self.on_enter(e, b, self.color_fondo_terciario))
        btn_cancelar.bind("<Leave>", lambda e, b=btn_cancelar: self.on_leave(e, b, self.color_fondo_terciario))
        
        # Poner el balance actual en el campo de entrada
        nuevo_balance_var.set(str(balance_inicial))
        
        # Seleccionar todo el texto en el campo de entrada
        nuevo_balance_entry.focus_set()
        nuevo_balance_entry.select_range(0, tk.END)
        
        # También permitir guardar con Enter
        nuevo_balance_entry.bind("<Return>", lambda e: guardar_cambios())

    def actualizar_balance_total(self):
        """Actualiza el display del balance total"""
        if not hasattr(self, 'lbl_balance_total'):
            return
        
        try:
            # Obtener configuración actual
            moneda_principal = self.configuracion.get("moneda_principal", "ARS")
            balance_inicial = float(self.configuracion.get("balance_total", 0))
            
            # Calcular total de transacciones convertidas a la moneda principal
            total_transacciones = 0
            for registro in self.datos:
                monto = float(registro.get("monto", 0))
                moneda_registro = registro.get("moneda", "USD")
                
                # Convertir si las monedas son diferentes
                if moneda_registro != moneda_principal:
                    # Usar el convertidor si está disponible
                    if hasattr(self, 'converter'):
                        monto_convertido = self.converter.convert(monto, moneda_registro, moneda_principal)
                    else:
                        # Conversión manual simple
                        tasas = {"USD": 1.0, "ARS": 950.0, "EUR": 0.92}
                        if moneda_registro in tasas and moneda_principal in tasas:
                            # Convertir a USD primero, luego a la moneda destino
                            monto_usd = monto / tasas[moneda_registro]
                            monto_convertido = monto_usd * tasas[moneda_principal]
                        else:
                            monto_convertido = monto  # Si no conocemos la tasa
                else:
                    monto_convertido = monto
                
                total_transacciones += monto_convertido
            
            # Calcular balance total
            balance_total = balance_inicial + total_transacciones
            
            # Formatear el texto
            if balance_total >= 0:
                texto_balance = f"${balance_total:+,.2f} {moneda_principal}"
                color = self.color_positivo
            else:
                texto_balance = f"${balance_total:+,.2f} {moneda_principal}"
                color = self.color_negativo
            
            # Actualizar el label
            self.lbl_balance_total.config(text=f"Balance: {texto_balance}", fg=color)
            
        except Exception as e:
            print(f"Error en actualizar_balance_total: {e}")
            # Mostrar valor por defecto
            self.lbl_balance_total.config(text="Balance: $0.00 ARS", fg=self.color_acento)


    # Refrescar tabla y guardar datos
    def actualizar_tabla(self):
        """Actualiza la tabla con los datos actuales incluyendo conversiones"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Ordenar datos por fecha (más reciente primero)
        datos_ordenados = sorted(self.datos, key=lambda x: x["fecha"], reverse=True)
        
        # Obtener moneda principal
        moneda_principal = self.configuracion.get("moneda_principal", "ARS")
        
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
            
            # Calcular conversión si no existe
            if "monto_convertido" not in registro:
                registro["monto_convertido"] = self.converter.convert(
                    registro["monto"], 
                    registro["moneda"], 
                    moneda_principal
                )
            
            self.tabla.insert(
                "",
                "end",
                values=(
                    registro["fecha"],
                    f"${registro['monto']:+.2f}",
                    registro["moneda"],
                    f"${registro['monto_convertido']:+.2f} {moneda_principal}",
                    registro["estado"]
                ),
                tags=tags
            )
        
        # Configurar colores
        self.tabla.tag_configure("positivo", foreground=self.color_positivo)
        self.tabla.tag_configure("negativo", foreground=self.color_negativo)
        self.tabla.tag_configure("neutro", foreground=self.color_neutro)
        
        # Actualizar balance total
        self.actualizar_balance_total()

    def aplicarCambios(self):
        """Aplica los cambios: guarda datos, actualiza tabla y estadísticas"""
        self.guardar_datos()
        self.actualizar_tabla()
        self.actualizar_estadisticas()
        self.actualizar_balance_total()

    def guardar_datos(self):
        """Guarda los datos en el archivo JSON"""
        with open("datos.json", "w") as archivo:
            json.dump(self.datos, archivo, indent=2)
        
        # También guardar configuración
        from setup.estado import guardar_configuracion
        guardar_configuracion(self)
        
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.ventana.mainloop()

if __name__ == "__main__":
    app = AplicacionFinanciera()
    app.ejecutar()