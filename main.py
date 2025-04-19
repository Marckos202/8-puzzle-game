import tkinter as tk
from tkinter import messagebox
import os
import sys

from models.puzzle import Puzzle
from ui.manual_mode import ManualModeUI
from ui.auto_mode import AutoModeUI

class EightPuzzleGame:
    """
    Clase principal que gestiona la aplicación del juego 8-puzzle.
    """
    def __init__(self):
        """Inicializa la aplicación."""
        # Inicializar ventana principal
        self.root = tk.Tk()
        self.root.title("8-Puzzle Game")
        self.root.geometry("1000x720")
        self.root.resizable(False, False)
        
        # Variables de estado
        self.current_mode = None  # 'manual' o 'auto'
        self.puzzle = Puzzle()  # Modelo compartido del juego
        
        # Colores y estilos
        self.colors = {
            "bg": "#f0f0f0",
            "button": "#4a7abc",
            "button_text": "#ffffff",
            "title": "#333333",
            "subtitle": "#555555",
        }
        
        # Crear menú principal
        self.create_main_menu()
        
        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_main_menu(self):
        """Crea la interfaz del menú principal."""
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            self.main_frame,
            text="8-Puzzle Game",
            font=("Arial", 24, "bold"),
            fg=self.colors["title"],
            bg=self.colors["bg"]
        )
        title_label.pack(pady=(20, 10))
        
        # Descripción
        description_frame = tk.Frame(self.main_frame, bg=self.colors["bg"])
        description_frame.pack(pady=10)
        
        desc1 = tk.Label(
            description_frame,
            text="Un juego de lógica para resolver el rompecabezas 8-puzzle",
            font=("Arial", 12),
            fg=self.colors["subtitle"],
            bg=self.colors["bg"]
        )
        desc1.pack(pady=2)
        
        desc2 = tk.Label(
            description_frame,
            text="Modo Manual: Resuelve el puzzle tú mismo",
            font=("Arial", 12),
            fg=self.colors["subtitle"],
            bg=self.colors["bg"]
        )
        desc2.pack(pady=2)
        
        desc3 = tk.Label(
            description_frame,
            text="Modo Automático: Observa diferentes algoritmos resolver el puzzle",
            font=("Arial", 12),
            fg=self.colors["subtitle"],
            bg=self.colors["bg"]
        )
        desc3.pack(pady=2)
        
        # Frame para botones
        buttons_frame = tk.Frame(self.main_frame, bg=self.colors["bg"])
        buttons_frame.pack(pady=30)
        
        # Botón de modo manual
        manual_button = tk.Button(
            buttons_frame,
            text="Modo Manual",
            font=("Arial", 14),
            width=20,
            height=2,
            bg=self.colors["button"],
            fg=self.colors["button_text"],
            command=self.start_manual_mode
        )
        manual_button.pack(pady=10)
        
        # Botón de modo automático
        auto_button = tk.Button(
            buttons_frame,
            text="Modo Automático",
            font=("Arial", 14),
            width=20,
            height=2,
            bg=self.colors["button"],
            fg=self.colors["button_text"],
            command=self.start_auto_mode
        )
        auto_button.pack(pady=10)
        
        # Botón de salida
        quit_button = tk.Button(
            buttons_frame,
            text="Salir",
            font=("Arial", 14),
            width=20,
            height=2,
            command=self.on_close
        )
        quit_button.pack(pady=10)
    
    def clear_interface(self):
        """Limpia la interfaz actual."""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def start_manual_mode(self, puzzle=None):
        """
        Inicia el modo manual del juego.
        
        Args:
            puzzle: Instancia de Puzzle opcional para usar un estado existente
        """
        # Actualizar el modelo si se proporciona uno
        if puzzle:
            self.puzzle = puzzle
        
        # Limpiar la interfaz actual
        self.clear_interface()
        
        # Establecer el modo actual
        self.current_mode = 'manual'
        
        # Crear la interfaz de modo manual
        self.manual_ui = ManualModeUI(
            root=self.root,
            puzzle=self.puzzle,
            return_to_menu_callback=self.switch_mode
        )
    
    def start_auto_mode(self, puzzle=None):
        """
        Inicia el modo automático del juego.
        
        Args:
            puzzle: Instancia de Puzzle opcional para usar un estado existente
        """
        # Actualizar el modelo si se proporciona uno
        if puzzle:
            self.puzzle = puzzle
        
        # Limpiar la interfaz actual
        self.clear_interface()
        
        # Establecer el modo actual
        self.current_mode = 'auto'
        
        # Crear la interfaz de modo automático
        self.auto_ui = AutoModeUI(
            root=self.root,
            puzzle=self.puzzle,
            return_to_menu_callback=self.switch_mode
        )
    
    def switch_mode(self, mode, puzzle=None):
        """
        Cambia entre modos o vuelve al menú principal.
        
        Args:
            mode: 'manual', 'auto' o 'menu'
            puzzle: Instancia de Puzzle opcional para pasar al nuevo modo
        """
        if mode == 'manual':
            self.start_manual_mode(puzzle)
        elif mode == 'auto':
            self.start_auto_mode(puzzle)
        else:  # 'menu'
            # Guardar el puzzle si se proporciona
            if puzzle:
                self.puzzle = puzzle
            
            # Volver al menú principal
            self.clear_interface()
            self.create_main_menu()
    
    def on_close(self):
        """Maneja el evento de cierre de la ventana."""
        if messagebox.askyesno("Salir", "¿Estás seguro de que quieres salir?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Ejecuta el bucle principal de la aplicación."""
        # Crear directorios necesarios si no existen
        os.makedirs('models', exist_ok=True)
        os.makedirs('ui', exist_ok=True)
        os.makedirs('utils', exist_ok=True)
        
        # Iniciar la aplicación
        self.root.mainloop()


# Inicializar la aplicación cuando se ejecuta el script
if __name__ == "__main__":
    game = EightPuzzleGame()
    game.run()