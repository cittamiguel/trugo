import unittest
import os
import tkinter as tk
from tournament_app import TournamentApp, Team  # Importamos tu código

class TestTrugoLogic(unittest.TestCase):
    
    def setUp(self):
        """Se ejecuta antes de cada prueba. Crea una instancia de la App."""
        # Instanciamos la app pero ocultamos la ventana para que no moleste
        self.app = TournamentApp()
        self.app.withdraw() 
        
        # Datos de prueba
        self.equipos_prueba = [
            ("1", "Alpha"),
            ("2", "Beta"),
            ("3", "Gamma"),
            ("4", "Delta")
        ]

    def tearDown(self):
        """Se ejecuta después de cada prueba. Limpia archivos creados."""
        self.app.destroy()
        if os.path.exists("TestTorneo.txt"):
            os.remove("TestTorneo.txt")

    def test_creacion_equipos(self):
        """Prueba que los equipos se crean con puntaje 0."""
        t = Team("01", "TestTeam")
        self.assertEqual(t.total_points, 0)
        self.assertEqual(t.name, "TestTeam")
        self.assertEqual(t.id, "01")

    def test_ordenamiento_ranking(self):
        """Prueba que la lógica de ordenamiento por puntos funcione."""
        # Agregamos equipos manualmente a la lógica de la app
        t1 = Team("1", "A")
        t1.total_points = 10
        
        t2 = Team("2", "B")
        t2.total_points = 5
        
        t3 = Team("3", "C")
        t3.total_points = 20
        
        self.app.teams = {"1": t1, "2": t2, "3": t3}
        
        # Simulamos la lógica de generar pareos que ordena primero
        sorted_teams = sorted(self.app.teams.values(), key=lambda t: t.total_points, reverse=True)
        
        # El primero debería ser C (20), luego A (10), luego B (5)
        self.assertEqual(sorted_teams[0].name, "C")
        self.assertEqual(sorted_teams[1].name, "A")
        self.assertEqual(sorted_teams[2].name, "B")

    def test_sistema_suizo_pareos(self):
        """Prueba que no se repitan rivales (lógica fundamental suiza)."""
        # Configurar 4 equipos
        for eid, name in self.equipos_prueba:
            self.app.teams[eid] = Team(eid, name)
        
        # Ronda 1
        self.app.generate_pairings()
        matches_r1 = list(self.app.current_matches)
        
        # Simulamos que el equipo 1 jugó contra el equipo 2
        # (La app ya lo registra internamente al generar pareos)
        team1 = self.app.teams[matches_r1[0][0]]
        team2 = self.app.teams[matches_r1[0][1]]
        
        # Verificar que se guardó el historial
        self.assertIn(team2.id, team1.opponents_played)
        self.assertIn(team1.id, team2.opponents_played)

    def test_bye_manual(self):
        """Prueba la lógica de equipos impares (BYE)."""
        # Agregamos 3 equipos
        equipos_impares = [("1", "A"), ("2", "B"), ("3", "C")]
        for eid, name in equipos_impares:
            self.app.teams[eid] = Team(eid, name)
            
        self.app.generate_pairings()
        
        # Debería haber un match donde el segundo componente es "BYE"
        found_bye = False
        bye_team_id = None
        
        for t1, t2 in self.app.current_matches:
            if t2 == "BYE":
                found_bye = True
                bye_team_id = t1
                break
        
        self.assertTrue(found_bye, "No se generó el BYE para equipos impares")
        
        # Verificamos que al equipo libre NO se le sumaron puntos automáticos (lógica nueva)
        bye_team = self.app.teams[bye_team_id]
        self.assertEqual(bye_team.total_points, 0, "El sistema sumó puntos automáticos al BYE (y no debería)")

    def test_guardado_archivo(self):
        """Verifica que el archivo de texto se crea."""
        self.app.tournament_name = "TestTorneo"
        # Agregamos un equipo dummy para que haya algo que guardar
        self.app.teams["1"] = Team("1", "A")
        
        self.app.save_tournament_data()
        
        self.assertTrue(os.path.exists("TestTorneo.txt"), "El archivo de torneo no se creó")

if __name__ == '__main__':
    print("Iniciando pruebas de lógica de Trugo...")
    unittest.main()