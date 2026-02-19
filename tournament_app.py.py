import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog
import os  # Necesario para crear y leer archivos del sistema

# =============================================================================
# CONFIGURACIÓN Y CONSTANTES
# =============================================================================
# Aquí definimos los colores y fuentes que usará toda la aplicación.
# Cambiar un valor aquí actualiza el aspecto en todas las ventanas.

COLOR_FONDO_MAIN = "#1e1e2e"    # Fondo oscuro principal
COLOR_FONDO_SEC  = "#252537"    # Fondo secundario (para tarjetas o paneles)
COLOR_TEXTO      = "#cdd6f4"    # Color de texto (blanco suave)
COLOR_ACENTO     = "#89b4fa"    # Color para destacar (azul claro)
COLOR_EXITO      = "#a6e3a1"    # Verde para acciones positivas
COLOR_PELIGRO    = "#f38ba8"    # Rojo para acciones destructivas o errores
COLOR_BORDE      = "#45475a"    # Color de bordes sutiles

# Fuentes tipográficas para mantener consistencia
FONT_MAIN      = ("Helvetica", 11)
FONT_HEADER    = ("Helvetica", 20, "bold")
FONT_SUBHEADER = ("Helvetica", 14, "bold")

# =============================================================================
# MODELO DE DATOS
# =============================================================================

class Team:
    """
    Representa a un equipo en el torneo.
    Guarda su nombre, ID, puntos acumulados y con quién ha jugado.
    """
    def __init__(self, team_id, name):
        self.id = team_id              # Identificador único (ej. "EQ01")
        self.name = name               # Nombre visible (ej. "Los Tigres")
        self.total_points = 0          # Puntos totales en el torneo
        self.opponents_played = set()  # Conjunto de IDs de equipos contra los que ya jugó
        self.received_bye = False      # Marca si ya recibió una victoria libre (BYE)

    def __repr__(self):
        # Representación en texto para depuración
        return f"Equipo({self.name}, Pts: {self.total_points})"


# =============================================================================
# VISTAS (INTERFAZ GRÁFICA)
# =============================================================================
# Estas clases definen cómo se VE la aplicación. Cada clase es una "Pantalla".

class SetupFrame(ttk.Frame):
    """
    PANTALLA 1: CONFIGURACIÓN
    Aquí se ingresa el nombre del torneo y se registran los equipos.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller # Referencia a la App principal para guardar datos
        
        # --- Contenedor Central ---
        center_frame = ttk.Frame(self, style="Main.TFrame")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título Grande
        label = ttk.Label(center_frame, text="Trugo", style="Header.TLabel", font=("Helvetica", 48, "bold"))
        label.pack(pady=20)

        # --- Sección: Nombre del Torneo ---
        name_frame = ttk.Frame(center_frame, style="Main.TFrame")
        name_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(name_frame, text="Nombre del Torneo:", style="SubHeader.TLabel").pack(pady=(0,5))
        self.tournament_name_entry = ttk.Entry(name_frame, width=40, font=("Helvetica", 12), justify="center")
        self.tournament_name_entry.pack(pady=5, ipady=3)
        
        # Botón para cargar un torneo guardado
        load_btn = ttk.Button(name_frame, text="📂 Cargar Torneo Existente", style="TButton", command=self.controller.load_tournament)
        load_btn.pack(pady=5)

        # --- Sección: Formulario de Ingreso de Equipos ---
        input_card = ttk.Frame(center_frame, style="Card.TFrame", padding=20)
        input_card.pack(fill="x", pady=10)

        grid_frame = ttk.Frame(input_card, style="Card.TFrame")
        grid_frame.pack()

        # Inputs
        ttk.Label(grid_frame, text="Nombre Equipo:", style="Card.TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.team_name_entry = ttk.Entry(grid_frame, width=25)
        self.team_name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(grid_frame, text="ID Equipo (Numérico):", style="Card.TLabel").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.team_id_entry = ttk.Entry(grid_frame, width=25)
        self.team_id_entry.grid(row=1, column=1, padx=10, pady=10)

        add_button = ttk.Button(grid_frame, text="+ Agregar Equipo", style="Primary.TButton", command=self.add_team)
        add_button.grid(row=2, column=0, columnspan=2, pady=15, sticky="ew")

        # Mensajes de Error
        self.error_label = ttk.Label(center_frame, text="", foreground=COLOR_PELIGRO, style="SubHeader.TLabel", font=("Helvetica", 10))
        self.error_label.pack(pady=5)

        # --- Sección: Lista de Equipos ---
        ttk.Label(center_frame, text="Equipos Registrados", style="SubHeader.TLabel").pack(pady=(20, 10))
        
        list_frame = ttk.Frame(center_frame, style="Main.TFrame")
        list_frame.pack(fill="both", expand=True)
        
        # Scrollbar para la lista (útil si hay muchos equipos)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.team_list_box = tk.Listbox(list_frame, height=8, width=50,
                                        bg=COLOR_FONDO_SEC, fg=COLOR_TEXTO,
                                        bd=0, highlightthickness=0,
                                        selectbackground=COLOR_ACENTO, selectforeground=COLOR_FONDO_MAIN,
                                        font=("Consolas", 11),
                                        yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.team_list_box.yview)
        
        self.team_list_box.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón para Corregir/Eliminar
        correction_btn = ttk.Button(center_frame, text="✏️ Corregir/Eliminar Seleccionado", style="Danger.TButton", command=self.correct_team)
        correction_btn.pack(fill="x", pady=5)
        
        # Botón para Iniciar
        start_button = ttk.Button(center_frame, text="Comenzar Torneo →", style="Success.TButton", command=self.start_tournament)
        start_button.pack(pady=30, fill="x", ipady=5)

    def add_team(self):
        """Toma los datos de los inputs y crea un objeto Team."""
        name = self.team_name_entry.get()
        team_id = self.team_id_entry.get()
        
        # 1. Validar campos vacíos
        if not name or not team_id:
            self.error_label.config(text="⚠️ Por favor completa ambos campos.")
            return

        # 2. VALIDACIÓN: Verificar que sea numérico
        if not team_id.isdigit():
            self.error_label.config(text="⚠️ El ID debe ser un número entero (ej: 10, 50).")
            return

        # 3. Validar duplicados
        if team_id in self.controller.teams:
            self.error_label.config(text="⚠️ El ID del equipo ya existe.")
            return

        #4. Validar que el nombre no contenga números
        if any(char.isdigit() for char in name):
            self.error_label.config(text="⚠️ El nombre no debe contener numeros.")
            return
        
        # Crear y guardar equipo
        new_team = Team(team_id, name)
        self.controller.teams[team_id] = new_team
        
        # Actualizar interfaz
        self.team_list_box.insert(tk.END, f" {name}  [ID: {team_id}]")
        self.team_name_entry.delete(0, tk.END)
        self.team_id_entry.delete(0, tk.END)
        self.error_label.config(text="")

    def correct_team(self):
        """Elimina el equipo seleccionado y devuelve sus datos a los inputs."""
        selection = self.team_list_box.curselection()
        if not selection:
            self.error_label.config(text="⚠️ Selecciona un equipo de la lista para corregir.")
            return
        
        index = selection[0]
        item_text = self.team_list_box.get(index)
        
        try:
            # Formato: " {name}  [ID: {team_id}]"
            parts = item_text.split("  [ID: ")
            name = parts[0].strip()
            team_id = parts[1].rstrip("]")
            
            if team_id in self.controller.teams:
                del self.controller.teams[team_id]
            self.team_list_box.delete(index)
            
            self.team_name_entry.delete(0, tk.END)
            self.team_name_entry.insert(0, name)
            self.team_id_entry.delete(0, tk.END)
            self.team_id_entry.insert(0, team_id)
            
            self.error_label.config(text="ℹ️ Equipo eliminado. Corrige los datos y agrégalo.")
        except Exception:
            self.error_label.config(text="⚠️ Error al procesar la selección.")

    def start_tournament(self):
        """Valida e inicia el torneo."""
        t_name = self.tournament_name_entry.get().strip()
        if not t_name:
            self.error_label.config(text="⚠️ Por favor ingresa un nombre para el torneo.")
            return
            
        if len(self.controller.teams) < 2:
            self.error_label.config(text="⚠️ Necesitas al menos 2 equipos.")
            return
            
        self.controller.tournament_name = t_name
        self.error_label.config(text="")
        
        self.controller.generate_pairings()
        self.controller.show_frame(MatchFrame)


class MatchFrame(ttk.Frame):
    """
    PANTALLA 2: PARTIDOS
    Muestra los enfrentamientos de la ronda actual y permite ingresar puntajes.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        
        # --- Barra Superior ---
        top_bar = ttk.Frame(self, style="Main.TFrame", padding=20)
        top_bar.pack(fill="x")
        
        self.header_label = ttk.Label(top_bar, text="Ronda 1", style="Header.TLabel")
        self.header_label.pack(side="left")
        
        end_btn = ttk.Button(top_bar, text="Finalizar Torneo", style="Danger.TButton", 
                           command=lambda: self.controller.show_frame(StandingsFrame))
        end_btn.pack(side="right")

        self.error_label = ttk.Label(self, text="", foreground=COLOR_PELIGRO, style="SubHeader.TLabel", font=("Helvetica", 10))
        self.error_label.pack(pady=5)

        # --- Contenedor Principal (Sistema de GRID para control de anchos) ---
        main_content = ttk.Frame(self, style="Main.TFrame")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Configuración de pesos de columnas: 
        # Columna 0 (Izquierda): peso 3
        # Columna 1 (Derecha): peso 2
        # Total = 5 partes. Derecha ocupa 2/5 = 40%.
        main_content.columnconfigure(0, weight=3)
        main_content.columnconfigure(1, weight=2)
        main_content.rowconfigure(0, weight=1)

        # Columna Izquierda: Lista de Partidos (con scroll)
        left_col = ttk.Frame(main_content, style="Main.TFrame")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 20)) # sticky nsew para estirar

        self.canvas = tk.Canvas(left_col, bg=COLOR_FONDO_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(left_col, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Main.TFrame")

        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.window_id, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Columna Derecha: Ranking en vivo (Más grande ahora)
        right_col = ttk.Frame(main_content, style="Card.TFrame", padding=15)
        right_col.grid(row=0, column=1, sticky="nsew")

        ttk.Label(right_col, text="Posiciones Actuales", style="SideHeader.TLabel").pack(pady=(0, 10))
        
        # Tabla lateral
        cols_small = ('rank', 'name', 'points')
        self.side_tree = ttk.Treeview(right_col, columns=cols_small, show='headings', height=15)
        self.side_tree.heading('rank', text='#')
        self.side_tree.column('rank', width=40, anchor='center')
        self.side_tree.heading('name', text='Equipo')
        self.side_tree.column('name', width=200) # Más ancha para aprovechar el espacio
        self.side_tree.heading('points', text='Pts')
        self.side_tree.column('points', width=60, anchor='center')
        self.side_tree.pack(fill="both", expand=True)

        # Botón para corregir errores manuales
        edit_btn = ttk.Button(right_col, text="✏️ Corregir Puntajes", style="TButton", command=self.edit_scores)
        edit_btn.pack(fill="x", pady=(10, 0))

        # --- Pie de página ---
        footer = ttk.Frame(self, style="Main.TFrame", padding=20)
        footer.pack(side="bottom", fill="x")
        
        self.submit_btn = ttk.Button(footer, text="Enviar Puntajes y Siguiente Ronda →", style="Success.TButton", command=self.submit_scores)
        self.submit_btn.pack(fill="x", ipady=5)

    def display_matches(self):
        """Genera los widgets (etiquetas e inputs) para cada partido."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.controller.match_entry_widgets = []
        self.header_label.config(text=f"Ronda {self.controller.current_round}")
        
        self.canvas.yview_moveto(0)

        # Cabecera de columnas
        header_row = ttk.Frame(self.scrollable_frame, style="Main.TFrame")
        header_row.pack(fill="x", pady=(0, 10))
        ttk.Label(header_row, text="Equipo 1", style="SubHeader.TLabel", width=20, anchor="e").pack(side="left", padx=10)
        ttk.Label(header_row, text="Pts", style="SubHeader.TLabel", width=10, anchor="center").pack(side="left", padx=5)
        ttk.Label(header_row, text="", width=4).pack(side="left") 
        ttk.Label(header_row, text="Pts", style="SubHeader.TLabel", width=10, anchor="center").pack(side="left", padx=5)
        ttk.Label(header_row, text="Equipo 2", style="SubHeader.TLabel", width=20, anchor="w").pack(side="left", padx=10)

        for i, (team1_id, team2_id) in enumerate(self.controller.current_matches):
            team1 = self.controller.teams[team1_id]
            
            match_card = ttk.Frame(self.scrollable_frame, style="Card.TFrame", padding=15)
            match_card.pack(fill="x", pady=5, padx=5)
            
            # Equipo 1
            t1_lbl = ttk.Label(match_card, text=f"{team1.name}\n({team1.total_points} pts)", style="Card.TLabel", justify="right", width=20, anchor="e")
            t1_lbl.pack(side="left", padx=10)
            
            s1_ent = ttk.Entry(match_card, width=5, font=("Helvetica", 14, "bold"), justify="center")
            s1_ent.pack(side="left", padx=5)
            
            ttk.Label(match_card, text="vs", style="Card.TLabel", foreground=COLOR_ACENTO).pack(side="left", padx=10)
            
            s2_ent = ttk.Entry(match_card, width=5, font=("Helvetica", 14, "bold"), justify="center")
            s2_ent.pack(side="left", padx=5)
            
            # Manejo de BYE
            if team2_id == "BYE":
                t2_text = "--- LIBRE ---"
                # Input 1 habilitado, Input 2 deshabilitado en 0
                s2_ent.insert(0, "0"); s2_ent.config(state="disabled") 
                self.controller.match_entry_widgets.append((s1_ent, None, team1_id, "BYE"))
            else:
                team2 = self.controller.teams[team2_id]
                t2_text = f"{team2.name}\n({team2.total_points} pts)"
                self.controller.match_entry_widgets.append((s1_ent, s2_ent, team1_id, team2_id))

            t2_lbl = ttk.Label(match_card, text=t2_text, style="Card.TLabel", justify="left", width=20, anchor="w")
            t2_lbl.pack(side="left", padx=10)

        self.update_sidebar()

    def update_sidebar(self):
        """Actualiza la tabla lateral con las posiciones actuales."""
        for row in self.side_tree.get_children():
            self.side_tree.delete(row)
            
        sorted_teams = sorted(self.controller.teams.values(), key=lambda t: t.total_points, reverse=True)
        
        for i, team in enumerate(sorted_teams):
            self.side_tree.insert("", "end", values=(i+1, team.name, team.total_points))

    def edit_scores(self):
        """Abre ventana emergente para editar puntajes manualmente."""
        popup = tk.Toplevel(self)
        popup.title("Corregir Puntajes Totales")
        popup.geometry("400x500")
        popup.configure(bg=COLOR_FONDO_MAIN)
        popup.grab_set() 

        ttk.Label(popup, text="Editar Puntajes Totales", style="Header.TLabel", font=("Helvetica", 14, "bold")).pack(pady=15)
        ttk.Label(popup, text="Modifica los valores y guarda.", style="Popup.TLabel").pack(pady=(0,10))

        footer_frame = ttk.Frame(popup, style="Main.TFrame")
        footer_frame.pack(side="bottom", fill="x", pady=20, padx=20)

        list_frame = ttk.Frame(popup, style="Main.TFrame")
        list_frame.pack(side="top", fill="both", expand=True, padx=10)

        canvas = tk.Canvas(list_frame, bg=COLOR_FONDO_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Main.TFrame")
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        entries = {}
        sorted_teams = sorted(self.controller.teams.values(), key=lambda t: t.name)
        
        for team in sorted_teams:
            frame = ttk.Frame(scrollable_frame, style="Main.TFrame")
            frame.pack(fill="x", pady=5)
            
            ttk.Label(frame, text=team.name, style="Popup.TLabel", width=20, anchor="e").pack(side="left", padx=10)
            ent = ttk.Entry(frame, width=10, justify="center")
            ent.insert(0, str(team.total_points))
            ent.pack(side="left", padx=10)
            entries[team.id] = ent
            
        def save_corrections():
            try:
                for tid, entry in entries.items():
                    val = entry.get()
                    if not val.strip(): continue
                    self.controller.teams[tid].total_points = int(val)
                self.update_sidebar()
                self.display_matches() 
                self.controller.save_tournament_data()
                messagebox.showinfo("Éxito", "Puntajes actualizados.", parent=popup)
                popup.destroy()
            except ValueError:
                messagebox.showerror("Error", "Solo números enteros.", parent=popup)

        btn_save = ttk.Button(footer_frame, text="Guardar Cambios", command=save_corrections, style="Primary.TButton")
        btn_save.pack(fill="x")

    def submit_scores(self):
        """Procesa los puntajes ingresados y pasa de ronda."""
        round_points = {team_id: 0 for team_id in self.controller.teams}
        try:
            for (entry1, entry2, team1_id, team2_id) in self.controller.match_entry_widgets:
                if team2_id == "BYE":
                    s1 = entry1.get()
                    if not s1:
                        self.error_label.config(text="⚠️ Ingresa el puntaje para el equipo libre.")
                        return
                    round_points[team1_id] += int(s1)
                    continue
                
                s1 = entry1.get()
                s2 = entry2.get()
                if not s1 or not s2:
                    self.error_label.config(text="⚠️ Ingresa los puntajes de todos los partidos.")
                    return
                round_points[team1_id] += int(s1)
                round_points[team2_id] += int(s2)

            for tid, pts in round_points.items():
                self.controller.teams[tid].total_points += pts
            
            self.error_label.config(text="")
            self.controller.generate_pairings()
            self.display_matches()
        except ValueError:
            self.error_label.config(text="⚠️ Puntaje inválido. Solo números enteros.")


class StandingsFrame(ttk.Frame):
    """
    PANTALLA 3: RESULTADOS FINALES
    """
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        
        center = ttk.Frame(self, style="Main.TFrame")
        center.pack(fill="both", expand=True, padx=40, pady=40)

        ttk.Label(center, text="🏆 Tabla de Posiciones Final", style="Header.TLabel").pack(pady=20)

        table_frame = ttk.Frame(center, style="Card.TFrame", padding=2)
        table_frame.pack(fill="both", expand=True)

        cols = ('rank', 'name', 'points', 'played')
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=10)
        
        self.tree.heading('rank', text='#')
        self.tree.column('rank', width=50, anchor='center')
        self.tree.heading('name', text='Equipo')
        self.tree.column('name', width=300)
        self.tree.heading('points', text='Puntos')
        self.tree.column('points', width=80, anchor='center')
        self.tree.heading('played', text='Oponentes')
        self.tree.column('played', width=300, anchor='w')
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        btn_area = ttk.Frame(center, style="Main.TFrame")
        btn_area.pack(pady=30)
        
        ttk.Button(btn_area, text="Comenzar Nuevo Torneo", style="Primary.TButton", 
                   command=self.controller.reset_tournament).pack(ipady=10, padx=20)

    def display_standings(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        sorted_teams = sorted(self.controller.teams.values(), key=lambda t: t.total_points, reverse=True)
        for i, team in enumerate(sorted_teams):
            opponents = [self.controller.teams[oid].name for oid in team.opponents_played if oid in self.controller.teams]
            self.tree.insert("", "end", values=(i+1, team.name, team.total_points, ", ".join(opponents)))


# =============================================================================
# CONTROLADOR PRINCIPAL
# =============================================================================

class TournamentApp(tk.Tk):
    """
    Controlador principal de la aplicación.
    """
    def __init__(self):
        super().__init__()
        self.title("Gestor de Torneos - Trugo")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.80)
        pos_x = (screen_width - window_width) // 2
        pos_y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
        self.configure(bg=COLOR_FONDO_MAIN) 

        self.teams = {}
        self.current_round = 0
        self.current_matches = []
        self.match_entry_widgets = []
        self.tournament_name = "Torneo_Trugo"

        self.setup_styles()

        container = ttk.Frame(self, style="Main.TFrame")
        container.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (SetupFrame, MatchFrame, StandingsFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SetupFrame)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') 

        style.configure(".", background=COLOR_FONDO_MAIN, foreground=COLOR_TEXTO, 
                        font=FONT_MAIN, borderwidth=0)

        style.configure("Main.TFrame", background=COLOR_FONDO_MAIN)
        style.configure("Card.TFrame", background=COLOR_FONDO_SEC, relief="flat")
        style.configure("TLabel", background=COLOR_FONDO_MAIN, foreground=COLOR_TEXTO)
        style.configure("Header.TLabel", font=FONT_HEADER, background=COLOR_FONDO_MAIN, foreground=COLOR_ACENTO)
        style.configure("SubHeader.TLabel", font=FONT_SUBHEADER, background=COLOR_FONDO_MAIN, foreground=COLOR_TEXTO)
        style.configure("Card.TLabel", background=COLOR_FONDO_SEC, foreground=COLOR_TEXTO)
        style.configure("SideHeader.TLabel", font=("Helvetica", 12, "bold"), background=COLOR_FONDO_SEC, foreground=COLOR_ACENTO)
        style.configure("Popup.TLabel", background=COLOR_FONDO_MAIN, foreground=COLOR_TEXTO, font=("Helvetica", 10))

        style.configure("TButton", background=COLOR_FONDO_SEC, foreground=COLOR_TEXTO, borderwidth=0, padding=(10, 10))
        style.map("TButton", background=[('active', COLOR_ACENTO)], foreground=[('active', COLOR_FONDO_MAIN)])

        style.configure("Primary.TButton", background=COLOR_ACENTO, foreground=COLOR_FONDO_MAIN, font=("Helvetica", 11, "bold"))
        style.map("Primary.TButton", background=[('active', COLOR_TEXTO)])

        style.configure("Success.TButton", background=COLOR_EXITO, foreground="#181825", font=("Helvetica", 11, "bold"))
        style.map("Success.TButton", background=[('active', COLOR_TEXTO)])

        style.configure("Danger.TButton", background=COLOR_PELIGRO, foreground="#181825", font=("Helvetica", 11, "bold"))
        style.map("Danger.TButton", background=[('active', COLOR_TEXTO)])

        style.configure("TEntry", fieldbackground=COLOR_FONDO_SEC, foreground=COLOR_TEXTO, insertcolor=COLOR_TEXTO, borderwidth=1, relief="flat", padding=5)
        style.map("TEntry", bordercolor=[('focus', COLOR_ACENTO)])

        style.configure("Treeview", background=COLOR_FONDO_SEC, fieldbackground=COLOR_FONDO_SEC, foreground=COLOR_TEXTO, borderwidth=0, rowheight=30)
        style.map("Treeview", background=[('selected', COLOR_ACENTO)], foreground=[('selected', COLOR_FONDO_MAIN)])
        style.configure("Treeview.Heading", background=COLOR_FONDO_MAIN, foreground=COLOR_TEXTO, font=("Helvetica", 10, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[('active', COLOR_FONDO_SEC)])
        
        style.configure("Vertical.TScrollbar", gripcount=0, background=COLOR_FONDO_SEC, darkcolor=COLOR_FONDO_MAIN, lightcolor=COLOR_FONDO_MAIN, troughcolor=COLOR_FONDO_MAIN, bordercolor=COLOR_FONDO_MAIN, arrowcolor=COLOR_TEXTO)

    def show_frame(self, cont):
        frame = self.frames[cont]
        if cont == StandingsFrame:
            frame.display_standings()
        elif cont == MatchFrame:
            frame.display_matches()
        frame.tkraise()

    def reset_tournament(self):
        self.teams = {}
        self.current_round = 0
        self.current_matches = []
        self.match_entry_widgets = []
        self.tournament_name = "Torneo_Trugo"
        
        setup = self.frames[SetupFrame]
        setup.team_list_box.delete(0, tk.END)
        setup.tournament_name_entry.delete(0, tk.END)
        setup.tournament_name_entry.insert(0, "")
        setup.error_label.config(text="")
        
        self.show_frame(SetupFrame)

    def save_tournament_data(self):
        try:
            safe_name = "".join([c for c in self.tournament_name if c.isalnum() or c in (' ', '_', '-')]).strip()
            if not safe_name: safe_name = "Torneo_Trugo"
            filename = f"{safe_name}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"=========================================\n")
                f.write(f"   {self.tournament_name}\n")
                f.write(f"   ESTADO DEL TORNEO: RONDA {self.current_round}\n")
                f.write(f"=========================================\n\n")
                
                sorted_teams = sorted(self.teams.values(), key=lambda t: t.total_points, reverse=True)
                for team in sorted_teams:
                    f.write(f"EQUIPO: {team.name} (ID: {team.id})\n")
                    f.write(f"  > Puntos Totales: {team.total_points}\n")
                    
                    rival_names = [self.teams[oid].name for oid in team.opponents_played if oid in self.teams]
                    rivals_str = ", ".join(rival_names) if rival_names else "Ninguno"
                    f.write(f"  > Rivales: {rivals_str}\n")
                    
                    rival_ids_str = ",".join(list(team.opponents_played))
                    f.write(f"  > SYSTEM_IDS_RIVALES: {rival_ids_str}\n")
                    f.write("-" * 40 + "\n")
                
                f.write("\n=== SYSTEM_PAREOS_ACTUALES ===\n")
                for t1, t2 in self.current_matches:
                    f.write(f"{t1},{t2}\n")
            
            print(f"Datos guardados exitosamente en {filename}")
        except Exception as e:
            print(f"Error al guardar datos: {e}")

    def load_tournament(self):
        filename = filedialog.askopenfilename(title="Seleccionar archivo de torneo", filetypes=[("Archivos de Texto", "*.txt")])
        if not filename: return
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            self.teams = {}
            self.current_matches = []
            
            self.tournament_name = lines[1].strip()
            round_line = lines[2].strip()
            if "RONDA" in round_line:
                self.current_round = int(round_line.split("RONDA")[-1].strip())
            else:
                raise ValueError("Formato de ronda inválido")
            
            current_team = None
            parsing_matches = False
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                if line.startswith("=== SYSTEM_PAREOS_ACTUALES ==="):
                    parsing_matches = True
                    continue
                
                if parsing_matches:
                    if "," in line:
                        t1, t2 = line.split(",")
                        self.current_matches.append((t1, t2))
                    continue

                if line.startswith("EQUIPO:"):
                    parts = line.split("(ID: ")
                    name = parts[0].replace("EQUIPO: ", "").strip()
                    tid = parts[1].replace(")", "").strip()
                    current_team = Team(tid, name)
                    self.teams[tid] = current_team
                
                elif line.startswith("> Puntos Totales:"):
                    if current_team:
                        current_team.total_points = int(line.split(":")[1].strip())
                        
                elif line.startswith("> SYSTEM_IDS_RIVALES:"):
                    if current_team:
                        ids_str = line.split(":")[1].strip()
                        if ids_str:
                            current_team.opponents_played = set(ids_str.split(","))

            if not self.teams: raise ValueError("No se encontraron equipos.")
            
            self.show_frame(MatchFrame)
            self.frames[MatchFrame].display_matches()
            messagebox.showinfo("Carga Exitosa", f"Torneo '{self.tournament_name}' cargado en la Ronda {self.current_round}.")

        except Exception as e:
            messagebox.showerror("Error de Carga", f"No se pudo cargar el archivo.\nDetalle: {e}")

    def generate_pairings(self):
        self.current_round += 1
        new_matches = []
        
        sorted_teams = sorted(self.teams.values(), key=lambda t: t.total_points, reverse=True)
        unpaired_teams = list(sorted_teams)
        
        if len(unpaired_teams) % 2 != 0:
            bye_team = None
            for team in reversed(unpaired_teams):
                if not team.received_bye:
                    bye_team = team
                    break
            if bye_team is None:
                bye_team = unpaired_teams[-1]
                
            bye_team.received_bye = True
            new_matches.append((bye_team.id, "BYE"))
            unpaired_teams.remove(bye_team)

        while unpaired_teams:
            team1 = unpaired_teams.pop(0)
            found_opponent = False
            for i, team2 in enumerate(unpaired_teams):
                if team2.id not in team1.opponents_played:
                    opponent = unpaired_teams.pop(i)
                    new_matches.append((team1.id, opponent.id))
                    team1.opponents_played.add(opponent.id)
                    opponent.opponents_played.add(team1.id)
                    found_opponent = True
                    break
            
            if not found_opponent and unpaired_teams:
                opponent = unpaired_teams.pop(0)
                new_matches.append((team1.id, opponent.id))
                team1.opponents_played.add(opponent.id)
                opponent.opponents_played.add(team1.id)

        self.current_matches = new_matches
        self.save_tournament_data()

if __name__ == "__main__":
    app = TournamentApp()
    app.mainloop()