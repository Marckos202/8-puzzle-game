import tkinter as tk
from tkinter import messagebox, simpledialog
import numpy as np
from models.puzzle import Puzzle

class ManualModeUI:
    """
    Interfaz gráfica para el modo manual del juego 8-puzzle usando Tkinter.
    """
    def __init__(self, root=None, puzzle=None, tile_size=80, return_to_menu_callback=None):
        """
        Inicializa la interfaz gráfica para el modo manual.
        
        Args:
            root: Ventana principal de Tkinter. Si es None, se crea una nueva.
            puzzle: Instancia de Puzzle. Si es None, se crea una nueva.
            tile_size: Tamaño de cada casilla en píxeles
            return_to_menu_callback: Función para volver al menú principal
        """
        # Inicializar modelo del juego
        self.puzzle = puzzle if puzzle else Puzzle()
        
        # Configuración de la UI
        self.tile_size = tile_size
        self.margin = 10
        self.grid_size = 3
        
        # Crear ventana principal si no se proporciona
        self.is_main_window = False
        if root is None:
            self.root = tk.Tk()
            self.root.title("8-Puzzle - Modo Manual")
            self.is_main_window = True
        else:
            self.root = root
        
        # Guardar callback para volver al menú
        self.return_to_menu_callback = return_to_menu_callback
        
        # Crear el marco principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=20, pady=20)
        
        # Crear el tablero
        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack(pady=10)
        
        # Crear botones del tablero (se actualizarán más tarde)
        self.tile_buttons = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                btn = tk.Button(
                    self.board_frame, 
                    width=3, 
                    height=1, 
                    font=('Arial', 24),
                    command=lambda r=row, c=col: self.handle_tile_click(r, c)
                )
                btn.grid(row=row, column=col, padx=2, pady=2)
                self.tile_buttons[row][col] = btn
        
        # Frame para información
        self.info_frame = tk.Frame(self.main_frame)
        self.info_frame.pack(pady=10)
        
        # Contador de movimientos
        self.moves_label = tk.Label(self.info_frame, text="Movimientos: 0", font=('Arial', 12))
        self.moves_label.pack(side=tk.LEFT, padx=10)
        
        # Mensaje informativo
        self.message_label = tk.Label(self.info_frame, text="", font=('Arial', 12))
        self.message_label.pack(side=tk.LEFT, padx=10)
        
        # Frame para botones de control
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(pady=10)
        
        # Botones de control
        self.reset_button = tk.Button(self.control_frame, text="Reiniciar", command=self.reset_game)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.shuffle_button = tk.Button(self.control_frame, text="Aleatorizar", command=self.shuffle_game)
        self.shuffle_button.pack(side=tk.LEFT, padx=5)
        
        self.verify_button = tk.Button(self.control_frame, text="Verificar", command=self.check_solution)
        self.verify_button.pack(side=tk.LEFT, padx=5)
        
        self.custom_button = tk.Button(self.control_frame, text="Personalizar", command=self.set_custom_state)
        self.custom_button.pack(side=tk.LEFT, padx=5)
        
        # Botón para cambiar al modo automático
        self.auto_button = tk.Button(self.main_frame, text="Modo Automático", command=self.switch_to_auto_mode)
        self.auto_button.pack(pady=10)
        
        # Actualizar el tablero
        self.update_board()
        
        # Si es ventana principal, configurar cierre
        if self.is_main_window:
            self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
    
    def update_board(self):
        """Actualiza el tablero con el estado actual del puzzle."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                value = self.puzzle.state[row, col]
                
                if value == 0:
                    # Espacio vacío
                    self.tile_buttons[row][col].config(text="", bg="white")
                else:
                    # Ficha con número
                    self.tile_buttons[row][col].config(text=str(value), bg="lightblue")
        
        # Actualizar contador de movimientos
        self.moves_label.config(text=f"Movimientos: {self.puzzle.moves_count}")
    
    def handle_tile_click(self, row, col):
        """
        Maneja el clic en una casilla del tablero.
        
        Args:
            row: Fila de la casilla
            col: Columna de la casilla
        """
        # Intentar mover la ficha
        if self.puzzle.move_tile(row, col):
            # Actualizar el tablero
            self.update_board()
            
            # Verificar si se ha resuelto el puzzle
            if self.puzzle.is_goal():
                messagebox.showinfo("¡Felicidades!", "¡Has resuelto el puzzle!")
                self.message_label.config(text="¡Puzzle resuelto!", fg="green")
    
    def reset_game(self):
        """Reinicia el juego al estado objetivo."""
        self.puzzle.reset()
        self.update_board()
        self.message_label.config(text="Juego reiniciado", fg="black")
    
    def shuffle_game(self):
        """Aleatoriza el tablero."""
        self.puzzle.shuffle(num_moves=100)
        
        # Verificar si el estado generado tiene solución
        if not self.puzzle.is_solvable():
            # Si no tiene solución, generar otro
            self.shuffle_game()
            return
        
        self.update_board()
        self.message_label.config(text="Tablero aleatorizado", fg="black")
    
    def check_solution(self):
        """Verifica si el jugador ha resuelto el puzzle."""
        if self.puzzle.is_goal():
            messagebox.showinfo("Verificación", "¡El puzzle está resuelto!")
            self.message_label.config(text="¡Puzzle resuelto!", fg="green")
        else:
            messagebox.showinfo("Verificación", "El puzzle aún no está resuelto")
            self.message_label.config(text="Aún no está resuelto", fg="red")
    
    def switch_to_auto_mode(self):
        """Cambia al modo automático."""
        if self.return_to_menu_callback:
            # Guardar el estado actual del puzzle
            current_puzzle = self.puzzle
            
            # Limpiar la interfaz actual
            self.main_frame.destroy()
            
            # Llamar al callback para cambiar de modo
            self.return_to_menu_callback("auto", current_puzzle)
        else:
            self.message_label.config(text="Cambiando a modo automático...", fg="blue")
            messagebox.showinfo("Cambio de Modo", "Esta funcionalidad no está disponible en modo standalone")
    
    def set_custom_state(self):
        """
        Permite al usuario configurar manualmente el estado inicial.
        """
        # Crear una ventana de diálogo para input
        input_dialog = CustomStateDialog(self.root)
        
        # Si el usuario configuró un estado válido
        if input_dialog.result:
            try:
                # Convertir la entrada a una matriz 3x3
                state = np.array(input_dialog.result).reshape(3, 3)
                
                # Verificar si el estado es resoluble
                temp_puzzle = Puzzle(state)
                if not temp_puzzle.is_solvable():
                    messagebox.showwarning("Estado no válido", "El estado ingresado no tiene solución.")
                    return
                
                # Establecer el nuevo estado
                self.puzzle.set_state(state)
                self.update_board()
                self.message_label.config(text="Estado configurado manualmente", fg="black")
            except Exception as e:
                messagebox.showerror("Error", f"Error al configurar el estado: {e}")
    
    def run(self):
        """Inicia el bucle principal de la interfaz si es ventana principal."""
        if self.is_main_window:
            self.root.mainloop()


class CustomStateDialog:
    """
    Diálogo para configurar un estado personalizado del tablero.
    """
    def __init__(self, parent):
        self.result = None
        
        # Crear ventana de diálogo
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configurar Estado")
        self.dialog.geometry("300x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Frame para la entrada
        frame = tk.Frame(self.dialog)
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Instrucciones
        tk.Label(frame, text="Ingrese los números del 0 al 8", font=('Arial', 12)).pack(pady=5)
        tk.Label(frame, text="(0 representa el espacio vacío)", font=('Arial', 10)).pack()
        tk.Label(frame, text="Formato: 1,2,3,4,5,6,7,8,0", font=('Arial', 10)).pack(pady=5)
        
        # Campo de entrada
        self.entry = tk.Entry(frame, font=('Arial', 12), width=20)
        self.entry.pack(pady=10)
        self.entry.insert(0, "1,2,3,4,5,6,7,8,0")
        
        # Botones
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Aceptar", command=self.on_accept).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancelar", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
        
        # Centrar el diálogo en la ventana padre
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Esperar a que se cierre el diálogo
        self.dialog.wait_window()
    
    def on_accept(self):
        """Procesa la entrada del usuario al hacer clic en Aceptar."""
        try:
            # Leer la entrada del usuario
            user_input = self.entry.get()
            numbers = [int(num.strip()) for num in user_input.split(',')]
            
            # Verificar que se ingresaron 9 números del 0 al 8 sin repetir
            if len(numbers) != 9 or set(numbers) != set(range(9)):
                messagebox.showwarning(
                    "Entrada inválida", 
                    "Debe ingresar los números del 0 al 8 sin repetir."
                )
                return
            
            # Guardar el resultado
            self.result = numbers
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la entrada: {e}")
    
    def on_cancel(self):
        """Cancela la operación."""
        self.dialog.destroy()


if __name__ == "__main__":
    # Ejemplo de uso independiente
    game = ManualModeUI()
    game.run()