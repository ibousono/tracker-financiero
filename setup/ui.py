import tkinter as tk
from tkinter import ttk, font, messagebox
from datetime import datetime

def crear_interfaz(self):
    """Crea todos los elementos de la interfaz con diseño moderno"""
    
    # Frame principal con gradiente visual
    main_container = tk.Frame(self.ventana, bg=self.color_fondo)
    main_container.pack(fill="both", expand=True, padx=0, pady=0)
    
    # Header con gradiente visual
    header_frame = tk.Frame(
        main_container,
        bg=self.color_fondo_secundario,
        height=80
    )
    header_frame.pack(fill="x", pady=(0, 20))
    header_frame.pack_propagate(False)
    
    # Título moderno
    titulo = tk.Label(
        header_frame,
        text="💰 TRACKER FINANCIERO",
        font=("Segoe UI", 24, "bold"),
        fg=self.color_texto,
        bg=self.color_fondo_secundario
    )
    titulo.pack(side="left", padx=30, pady=20)
    
    # Subtítulo
    subtitulo = tk.Label(
        header_frame,
        text="Controla tus ingresos y gastos",
        font=("Segoe UI", 12),
        fg=self.color_texto_secundario,
        bg=self.color_fondo_secundario
    )
    subtitulo.pack(side="left", padx=(0, 30), pady=20)
    
    # Widget del balance y fecha - EN LA MISMA LÍNEA
    balance_frame = tk.Frame(header_frame, bg=self.color_fondo_secundario)
    balance_frame.pack(side="right", padx=30, pady=20)
    
    # Frame para organizar balance y botón
    info_frame = tk.Frame(balance_frame, bg=self.color_fondo_secundario)
    info_frame.pack()
    
    # Fecha actual - COMPACTA
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    self.fecha_label = tk.Label(
        info_frame,
        text=f"📅 {fecha_actual}",
        font=("Segoe UI", 9),
        fg=self.color_texto_secundario,
        bg=self.color_fondo_secundario
    )
    self.fecha_label.pack(anchor="e", pady=(0, 5))
    
    # Frame para balance y botón
    balance_boton_frame = tk.Frame(info_frame, bg=self.color_fondo_secundario)
    balance_boton_frame.pack(fill="x")
    
    # Balance total
    self.lbl_balance_total = tk.Label(
        balance_boton_frame,
        text="Balance: $0.00",
        font=("Segoe UI", 11, "bold"),
        fg=self.color_acento,
        bg=self.color_fondo_secundario
    )
    self.lbl_balance_total.pack(side="left", padx=(0, 10))
    
    # Botón Balance - NUEVO
    btn_balance = tk.Button(
        balance_boton_frame,
        text="⚙️ Balance",
        command=self.mostrar_configuracion_balance,
        font=("Segoe UI", 9, "bold"),
        bg=self.color_boton_neutral,
        fg="white",
        relief="flat",
        borderwidth=0,
        padx=12,
        pady=6,
        cursor="hand2"
    )
    btn_balance.pack(side="right")
    
    # Efecto hover para el botón
    btn_balance.bind("<Enter>", lambda e, b=btn_balance: self.on_enter(e, b, self.color_boton_neutral))
    btn_balance.bind("<Leave>", lambda e, b=btn_balance: self.on_leave(e, b, self.color_boton_neutral))
    
    # Contenedor principal con dos columnas
    contenido_frame = tk.Frame(main_container, bg=self.color_fondo)
    contenido_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
    
    # Columna izquierda - Panel de entrada
    columna_izquierda = tk.Frame(contenido_frame, bg=self.color_fondo)
    columna_izquierda.pack(side="left", fill="y", padx=(0, 20))
    
    # Panel de entrada de datos
    panel_entrada = tk.Frame(
        columna_izquierda,
        bg=self.color_fondo_secundario,
        relief="flat",
        highlightbackground=self.color_borde,
        highlightthickness=1,
        padx=25,
        pady=25
    )
    panel_entrada.pack(fill="y", pady=(0, 20))
    
    # Título del panel
    tk.Label(
        panel_entrada,
        text="NUEVO REGISTRO",
        font=("Segoe UI", 14, "bold"),
        fg=self.color_acento,
        bg=self.color_fondo_secundario
    ).pack(anchor="w", pady=(0, 20))
    
    # Campos de entrada con diseño moderno
    campos = [
        ("📅 Fecha", "entrada_fecha", datetime.now().strftime("%Y-%m-%d")),
        ("💰 Monto", "entrada_monto", "")
    ]
    
    for i, (texto, attr_name, valor_default) in enumerate(campos):
        # Frame para cada campo
        campo_frame = tk.Frame(panel_entrada, bg=self.color_fondo_secundario)
        campo_frame.pack(fill="x", pady=8)
        
        # Etiqueta
        tk.Label(
            campo_frame,
            text=texto,
            font=("Segoe UI", 11),
            fg=self.color_texto_secundario,
            bg=self.color_fondo_secundario,
            width=15,
            anchor="w"
        ).pack(side="left")
        
        # Campo de entrada
        entrada = tk.Entry(
            campo_frame,
            font=("Segoe UI", 11),
            bg=self.color_fondo_terciario,
            fg=self.color_texto,
            relief="flat",
            insertbackground=self.color_texto,
            borderwidth=0,
            width=20
        )
        entrada.pack(side="left", fill="x", expand=True, padx=(10, 0))
        entrada.insert(0, valor_default)
        
        # Asignar a la instancia
        setattr(self, attr_name, entrada)
        
        # Decoración inferior del campo
        tk.Frame(
            campo_frame,
            height=2,
            bg=self.color_borde
        ).pack(side="left", fill="x", expand=True, padx=(10, 0))
    
    # Selección de moneda - SOLO LAS 3 QUE QUERÉS
    moneda_frame = tk.Frame(panel_entrada, bg=self.color_fondo_secundario)
    moneda_frame.pack(fill="x", pady=15)
    
    tk.Label(
        moneda_frame,
        text="💱 Moneda",
        font=("Segoe UI", 11),
        fg=self.color_texto_secundario,
        bg=self.color_fondo_secundario,
        width=15,
        anchor="w"
    ).pack(side="left")
    
    self.moneda_var = tk.StringVar(value="USD")
    
    # Frame para botones de radio - SOLO LAS 3 MONEDAS
    radio_frame = tk.Frame(moneda_frame, bg=self.color_fondo_secundario)
    radio_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
    
    # SOLO USD, ARS, EUR
    monedas_a_mostrar = [
        ("USD", "💵 USD"),
        ("ARS", "🇦🇷 ARS"), 
        ("EUR", "💶 EUR")
    ]
    
    for moneda, texto in monedas_a_mostrar:
        btn = tk.Radiobutton(
            radio_frame,
            text=texto,
            variable=self.moneda_var,
            value=moneda,
            font=("Segoe UI", 10),
            fg=self.color_texto_secundario,
            bg=self.color_fondo_secundario,
            selectcolor=self.color_fondo_secundario,
            activebackground=self.color_fondo_secundario,
            activeforeground=self.color_acento,
            indicatoron=0,
            width=8,
            relief="raised",
            borderwidth=1
        )
        btn.pack(side="left", padx=(0, 10))
    
    # Botones de acción
    botones_frame = tk.Frame(panel_entrada, bg=self.color_fondo_secundario)
    botones_frame.pack(fill="x", pady=(20, 0))
    
    botones = [
        ("➕ Agregar", self.agregar_registro, self.color_boton_agregar),
        ("🗑️ Borrar", self.borrar_registro, self.color_boton_borrar),
        ("📅 Calendario", self.mostrar_calendario, self.color_boton_calendario)
    ]
    
    for texto, comando, color in botones:
        btn = tk.Button(
            botones_frame,
            text=texto,
            command=comando,
            font=("Segoe UI", 11, "bold"),
            bg=color,
            fg="white",
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Efecto hover
        btn.bind("<Enter>", lambda e, b=btn, c=color: self.on_enter(e, b, c))
        btn.bind("<Leave>", lambda e, b=btn, c=color: self.on_leave(e, b, c))
    
    # Columna derecha - Tabla de datos
    columna_derecha = tk.Frame(contenido_frame, bg=self.color_fondo)
    columna_derecha.pack(side="left", fill="both", expand=True)
    
    # Panel de tabla
    panel_tabla = tk.Frame(
        columna_derecha,
        bg=self.color_fondo_secundario,
        relief="flat",
        highlightbackground=self.color_borde,
        highlightthickness=1
    )
    panel_tabla.pack(fill="both", expand=True)
    
    # Título del panel de tabla
    tk.Label(
        panel_tabla,
        text="📊 REGISTROS RECIENTES",
        font=("Segoe UI", 14, "bold"),
        fg=self.color_acento,
        bg=self.color_fondo_secundario
    ).pack(anchor="w", padx=25, pady=(20, 10))
    
    # Frame para la tabla con scrollbar
    tabla_frame = tk.Frame(panel_tabla, bg=self.color_fondo_secundario)
    tabla_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    # Tabla Treeview con estilo moderno
    self.tabla = ttk.Treeview(
        tabla_frame,
        columns=("Fecha", "Monto", "Moneda", "En tu moneda", "Estado"),
        show="headings",
        height=15
    )
    
    # Configurar estilo de la tabla
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure(
        "Treeview",
        background=self.color_fondo_terciario,
        foreground=self.color_texto,
        fieldbackground=self.color_fondo_terciario,
        borderwidth=0,
        font=("Segoe UI", 10)
    )
    estilo.configure(
        "Treeview.Heading",
        background=self.color_fondo_secundario,
        foreground=self.color_texto,
        relief="flat",
        font=("Segoe UI", 11, "bold")
    )
    estilo.map(
        "Treeview",
        background=[("selected", self.color_acento)],
        foreground=[("selected", "white")]
    )
    
    # Configurar columnas
    columnas = [
        ("Fecha", 100, "📅"),
        ("Monto", 100, "💰"),
        ("Moneda", 70, "💱"),
        ("En tu moneda", 120, "🏠"),
        ("Estado", 90, "📊")
    ]
    
    for col_name, width, emoji in columnas:
        self.tabla.heading(col_name, text=f"{emoji} {col_name}")
        self.tabla.column(col_name, width=width, anchor="center")
    
    # Scrollbar personalizada
    scrollbar = ttk.Scrollbar(
        tabla_frame,
        orient="vertical",
        command=self.tabla.yview
    )
    self.tabla.configure(yscrollcommand=scrollbar.set)
    
    # Posicionar elementos
    self.tabla.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Cargar datos en la tabla
    self.actualizar_tabla()
    
    # Estadísticas
    self.crear_estadisticas()
    
    # Actualizar balance total
    self.actualizar_balance_total()
