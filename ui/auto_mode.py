import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import numpy as np
import time
import threading
from models.puzzle import Puzzle
from models.solver import PuzzleSolver
from ui.manual_mode import CustomStateDialog

class AutoModeUI:
    """
    Interfaz gráfica para el modo automático del juego 8-puzzle usando Tkinter.
    """
    def __init__(self, root=None, puzzle=None, tile_size=80, return_to_menu_callback=None):
        """
        Inicializa la interfaz gráfica para el modo automático.
        
        Args:
            root: Ventana principal de Tkinter. Si es None, se crea una nueva.
            puzzle: Instancia de Puzzle. Si es None, se crea una nueva.
            tile_size: Tamaño de cada casilla en píxeles
            return_to_menu_callback: Función para volver al menú principal
        """
        # Inicializar modelo del juego
        self.puzzle = puzzle if puzzle else Puzzle()
        self.goal_state = self.puzzle.goal_state
        
        # Configuración de la UI
        self.tile_size = tile_size
        self.margin = 10
        self.grid_size = 3
        
        # Crear ventana principal si no se proporciona
        self.is_main_window = False
        if root is None:
            self.root = tk.Tk()
            self.root.title("8-Puzzle - Modo Automático")
            self.is_main_window = True
        else:
            self.root = root
        
        # Guardar callback para volver al menú
        self.return_to_menu_callback = return_to_menu_callback
        
        # Estado y resultados
        self.algorithms = ["BFS", "DFS Limitada", "A* Manhattan"]
        self.selected_algorithm = tk.StringVar(value=self.algorithms[0])
        self.results = {}
        self.all_results = {}
        self.recommended_algorithm = None
        
        # Estado de la solución
        self.solution_path = []
        self.current_step = 0
        self.animating = False
        self.animation_speed = tk.DoubleVar(value=0.5)  # segundos entre pasos
        
        # Crear interfaz
        self.create_widgets()
        
        # Actualizar el tablero
        self.update_board()
        
        # Si es ventana principal, configurar cierre
        if self.is_main_window:
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        """Crea y dispone los widgets de la interfaz."""
        # Frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=20, pady=20)
        
        # Crear una disposición de dos columnas
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, padx=10, sticky="n")
        
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, padx=10, sticky="n")
        
        # Panel izquierdo - Tablero y controles
        self.board_frame = tk.Frame(self.left_frame)
        self.board_frame.pack(pady=10)
        
        # Crear botones del tablero
        self.tile_buttons = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                btn = tk.Button(
                    self.board_frame, 
                    width=3, 
                    height=1, 
                    font=('Arial', 24),
                    state=tk.DISABLED  # No se pueden hacer clic en modo automático
                )
                btn.grid(row=row, column=col, padx=2, pady=2)
                self.tile_buttons[row][col] = btn
        
        # Frame para información y controles
        self.info_frame = tk.Frame(self.left_frame)
        self.info_frame.pack(pady=10, fill="x")
        
        # Mensaje informativo
        self.message_label = tk.Label(self.info_frame, text="", font=('Arial', 12))
        self.message_label.pack(pady=5)
        
        # Estado de la solución
        self.status_label = tk.Label(self.info_frame, text="Estado: Listo", font=('Arial', 10))
        self.status_label.pack(pady=2)
        
        # Controles del algoritmo
        self.algo_frame = tk.LabelFrame(self.left_frame, text="Algoritmo", padx=10, pady=5)
        self.algo_frame.pack(pady=5, fill="x")
        
        algo_combobox = ttk.Combobox(
            self.algo_frame, 
            textvariable=self.selected_algorithm,
            values=self.algorithms,
            state="readonly",
            width=20
        )
        algo_combobox.pack(pady=5)
        
        # Frame para botones de control
        self.control_frame = tk.Frame(self.left_frame)
        self.control_frame.pack(pady=10, fill="x")
        
        # Botones de control
        self.shuffle_button = tk.Button(self.control_frame, text="Aleatorizar", command=self.shuffle_game)
        self.shuffle_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.solve_button = tk.Button(self.control_frame, text="Resolver", command=self.solve_puzzle)
        self.solve_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.animate_button = tk.Button(self.control_frame, text="Mostrar Solución", command=self.toggle_animation)
        self.animate_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.custom_button = tk.Button(self.control_frame, text="Configurar Estado", command=self.set_custom_state)
        self.custom_button.grid(row=1, column=0, padx=5, pady=5)
        
        self.compare_button = tk.Button(self.control_frame, text="Comparar Todos", command=self.compare_all)
        self.compare_button.grid(row=1, column=1, padx=5, pady=5)
        
        self.manual_button = tk.Button(self.control_frame, text="Modo Manual", command=self.switch_to_manual_mode)
        self.manual_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Control de velocidad de animación
        self.speed_frame = tk.LabelFrame(self.left_frame, text="Velocidad de animación", padx=10, pady=5)
        self.speed_frame.pack(pady=5, fill="x")
        
        self.speed_scale = ttk.Scale(
            self.speed_frame,
            from_=0.1,
            to=2.0,
            orient=tk.HORIZONTAL,
            variable=self.animation_speed,
            length=200
        )
        self.speed_scale.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.speed_label = tk.Label(self.speed_frame, text="0.5 seg")
        self.speed_label.pack(side=tk.LEFT, padx=5)
        
        self.speed_scale.configure(command=self.update_speed_label)
        
        # Panel derecho - Resultados
        self.results_frame = tk.LabelFrame(self.right_frame, text="Resultados", padx=10, pady=10)
        self.results_frame.pack(pady=10, fill="both", expand=True)
        
        # Crear tabla de resultados
        self.results_tree = ttk.Treeview(
            self.results_frame,
            columns=("Algoritmo", "Tiempo (s)", "Nodos", "Longitud"),
            show="headings",
            height=5
        )
        
        # Configurar columnas
        self.results_tree.heading("Algoritmo", text="Algoritmo")
        self.results_tree.heading("Tiempo (s)", text="Tiempo (s)")
        self.results_tree.heading("Nodos", text="Nodos")
        self.results_tree.heading("Longitud", text="Longitud")
        
        self.results_tree.column("Algoritmo", width=120)
        self.results_tree.column("Tiempo (s)", width=80)
        self.results_tree.column("Nodos", width=80)
        self.results_tree.column("Longitud", width=80)
        
        self.results_tree.pack(pady=5)
        
        # Etiqueta de recomendación
        self.recommendation_frame = tk.Frame(self.right_frame)
        self.recommendation_frame.pack(pady=10, fill="x")
        
        self.recommendation_label = tk.Label(
            self.recommendation_frame,
            text="Ejecute algoritmos para obtener una recomendación",
            font=('Arial', 10),
            wraplength=350
        )
        self.recommendation_label.pack(pady=5)
    
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
    
    def update_speed_label(self, value):
        """Actualiza la etiqueta de velocidad."""
        self.speed_label.config(text=f"{float(value):.1f} seg")
    
    def shuffle_game(self):
        """Aleatoriza el tablero."""
        if self.animating:
            self.toggle_animation()  # Detener animación si está en curso
        
        self.puzzle.shuffle(num_moves=30)
        
        # Verificar que el estado generado tiene solución
        if not self.puzzle.is_solvable():
            # Si no tiene solución, mover una ficha para cambiar la paridad
            state = self.puzzle.state.copy()
            # Intercambiar las dos primeras fichas que no sean 0
            idx1, idx2 = None, None
            for i in range(3):
                for j in range(3):
                    if state[i, j] != 0:
                        if idx1 is None:
                            idx1 = (i, j)
                        elif idx2 is None:
                            idx2 = (i, j)
                            break
                if idx2 is not None:
                    break
            
            # Intercambiar las fichas
            state[idx1], state[idx2] = state[idx2], state[idx1]
            self.puzzle.set_state(state)
        
        self.update_board()
        self.solution_path = []
        self.current_step = 0
        self.message_label.config(text="Tablero aleatorizado", fg="black")
        self.status_label.config(text="Estado: Listo")
        
        # Limpiar resultados
        self.clear_results()
    
    def solve_puzzle(self):
        """Resuelve el puzzle con el algoritmo seleccionado."""
        if self.animating:
            self.toggle_animation()  # Detener animación si está en curso
        
        # Deshabilitar botones durante la resolución
        self.set_buttons_state(tk.DISABLED)
        self.message_label.config(text="Resolviendo...", fg="blue")
        self.status_label.config(text="Estado: Calculando solución")
        self.root.update()
        
        # Ejecutar algoritmo en un hilo separado para no bloquear la interfaz
        algorithm = self.selected_algorithm.get()
        threading.Thread(target=self._solve_in_thread, args=(algorithm,), daemon=True).start()
    
    def _solve_in_thread(self, algorithm):
        """Ejecuta el algoritmo de resolución en un hilo separado."""
        try:
            # Crear el solucionador
            solver = PuzzleSolver(initial_state=self.puzzle.state, goal_state=self.goal_state)
            
            # Resolver con el algoritmo seleccionado
            if algorithm == "BFS":
                result = solver.solve_bfs()
            elif algorithm == "DFS Limitada":
                result = solver.solve_dfs_limited(depth_limit=20)
            elif algorithm == "A* Manhattan":
                result = solver.solve_astar()
            
            # Guardar los resultados
            self.results = result
            self.all_results[algorithm] = result
            
            # Actualizar la interfaz
            self.root.after(0, self._update_after_solve, result, algorithm)
            
        except Exception as e:
            # Manejar errores
            self.root.after(0, lambda: self._show_error(f"Error en la resolución: {str(e)}"))
    
    def _update_after_solve(self, result, algorithm):
        """Actualiza la interfaz después de resolver."""
        # Actualizar la solución
        if result['success']:
            self.solution_path = result['path']
            self.current_step = 0
            self.message_label.config(
                text=f"Solución encontrada con {algorithm}. Longitud: {result['path_length']}",
                fg="green"
            )
            self.status_label.config(text=f"Estado: Solución lista (Pasos: {len(self.solution_path)})")
        else:
            self.solution_path = []
            self.message_label.config(
                text=f"No se encontró solución con {algorithm}",
                fg="red"
            )
            self.status_label.config(text="Estado: Sin solución")
        
        # Actualizar tabla de resultados
        self.update_results_table()
        
        # Recomendar algoritmo si se han ejecutado varios
        if len(self.all_results) > 1:
            self.recommend_algorithm()
        
        # Habilitar botones
        self.set_buttons_state(tk.NORMAL)
    
    def _show_error(self, message):
        """Muestra un mensaje de error y restablece el estado de los botones."""
        messagebox.showerror("Error", message)
        self.message_label.config(text="Error en la resolución", fg="red")
        self.set_buttons_state(tk.NORMAL)
    
    def toggle_animation(self):
        """Inicia o detiene la animación de la solución."""
        if not self.solution_path:
            messagebox.showinfo("Información", "No hay solución para mostrar")
            return
        
        self.animating = not self.animating
        
        if self.animating:
            self.animate_button.config(text="Detener")
            self.status_label.config(text=f"Estado: Animando solución ({self.current_step+1}/{len(self.solution_path)})")
            self.set_buttons_state(tk.DISABLED, exclude=[self.animate_button])
            self.animate_solution()
        else:
            self.animate_button.config(text="Mostrar Solución")
            self.status_label.config(text=f"Estado: Pausa ({self.current_step}/{len(self.solution_path)})")
            self.set_buttons_state(tk.NORMAL)
    
    def animate_solution(self):
        """Anima la solución paso a paso."""
        if not self.animating or self.current_step >= len(self.solution_path):
            if self.current_step >= len(self.solution_path):
                self.message_label.config(text="Solución completada", fg="green")
                self.status_label.config(text="Estado: Completado")
                self.animating = False
                self.animate_button.config(text="Mostrar Solución")
                self.set_buttons_state(tk.NORMAL)
            return
        
        # Actualizar el estado del puzzle
        _, state = self.solution_path[self.current_step]
        self.puzzle.set_state(state)
        self.update_board()
        
        # Actualizar contador
        self.current_step += 1
        self.status_label.config(text=f"Estado: Animando solución ({self.current_step}/{len(self.solution_path)})")
        
        # Programar el siguiente paso
        delay = int(self.animation_speed.get() * 1000)  # Convertir a milisegundos
        self.root.after(delay, self.animate_solution)
    
    def set_buttons_state(self, state, exclude=None):
        """Establece el estado de los botones."""
        exclude = exclude or []
        buttons = [
            self.shuffle_button,
            self.solve_button,
            self.custom_button,
            self.compare_button,
            self.manual_button
        ]
        
        for button in buttons:
            if button not in exclude:
                button.config(state=state)
    
    def set_custom_state(self):
        """Permite al usuario configurar manualmente el estado inicial."""
        if self.animating:
            self.toggle_animation()  # Detener animación si está en curso
        
        # Crear diálogo para introducir estado personalizado
        dialog = CustomStateDialog(self.root)
        
        # Si el usuario configuró un estado válido
        if dialog.result:
            try:
                # Convertir la entrada a una matriz 3x3
                state = np.array(dialog.result).reshape(3, 3)
                
                # Verificar si el estado es resoluble
                temp_puzzle = Puzzle(state)
                if not temp_puzzle.is_solvable():
                    messagebox.showwarning("Estado no válido", "El estado ingresado no tiene solución.")
                    return
                
                # Establecer el nuevo estado
                self.puzzle.set_state(state)
                self.update_board()
                self.solution_path = []
                self.current_step = 0
                self.message_label.config(text="Estado configurado manualmente", fg="black")
                self.status_label.config(text="Estado: Listo")
                
                # Limpiar resultados
                self.clear_results()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al configurar el estado: {e}")
    
    def compare_all(self):
        """Ejecuta todos los algoritmos para comparar su rendimiento."""
        if self.animating:
            self.toggle_animation()  # Detener animación si está en curso
        
        # Deshabilitar botones durante la comparación
        self.set_buttons_state(tk.DISABLED)
        self.message_label.config(text="Comparando algoritmos...", fg="blue")
        self.status_label.config(text="Estado: Ejecutando comparación")
        self.root.update()
        
        # Ejecutar comparación en un hilo separado
        threading.Thread(target=self._compare_in_thread, daemon=True).start()
    
    def _compare_in_thread(self):
        """Ejecuta la comparación de algoritmos en un hilo separado."""
        try:
            # Guardar el estado actual para restaurarlo después
            original_state = self.puzzle.state.copy()
            
            # Limpiar resultados previos
            self.all_results = {}
            
            # Ejecutar cada algoritmo
            for algorithm in self.algorithms:
                # Restaurar estado original para cada algoritmo
                self.puzzle.set_state(original_state)
                
                # Crear el solucionador
                solver = PuzzleSolver(initial_state=self.puzzle.state, goal_state=self.goal_state)
                
                # Resolver con el algoritmo actual
                if algorithm == "BFS":
                    result = solver.solve_bfs()
                elif algorithm == "DFS Limitada":
                    result = solver.solve_dfs_limited(depth_limit=20)
                elif algorithm == "A* Manhattan":
                    result = solver.solve_astar()
                
                # Guardar resultados
                self.all_results[algorithm] = result
                
                # Si el algoritmo actual tuvo éxito, guardar su camino
                if result['success'] and not self.solution_path:
                    self.results = result
                    self.solution_path = result['path']
                    self.current_step = 0
            
            # Actualizar la interfaz
            self.root.after(0, self._update_after_compare)
            
        except Exception as e:
            # Manejar errores
            self.root.after(0, lambda: self._show_error(f"Error en la comparación: {str(e)}"))
    
    def _update_after_compare(self):
        """Actualiza la interfaz después de comparar todos los algoritmos."""
        # Actualizar tabla de resultados
        self.update_results_table()
        
        # Recomendar el mejor algoritmo
        self.recommend_algorithm()
        
        # Restaurar el estado del tablero si hay una solución
        if self.solution_path:
            self.puzzle.set_state(self.puzzle.state)  # Mantener el estado actual
            self.message_label.config(text="Comparación completada. Use 'Mostrar Solución' para ver el resultado.", fg="green")
            self.status_label.config(text=f"Estado: Solución lista (Pasos: {len(self.solution_path)})")
        else:
            self.message_label.config(text="Ningún algoritmo encontró solución.", fg="red")
            self.status_label.config(text="Estado: Sin solución")
        
        # Habilitar botones
        self.set_buttons_state(tk.NORMAL)
    
    def recommend_algorithm(self):
        """Recomienda el algoritmo más eficiente basado en las métricas disponibles."""
        # Solo considerar algoritmos que encontraron solución
        successful_results = {algo: res for algo, res in self.all_results.items() if res['success']}
        
        if not successful_results:
            self.recommendation_label.config(
                text="No se pudo encontrar una solución con ningún algoritmo.",
                fg="red"
            )
            return
        
        # Criterios de evaluación (menor es mejor)
        # 1. Longitud del camino (más importante)
        # 2. Tiempo de ejecución
        # 3. Nodos expandidos
        
        # Normalizar los valores
        path_lengths = [res['path_length'] for res in successful_results.values()]
        exec_times = [res['execution_time'] for res in successful_results.values()]
        nodes_expanded = [res['nodes_expanded'] for res in successful_results.values()]
        
        max_path = max(path_lengths) if path_lengths else 1
        max_time = max(exec_times) if exec_times else 1
        max_nodes = max(nodes_expanded) if nodes_expanded else 1
        
        # Calcular puntuación para cada algoritmo
        scores = {}
        for algo, res in successful_results.items():
            norm_path = res['path_length'] / max_path if max_path > 0 else 0
            norm_time = res['execution_time'] / max_time if max_time > 0 else 0
            norm_nodes = res['nodes_expanded'] / max_nodes if max_nodes > 0 else 0
            
            # Ponderación: 50% longitud, 30% tiempo, 20% nodos
            scores[algo] = 0.5 * norm_path + 0.3 * norm_time + 0.2 * norm_nodes
        
        # Encontrar el algoritmo con menor puntuación
        self.recommended_algorithm = min(scores, key=scores.get)
        
        # Actualizar la recomendación
        self.recommendation_label.config(
            text=f"Recomendado: {self.recommended_algorithm}\n"
                f"Mejor equilibrio entre tiempo de ejecución, "
                f"memoria utilizada y calidad de la solución.",
            fg="green"
        )
        
        # Resaltar la fila recomendada en la tabla
        self.update_results_table()
    
    def update_results_table(self):
        """Actualiza la tabla de resultados con los datos de todos los algoritmos ejecutados."""
        # Limpiar tabla
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Insertar resultados
        for algo, result in self.all_results.items():
            if result['success']:
                values = (
                    algo,
                    f"{result['execution_time']:.6f}",
                    str(result['nodes_expanded']),
                    str(result['path_length'])
                )
                
                # Añadir fila a la tabla
                item_id = self.results_tree.insert("", "end", values=values)
                
                # Resaltar el algoritmo recomendado
                if algo == self.recommended_algorithm:
                    self.results_tree.item(item_id, tags=("recommended",))
            else:
                # Algoritmo sin éxito
                self.results_tree.insert("", "end", values=(algo, "N/A", "N/A", "Sin solución"))
        
        # Configurar color para la recomendación
        self.results_tree.tag_configure("recommended", background="lightgreen")
    
    def clear_results(self):
        """Limpia los resultados."""
        self.results = {}
        self.all_results = {}
        self.recommended_algorithm = None
        self.solution_path = []
        self.current_step = 0
        
        # Limpiar tabla
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Restablecer etiqueta de recomendación
        self.recommendation_label.config(
            text="Ejecute algoritmos para obtener una recomendación",
            fg="black"
        )
    
    def switch_to_manual_mode(self):
        """Cambia al modo manual."""
        if self.animating:
            self.toggle_animation()  # Detener animación si está en curso
        
        if self.return_to_menu_callback:
            # Guardar el estado actual del puzzle
            current_puzzle = self.puzzle
            
            # Limpiar la interfaz actual
            self.main_frame.destroy()
            
            # Llamar al callback para cambiar de modo
            self.return_to_menu_callback("manual", current_puzzle)
        else:
            self.message_label.config(text="Cambiando a modo manual...", fg="blue")
            messagebox.showinfo("Cambio de Modo", "Esta funcionalidad no está disponible en modo standalone")
    
    def on_close(self):
        """Maneja el evento de cierre de la ventana."""
        if self.animating:
            self.toggle_animation()
        
        if self.is_main_window:
            self.root.quit()
    
    def run(self):
        """Inicia el bucle principal de la interfaz si es ventana principal."""
        if self.is_main_window:
            self.root.mainloop()


if __name__ == "__main__":
    # Ejemplo de uso independiente
    game = AutoModeUI()
    game.run()