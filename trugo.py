import tkinter as tk
from tkinter import ttk, font
import os  # Importado para manejo de archivos

# --- Clase de Datos del Equipo ---
class Team:
    def __init__(self, team_id, name):
        self.id = team_id
        self.name = name
        self.total_points = 0  # Entero
        self.opponents_played = set()
        self.received_bye = False

    def __repr__(self):
        return f"Team({self.name}, Pts: {self.total_points})"

# --- Constantes de Estilo ---
COLOR_BG_MAIN = "#1e1e2e"    # Fondo oscuro
COLOR_BG_SEC = "#252537"     # Ligeramente más claro para paneles/inputs
COLOR_TEXT = "#cdd6f4"       # Texto blanco roto
COLOR_ACCENT = "#89b4fa"     # Azul claro para acentos
COLOR_SUCCESS = "#a6e3a1"    # Verde
COLOR_DANGER = "#f38ba8"     # Rojo
COLOR_BORDER = "#45475a"     # Color del borde

FONT_MAIN = ("Helvetica", 11)
FONT_HEADER = ("Helvetica", 20, "bold")
FONT_SUBHEADER = ("Helvetica", 14, "bold")

# --- Clase Principal de la Aplicación ---
class TournamentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Torneos - Trugo")
        self.geometry("1100x700") # Un poco más ancho para el panel lateral
        self.configure(bg=COLOR_BG_MAIN) 

        # --- Estado de la App ---
        self.teams = {} 
        self.current_round = 0
        self.current_matches = []
        self.match_entry_widgets = []

        # --- Configuración de Estilos ---
        self.setup_styles()

        # --- Contenedor de Frames ---
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
        """Configura un tema oscuro moderno usando estilos ttk estándar."""
        style = ttk.Style()
        style.theme_use('clam') 

        # Valores predeterminados generales
        style.configure(".", 
                        background=COLOR_BG_MAIN, 
                        foreground=COLOR_TEXT, 
                        font=FONT_MAIN,
                        borderwidth=0)

        # Frames
        style.configure("Main.TFrame", background=COLOR_BG_MAIN)
        style.configure("Card.TFrame", background=COLOR_BG_SEC, relief="flat")

        # Etiquetas (Labels)
        style.configure("TLabel", background=COLOR_BG_MAIN, foreground=COLOR_TEXT)
        style.configure("Header.TLabel", font=FONT_HEADER, background=COLOR_BG_MAIN, foreground=COLOR_ACCENT)
        style.configure("SubHeader.TLabel", font=FONT_SUBHEADER, background=COLOR_BG_MAIN, foreground=COLOR_TEXT)
        style.configure("Card.TLabel", background=COLOR_BG_SEC, foreground=COLOR_TEXT)
        style.configure("SideHeader.TLabel", font=("Helvetica", 12, "bold"), background=COLOR_BG_SEC, foreground=COLOR_ACCENT)

        # Botones
        # Botón Estándar
        style.configure("TButton", 
                        background=COLOR_BG_SEC, 
                        foreground=COLOR_TEXT, 
                        borderwidth=0, 
                        focuscolor=COLOR_ACCENT,
                        padding=(10, 10))
        style.map("TButton", 
                  background=[('active', COLOR_ACCENT), ('pressed', COLOR_ACCENT)],
                  foreground=[('active', COLOR_BG_MAIN), ('pressed', COLOR_BG_MAIN)])

        # Botón Primario (Azul)
        style.configure("Primary.TButton", 
                        background=COLOR_ACCENT, 
                        foreground=COLOR_BG_MAIN, 
                        font=("Helvetica", 11, "bold"))
        style.map("Primary.TButton", 
                  background=[('active', COLOR_TEXT)],
                  foreground=[('active', COLOR_BG_MAIN)])

        # Botón Éxito (Verde)
        style.configure("Success.TButton", 
                        background=COLOR_SUCCESS, 
                        foreground="#181825", 
                        font=("Helvetica", 11, "bold"))
        style.map("Success.TButton", background=[('active', COLOR_TEXT)])

        # Botón Peligro (Rojo)
        style.configure("Danger.TButton", 
                        background=COLOR_DANGER, 
                        foreground="#181825",
                        font=("Helvetica", 11, "bold"))
        style.map("Danger.TButton", background=[('active', COLOR_TEXT)])

        # Entradas de texto (Inputs)
        style.configure("TEntry", 
                        fieldbackground=COLOR_BG_SEC, 
                        foreground=COLOR_TEXT, 
                        insertcolor=COLOR_TEXT, 
                        borderwidth=1,
                        relief="flat",
                        padding=5)
        style.map("TEntry", bordercolor=[('focus', COLOR_ACCENT)])

        # Treeview (Tabla)
        style.configure("Treeview", 
                        background=COLOR_BG_SEC,
                        fieldbackground=COLOR_BG_SEC,
                        foreground=COLOR_TEXT,
                        borderwidth=0,
                        rowheight=30)
        style.map("Treeview", background=[('selected', COLOR_ACCENT)], foreground=[('selected', COLOR_BG_MAIN)])
        
        style.configure("Treeview.Heading", 
                        background=COLOR_BG_MAIN, 
                        foreground=COLOR_TEXT, 
                        font=("Helvetica", 10, "bold"),
                        relief="flat")
        style.map("Treeview.Heading", background=[('active', COLOR_BG_SEC)])
        
        # Barra de desplazamiento (Scrollbar)
        style.configure("Vertical.TScrollbar", 
                        gripcount=0,
                        background=COLOR_BG_SEC, 
                        darkcolor=COLOR_BG_MAIN, 
                        lightcolor=COLOR_BG_MAIN, 
                        troughcolor=COLOR_BG_MAIN, 
                        bordercolor=COLOR_BG_MAIN, 
                        arrowcolor=COLOR_TEXT)

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
        
        setup_frame = self.frames[SetupFrame]
        setup_frame.team_list_box.delete(0, tk.END)
        setup_frame.error_label.config(text="")
        
        self.show_frame(SetupFrame)

    def save_tournament_data(self):
        """Guarda el estado actual de todos los equipos en un archivo de texto."""
        try:
            filename = "estado_torneo.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"=========================================\n")
                f.write(f"   TRUGO - ESTADO DEL TORNEO: RONDA {self.current_round}\n")
                f.write(f"=========================================\n\n")
                
                # Ordenar equipos por puntos para mejor lectura
                sorted_teams = sorted(self.teams.values(), key=lambda t: t.total_points, reverse=True)
                
                for team in sorted_teams:
                    f.write(f"EQUIPO: {team.name} (ID: {team.id})\n")
                    f.write(f"  > Puntos Totales: {team.total_points}\n")
                    
                    # Convertir IDs de rivales a Nombres
                    rival_names = []
                    for opponent_id in team.opponents_played:
                        if opponent_id in self.teams:
                            rival_names.append(self.teams[opponent_id].name)
                    
                    rivals_str = ", ".join(rival_names) if rival_names else "Ninguno"
                    f.write(f"  > Rivales: {rivals_str}\n")
                    f.write("-" * 40 + "\n")
            
            print(f"Datos guardados exitosamente en {filename}")
        except Exception as e:
            print(f"Error al guardar datos: {e}")

    def generate_pairings(self):
        # ... lógica permanece igual ...
        self.current_round += 1
        new_matches = []
        sorted_teams = sorted(self.teams.values(), key=lambda t: t.total_points, reverse=True)
        unpaired_teams = list(sorted_teams)
        bye_team = None

        if len(unpaired_teams) % 2 != 0:
            for team in reversed(unpaired_teams):
                if not team.received_bye:
                    bye_team = team
                    break
            if bye_team is None:
                bye_team = unpaired_teams[-1]
            bye_team.received_bye = True
            bye_team.total_points += 1 
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
        
        # --- NUEVO: Guardar datos al archivo ---
        self.save_tournament_data()

# --- Frame de Configuración (Setup) ---
class SetupFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        
        # Contenedor central
        center_frame = ttk.Frame(self, style="Main.TFrame")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título modificado a "Trugo" con fuente más grande
        label = ttk.Label(center_frame, text="Trugo", style="Header.TLabel", font=("Helvetica", 48, "bold"))
        label.pack(pady=30)

        # Tarjeta para inputs
        input_card = ttk.Frame(center_frame, style="Card.TFrame", padding=20)
        input_card.pack(fill="x", pady=10)

        grid_frame = ttk.Frame(input_card, style="Card.TFrame")
        grid_frame.pack()

        ttk.Label(grid_frame, text="Nombre Equipo:", style="Card.TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.team_name_entry = ttk.Entry(grid_frame, width=25)
        self.team_name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(grid_frame, text="ID Equipo:", style="Card.TLabel").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.team_id_entry = ttk.Entry(grid_frame, width=25)
        self.team_id_entry.grid(row=1, column=1, padx=10, pady=10)

        add_button = ttk.Button(grid_frame, text="+ Agregar Equipo", style="Primary.TButton", command=self.add_team)
        add_button.grid(row=2, column=0, columnspan=2, pady=15, sticky="ew")

        self.error_label = ttk.Label(center_frame, text="", foreground=COLOR_DANGER, style="SubHeader.TLabel", font=("Helvetica", 10))
        self.error_label.pack(pady=5)

        # Área de Lista
        ttk.Label(center_frame, text="Equipos Registrados", style="SubHeader.TLabel").pack(pady=(20, 10))
        
        list_frame = ttk.Frame(center_frame, style="Main.TFrame")
        list_frame.pack(fill="both", expand=True)
        
        # Estilo de Listbox
        self.team_list_box = tk.Listbox(list_frame, 
                                        height=8, 
                                        width=50,
                                        bg=COLOR_BG_SEC, 
                                        fg=COLOR_TEXT,
                                        bd=0,
                                        highlightthickness=0,
                                        selectbackground=COLOR_ACCENT,
                                        selectforeground=COLOR_BG_MAIN,
                                        font=("Consolas", 11))
        self.team_list_box.pack(side="left", fill="both")
        
        # Botón de Inicio
        start_button = ttk.Button(center_frame, text="Comenzar Torneo →", style="Success.TButton", command=self.start_tournament)
        start_button.pack(pady=30, fill="x", ipady=5)

    def add_team(self):
        name = self.team_name_entry.get()
        team_id = self.team_id_entry.get()
        if not name or not team_id:
            self.error_label.config(text="⚠️ Por favor completa ambos campos.")
            return
        if team_id in self.controller.teams:
            self.error_label.config(text="⚠️ El ID del equipo ya existe.")
            return

        new_team = Team(team_id, name)
        self.controller.teams[team_id] = new_team
        self.team_list_box.insert(tk.END, f" {name}  [ID: {team_id}]")
        self.team_name_entry.delete(0, tk.END)
        self.team_id_entry.delete(0, tk.END)
        self.error_label.config(text="")

    def start_tournament(self):
        if len(self.controller.teams) < 2:
            self.error_label.config(text="⚠️ Necesitas al menos 2 equipos.")
            return
        self.error_label.config(text="")
        self.controller.generate_pairings()
        self.controller.show_frame(MatchFrame)

# --- Frame de Partidos (Match) ---
class MatchFrame(ttk.Frame):
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

        self.error_label = ttk.Label(self, text="", foreground=COLOR_DANGER, style="SubHeader.TLabel", font=("Helvetica", 10))
        self.error_label.pack(pady=5)

        # --- Contenedor Principal (Divide la pantalla) ---
        main_content = ttk.Frame(self, style="Main.TFrame")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Columna Izquierda: Partidos
        left_col = ttk.Frame(main_content, style="Main.TFrame")
        left_col.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(left_col, bg=COLOR_BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(left_col, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Main.TFrame")

        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.window_id, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Columna Derecha: Ranking Lateral (Nuevo)
        right_col = ttk.Frame(main_content, style="Card.TFrame", padding=15)
        right_col.pack(side="right", fill="y", padx=(20, 0)) # Margen a la izquierda

        ttk.Label(right_col, text="Posiciones Actuales", style="SideHeader.TLabel").pack(pady=(0, 10))
        
        # Tabla pequeña para el lateral
        cols_small = ('rank', 'name', 'points')
        self.side_tree = ttk.Treeview(right_col, columns=cols_small, show='headings', height=15)
        self.side_tree.heading('rank', text='#')
        self.side_tree.column('rank', width=30, anchor='center')
        self.side_tree.heading('name', text='Equipo')
        self.side_tree.column('name', width=120)
        self.side_tree.heading('points', text='Pts')
        self.side_tree.column('points', width=40, anchor='center')
        self.side_tree.pack(fill="both", expand=True)

        # --- Pie de Página ---
        footer = ttk.Frame(self, style="Main.TFrame", padding=20)
        footer.pack(side="bottom", fill="x")
        
        self.submit_btn = ttk.Button(footer, text="Enviar Puntajes y Siguiente Ronda →", style="Success.TButton", command=self.submit_scores)
        self.submit_btn.pack(fill="x", ipady=5)

    def display_matches(self):
        # 1. Limpiar área de partidos
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.controller.match_entry_widgets = []
        self.header_label.config(text=f"Ronda {self.controller.current_round}")
        
        self.canvas.yview_moveto(0)

        # Cabecera de la tabla de partidos
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
            
            # Input 1
            s1_ent = ttk.Entry(match_card, width=5, font=("Helvetica", 14, "bold"), justify="center")
            s1_ent.pack(side="left", padx=5)
            
            # VS
            ttk.Label(match_card, text="vs", style="Card.TLabel", foreground=COLOR_ACCENT).pack(side="left", padx=10)
            
            # Input 2
            s2_ent = ttk.Entry(match_card, width=5, font=("Helvetica", 14, "bold"), justify="center")
            s2_ent.pack(side="left", padx=5)
            
            # Equipo 2
            if team2_id == "BYE":
                t2_text = "--- LIBRE ---" # Traducido
                s2_ent.insert(0, "0")
                s2_ent.config(state="disabled")
                s1_ent.insert(0, "1")
                s1_ent.config(state="disabled")
                self.controller.match_entry_widgets.append((None, None, team1_id, "BYE"))
            else:
                team2 = self.controller.teams[team2_id]
                t2_text = f"{team2.name}\n({team2.total_points} pts)"
                self.controller.match_entry_widgets.append((s1_ent, s2_ent, team1_id, team2_id))

            t2_lbl = ttk.Label(match_card, text=t2_text, style="Card.TLabel", justify="left", width=20, anchor="w")
            t2_lbl.pack(side="left", padx=10)

        # 2. Actualizar Tabla Lateral (Sidebar)
        self.update_sidebar()

    def update_sidebar(self):
        # Limpiar tabla
        for row in self.side_tree.get_children():
            self.side_tree.delete(row)
            
        # Ordenar equipos por puntos
        sorted_teams = sorted(self.controller.teams.values(), key=lambda t: t.total_points, reverse=True)
        
        for i, team in enumerate(sorted_teams):
            self.side_tree.insert("", "end", values=(i+1, team.name, team.total_points))

    def submit_scores(self):
        round_points = {team_id: 0 for team_id in self.controller.teams}
        try:
            for (entry1, entry2, team1_id, team2_id) in self.controller.match_entry_widgets:
                if team2_id == "BYE": continue
                
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
            self.display_matches() # Esto actualizará la barra lateral también
        except ValueError:
            self.error_label.config(text="⚠️ Puntaje inválido. Solo números enteros.")

# --- Frame de Posiciones Finales (Standings) ---
class StandingsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        
        center = ttk.Frame(self, style="Main.TFrame")
        center.pack(fill="both", expand=True, padx=40, pady=40)

        ttk.Label(center, text="🏆 Tabla de Posiciones Final", style="Header.TLabel").pack(pady=20)

        # Contenedor Tabla
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

if __name__ == "__main__":
    app = TournamentApp()
    app.mainloop()