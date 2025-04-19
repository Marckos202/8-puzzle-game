import time
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from models.puzzle import Puzzle
from models.solver import PuzzleSolver

class AlgorithmMetrics:
    """
    Clase para medir y comparar el rendimiento de diferentes algoritmos de búsqueda.
    """
    def __init__(self):
        """Inicializa el sistema de métricas."""
        self.results = {}
    
    def run_benchmark(self, initial_states, algorithms=None):
        """
        Ejecuta una comparación de rendimiento para varios estados iniciales
        y algoritmos.
        
        Args:
            initial_states: Lista de estados iniciales para probar
            algorithms: Lista de algoritmos para probar. Si es None, se usan todos.
            
        Returns:
            Dictionary con los resultados para cada algoritmo y cada estado.
        """
        if algorithms is None:
            algorithms = ["BFS", "DFS Limitada", "A* Manhattan"]
        
        goal_state = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        
        results = {algo: [] for algo in algorithms}
        
        # Para cada estado inicial
        for i, state in enumerate(initial_states):
            print(f"Evaluando estado {i+1}/{len(initial_states)}")
            
            # Crear el solucionador
            solver = PuzzleSolver(initial_state=state, goal_state=goal_state)
            
            # Ejecutar cada algoritmo
            for algo in algorithms:
                print(f"  Ejecutando {algo}...")
                
                # Medir el tiempo de inicio
                start_time = time.time()
                
                # Resolver con el algoritmo seleccionado
                if algo == "BFS":
                    result = solver.solve_bfs()
                elif algo == "DFS Limitada":
                    result = solver.solve_dfs_limited(depth_limit=20)
                elif algo == "A* Manhattan":
                    result = solver.solve_astar()
                
                # Guardar los resultados
                result['initial_state'] = state
                results[algo].append(result)
        
        self.results = results
        return results
    
    def generate_test_cases(self, num_cases=5, min_difficulty=5, max_difficulty=25):
        """
        Genera casos de prueba aleatorios con diferentes niveles de dificultad.
        
        Args:
            num_cases: Número de casos a generar
            min_difficulty: Número mínimo de movimientos desde el estado objetivo
            max_difficulty: Número máximo de movimientos desde el estado objetivo
            
        Returns:
            Lista de estados iniciales.
        """
        test_cases = []
        
        # Generar varios casos con diferentes niveles de dificultad
        for _ in range(num_cases):
            # Crear un puzzle en estado objetivo
            puzzle = Puzzle()
            
            # Determinar la dificultad (número de movimientos aleatorios)
            difficulty = np.random.randint(min_difficulty, max_difficulty + 1)
            
            # Realizar una serie de movimientos aleatorios
            for _ in range(difficulty):
                moves = puzzle.get_possible_moves()
                move = np.random.choice(moves)
                puzzle.move(move)
            
            # Guardar el estado generado
            test_cases.append(puzzle.state.copy())
        
        return test_cases
    
    def plot_execution_time(self, figure=None):
        """
        Genera un gráfico comparativo de tiempos de ejecución.
        
        Args:
            figure: Figura de matplotlib para dibujar. Si es None, se crea una nueva.
            
        Returns:
            Figura de matplotlib con el gráfico.
        """
        if not self.results:
            print("No hay resultados para graficar. Ejecute run_benchmark primero.")
            return None
        
        # Preparar los datos para el gráfico
        algorithms = list(self.results.keys())
        
        # Calcular tiempos promedio
        avg_times = {}
        for algo in algorithms:
            times = [res['execution_time'] for res in self.results[algo] if res['success']]
            if times:
                avg_times[algo] = sum(times) / len(times)
            else:
                avg_times[algo] = 0
        
        # Crear o usar la figura proporcionada
        if figure is None:
            fig = Figure(figsize=(8, 5))
        else:
            fig = figure
            fig.clear()
        
        ax = fig.add_subplot(111)
        
        # Crear el gráfico de barras
        bars = ax.bar(list(avg_times.keys()), list(avg_times.values()), color='skyblue')
        
        # Añadir etiquetas y título
        ax.set_xlabel('Algoritmo')
        ax.set_ylabel('Tiempo promedio (segundos)')
        ax.set_title('Comparación de tiempos de ejecución')
        
        # Añadir valores sobre las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.6f}',
                   ha='center', va='bottom', fontsize=9)
        
        fig.tight_layout()
        return fig
    
    def plot_nodes_expanded(self, figure=None):
        """
        Genera un gráfico comparativo de nodos expandidos.
        
        Args:
            figure: Figura de matplotlib para dibujar. Si es None, se crea una nueva.
            
        Returns:
            Figura de matplotlib con el gráfico.
        """
        if not self.results:
            print("No hay resultados para graficar. Ejecute run_benchmark primero.")
            return None
        
        # Preparar los datos para el gráfico
        algorithms = list(self.results.keys())
        
        # Calcular nodos promedio
        avg_nodes = {}
        for algo in algorithms:
            nodes = [res['nodes_expanded'] for res in self.results[algo] if res['success']]
            if nodes:
                avg_nodes[algo] = sum(nodes) / len(nodes)
            else:
                avg_nodes[algo] = 0
        
        # Crear o usar la figura proporcionada
        if figure is None:
            fig = Figure(figsize=(8, 5))
        else:
            fig = figure
            fig.clear()
        
        ax = fig.add_subplot(111)
        
        # Crear el gráfico de barras
        bars = ax.bar(list(avg_nodes.keys()), list(avg_nodes.values()), color='lightgreen')
        
        # Añadir etiquetas y título
        ax.set_xlabel('Algoritmo')
        ax.set_ylabel('Nodos expandidos (promedio)')
        ax.set_title('Comparación de nodos expandidos')
        
        # Añadir valores sobre las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom')
        
        fig.tight_layout()
        return fig
    
    def plot_path_length(self, figure=None):
        """
        Genera un gráfico comparativo de longitudes de camino.
        
        Args:
            figure: Figura de matplotlib para dibujar. Si es None, se crea una nueva.
            
        Returns:
            Figura de matplotlib con el gráfico.
        """
        if not self.results:
            print("No hay resultados para graficar. Ejecute run_benchmark primero.")
            return None
        
        # Preparar los datos para el gráfico
        algorithms = list(self.results.keys())
        
        # Calcular longitudes promedio
        avg_length = {}
        for algo in algorithms:
            lengths = [res['path_length'] for res in self.results[algo] if res['success']]
            if lengths:
                avg_length[algo] = sum(lengths) / len(lengths)
            else:
                avg_length[algo] = 0
        
        # Crear o usar la figura proporcionada
        if figure is None:
            fig = Figure(figsize=(8, 5))
        else:
            fig = figure
            fig.clear()
        
        ax = fig.add_subplot(111)
        
        # Crear el gráfico de barras
        bars = ax.bar(list(avg_length.keys()), list(avg_length.values()), color='salmon')
        
        # Añadir etiquetas y título
        ax.set_xlabel('Algoritmo')
        ax.set_ylabel('Longitud del camino (promedio)')
        ax.set_title('Comparación de longitudes de camino')
        
        # Añadir valores sobre las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom')
        
        fig.tight_layout()
        return fig
    
    def generate_comparison_report(self, report_path="comparison_report.txt"):
        """
        Genera un informe comparativo de los algoritmos.
        
        Args:
            report_path: Ruta para guardar el informe.
        """
        if not self.results:
            print("No hay resultados para generar el informe. Ejecute run_benchmark primero.")
            return
        
        # Abrir el archivo para escribir
        with open(report_path, 'w') as f:
            f.write("INFORME COMPARATIVO DE ALGORITMOS DE BÚSQUEDA PARA 8-PUZZLE\n")
            f.write("=" * 70 + "\n\n")
            
            # Información general
            algorithms = list(self.results.keys())
            num_cases = len(self.results[algorithms[0]])
            f.write(f"Algoritmos evaluados: {', '.join(algorithms)}\n")
            f.write(f"Número de casos de prueba: {num_cases}\n\n")
            
            # Tabla de resumen
            f.write("RESUMEN DE RENDIMIENTO (promedios)\n")
            f.write("-" * 70 + "\n")
            f.write(f"{'Algoritmo':<15} | {'Éxito (%)':<10} | {'Tiempo (s)':<12} | {'Nodos':<10} | {'Longitud':<8}\n")
            f.write("-" * 70 + "\n")
            
            # Calcular métricas promedio para cada algoritmo
            for algo in algorithms:
                # Tasa de éxito
                success_rate = sum(1 for res in self.results[algo] if res['success']) / num_cases * 100
                
                # Promedios (solo para casos exitosos)
                successful_results = [res for res in self.results[algo] if res['success']]
                
                if successful_results:
                    avg_time = sum(res['execution_time'] for res in successful_results) / len(successful_results)
                    avg_nodes = sum(res['nodes_expanded'] for res in successful_results) / len(successful_results)
                    avg_length = sum(res['path_length'] for res in successful_results) / len(successful_results)
                else:
                    avg_time = avg_nodes = avg_length = 0
                
                # Escribir fila de la tabla
                f.write(f"{algo:<15} | {success_rate:<10.1f} | {avg_time:<12.6f} | {avg_nodes:<10.1f} | {avg_length:<8.1f}\n")
            
            f.write("-" * 70 + "\n\n")
            
            # Análisis y recomendaciones
            f.write("ANÁLISIS Y RECOMENDACIONES\n")
            f.write("-" * 70 + "\n")
            
            # Algoritmo más rápido
            avg_times = {}
            for algo in algorithms:
                times = [res['execution_time'] for res in self.results[algo] if res['success']]
                if times:
                    avg_times[algo] = sum(times) / len(times)
            
            if avg_times:
                fastest_algo = min(avg_times, key=avg_times.get)
                f.write(f"- Algoritmo más rápido: {fastest_algo} ({avg_times[fastest_algo]:.6f} segundos en promedio)\n")
            
            # Algoritmo más eficiente en memoria
            avg_nodes = {}
            for algo in algorithms:
                nodes = [res['nodes_expanded'] for res in self.results[algo] if res['success']]
                if nodes:
                    avg_nodes[algo] = sum(nodes) / len(nodes)
            
            if avg_nodes:
                most_efficient_algo = min(avg_nodes, key=avg_nodes.get)
                f.write(f"- Algoritmo más eficiente en memoria: {most_efficient_algo} ({int(avg_nodes[most_efficient_algo])} nodos expandidos en promedio)\n")
            
            # Algoritmo con caminos más cortos
            avg_lengths = {}
            for algo in algorithms:
                lengths = [res['path_length'] for res in self.results[algo] if res['success']]
                if lengths:
                    avg_lengths[algo] = sum(lengths) / len(lengths)
            
            if avg_lengths:
                shortest_algo = min(avg_lengths, key=avg_lengths.get)
                f.write(f"- Algoritmo con caminos más cortos: {shortest_algo} ({avg_lengths[shortest_algo]:.1f} pasos en promedio)\n")
            
            # Recomendación general
            f.write("\nRECOMENDACIÓN GENERAL:\n")
            
            if avg_times and avg_nodes and avg_lengths:
                # Normalizar los valores (menor es mejor)
                max_time = max(avg_times.values())
                max_nodes = max(avg_nodes.values())
                max_length = max(avg_lengths.values())
                
                scores = {}
                for algo in algorithms:
                    # Solo considerar algoritmos con alta tasa de éxito (>80%)
                    success_rate = sum(1 for res in self.results[algo] if res['success']) / num_cases * 100
                    if success_rate >= 80 and algo in avg_times and algo in avg_nodes and algo in avg_lengths:
                        # Ponderación: 40% tiempo, 30% memoria, 30% longitud
                        norm_time = avg_times[algo] / max_time if max_time > 0 else 0
                        norm_nodes = avg_nodes[algo] / max_nodes if max_nodes > 0 else 0
                        norm_length = avg_lengths[algo] / max_length if max_length > 0 else 0
                        
                        scores[algo] = 0.4 * norm_time + 0.3 * norm_nodes + 0.3 * norm_length
                
                if scores:
                    recommended_algo = min(scores, key=scores.get)
                    f.write(f"Para problemas similares a los evaluados, se recomienda usar el algoritmo {recommended_algo}.\n")
                    
                    f.write("\nJustificación:\n")
                    
                    if recommended_algo == fastest_algo:
                        f.write("- Es el algoritmo más rápido en promedio.\n")
                    
                    if recommended_algo == most_efficient_algo:
                        f.write("- Es el algoritmo más eficiente en términos de memoria.\n")
                    
                    if recommended_algo == shortest_algo:
                        f.write("- Encuentra los caminos más cortos en promedio.\n")
                    
                    if not (recommended_algo == fastest_algo or recommended_algo == most_efficient_algo or recommended_algo == shortest_algo):
                        f.write("- Ofrece el mejor balance entre tiempo de ejecución, uso de memoria y calidad de la solución.\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("Fin del informe")
        
        print(f"Informe generado: {report_path}")
        return report_path


class MetricsUI:
    """
    Interfaz gráfica para ejecutar y visualizar métricas de comparación de algoritmos.
    """
    def __init__(self, root=None):
        """
        Inicializa la interfaz gráfica para métricas.
        
        Args:
            root: Ventana principal de Tkinter. Si es None, se crea una nueva.
        """
        # Inicializar sistema de métricas
        self.metrics = AlgorithmMetrics()
        
        # Crear ventana principal si no se proporciona
        self.is_main_window = False
        if root is None:
            self.root = tk.Tk()
            self.root.title("Métricas de Algoritmos 8-Puzzle")
            self.root.geometry("800x600")
            self.is_main_window = True
        else:
            self.root = root
        
        # Variables de estado
        self.algorithms = ["BFS", "DFS Limitada", "A* Manhattan"]
        self.selected_algorithms = []
        for algo in self.algorithms:
            self.selected_algorithms.append(tk.BooleanVar(value=True))
        
        self.num_test_cases = tk.IntVar(value=5)
        self.min_difficulty = tk.IntVar(value=5)
        self.max_difficulty = tk.IntVar(value=15)
        
        # Crear interfaz
        self.create_widgets()
        
        # Si es ventana principal, configurar cierre
        if self.is_main_window:
            self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
    
    def create_widgets(self):
        """Crea y dispone los widgets de la interfaz."""
        # Frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panel izquierdo - Configuración
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, expand=True)
        
        # Panel derecho - Resultados y gráficos
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, expand=True)
        
        # Sección de configuración
        self.config_frame = tk.LabelFrame(self.left_frame, text="Configuración", padx=10, pady=10)
        self.config_frame.pack(fill=tk.X, pady=10)
        
        # Selección de algoritmos
        algo_label = tk.Label(self.config_frame, text="Algoritmos a comparar:")
        algo_label.pack(anchor=tk.W, pady=(5, 0))
        
        for i, algo in enumerate(self.algorithms):
            cb = tk.Checkbutton(self.config_frame, text=algo, variable=self.selected_algorithms[i])
            cb.pack(anchor=tk.W, padx=20)
        
        # Número de casos de prueba
        tk.Label(self.config_frame, text="Número de casos de prueba:").pack(anchor=tk.W, pady=(10, 0))
        ttk.Spinbox(self.config_frame, from_=1, to=20, textvariable=self.num_test_cases, width=5).pack(anchor=tk.W, padx=20)
        
        # Dificultad mínima
        tk.Label(self.config_frame, text="Dificultad mínima (movimientos):").pack(anchor=tk.W, pady=(10, 0))
        ttk.Spinbox(self.config_frame, from_=3, to=30, textvariable=self.min_difficulty, width=5).pack(anchor=tk.W, padx=20)
        
        # Dificultad máxima
        tk.Label(self.config_frame, text="Dificultad máxima (movimientos):").pack(anchor=tk.W, pady=(10, 0))
        ttk.Spinbox(self.config_frame, from_=5, to=50, textvariable=self.max_difficulty, width=5).pack(anchor=tk.W, padx=20)
        
        # Botones de acción
        self.action_frame = tk.Frame(self.left_frame)
        self.action_frame.pack(fill=tk.X, pady=10)
        
        # Botón de ejecutar benchmark
        self.run_button = tk.Button(
            self.action_frame,
            text="Ejecutar Benchmark",
            command=self.run_benchmark
        )
        self.run_button.pack(fill=tk.X, pady=5)
        
        # Botón de generar informe
        self.report_button = tk.Button(
            self.action_frame,
            text="Generar Informe",
            command=self.generate_report,
            state=tk.DISABLED
        )
        self.report_button.pack(fill=tk.X, pady=5)
        
        # Botón de guardar gráficos
        self.save_button = tk.Button(
            self.action_frame,
            text="Guardar Gráficos",
            command=self.save_plots,
            state=tk.DISABLED
        )
        self.save_button.pack(fill=tk.X, pady=5)
        
        # Panel de registro
        self.log_frame = tk.LabelFrame(self.left_frame, text="Registro", padx=10, pady=10)
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Área de texto para el registro
        self.log_text = tk.Text(self.log_frame, height=10, width=30)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Crear figuras para los gráficos
        self.fig1 = Figure(figsize=(4, 3))
        self.fig2 = Figure(figsize=(4, 3))
        self.fig3 = Figure(figsize=(4, 3))
        
        # Crear contenedores para los gráficos
        self.results_notebook = ttk.Notebook(self.right_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Página para tiempo de ejecución
        self.time_frame = tk.Frame(self.results_notebook)
        self.results_notebook.add(self.time_frame, text="Tiempo de Ejecución")
        
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.time_frame)
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Página para nodos expandidos
        self.nodes_frame = tk.Frame(self.results_notebook)
        self.results_notebook.add(self.nodes_frame, text="Nodos Expandidos")
        
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.nodes_frame)
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Página para longitud del camino
        self.path_frame = tk.Frame(self.results_notebook)
        self.results_notebook.add(self.path_frame, text="Longitud del Camino")
        
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self.path_frame)
        self.canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def log(self, message):
        """Añade un mensaje al registro."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def run_benchmark(self):
        """Ejecuta el benchmark con la configuración actual."""
        # Obtener algoritmos seleccionados
        selected = []
        for i, var in enumerate(self.selected_algorithms):
            if var.get():
                selected.append(self.algorithms[i])
        
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione al menos un algoritmo para comparar.")
            return
        
        # Validar dificultad
        min_diff = self.min_difficulty.get()
        max_diff = self.max_difficulty.get()
        
        if min_diff >= max_diff:
            messagebox.showwarning("Advertencia", "La dificultad mínima debe ser menor que la máxima.")
            return
        
        # Desactivar botones durante el benchmark
        self.run_button.config(state=tk.DISABLED)
        
        # Limpiar registro
        self.log_text.delete(1.0, tk.END)
        
        try:
            # Generar casos de prueba
            self.log("Generando casos de prueba...")
            test_cases = self.metrics.generate_test_cases(
                num_cases=self.num_test_cases.get(),
                min_difficulty=min_diff,
                max_difficulty=max_diff
            )
            
            # Ejecutar benchmark
            self.log(f"Ejecutando benchmark con {len(test_cases)} casos y algoritmos: {', '.join(selected)}")
            results = self.metrics.run_benchmark(test_cases, algorithms=selected)
            
            # Actualizar gráficos
            self.update_plots()
            
            # Habilitar botones de informe y guardar
            self.report_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            
            # Mostrar resumen
            self.log("\nResumen de resultados:")
            for algo in selected:
                successes = sum(1 for res in results[algo] if res['success'])
                if successes > 0:
                    avg_time = sum(res['execution_time'] for res in results[algo] if res['success']) / successes
                    avg_nodes = sum(res['nodes_expanded'] for res in results[algo] if res['success']) / successes
                    avg_path = sum(res['path_length'] for res in results[algo] if res['success']) / successes
                    
                    self.log(f"{algo}:")
                    self.log(f"  - Éxito: {successes}/{len(test_cases)} ({successes/len(test_cases)*100:.1f}%)")
                    self.log(f"  - Tiempo promedio: {avg_time:.6f} segundos")
                    self.log(f"  - Nodos expandidos: {avg_nodes:.1f}")
                    self.log(f"  - Longitud del camino: {avg_path:.1f}")
                else:
                    self.log(f"{algo}: No encontró soluciones.")
            
            self.log("\nBenchmark completado con éxito.")
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error al ejecutar el benchmark: {str(e)}")
        
        # Reactivar botones
        self.run_button.config(state=tk.NORMAL)
    
    def update_plots(self):
        """Actualiza los gráficos con los resultados actuales."""
        # Gráfico de tiempo de ejecución
        self.metrics.plot_execution_time(self.fig1)
        self.canvas1.draw()
        
        # Gráfico de nodos expandidos
        self.metrics.plot_nodes_expanded(self.fig2)
        self.canvas2.draw()
        
        # Gráfico de longitud del camino
        self.metrics.plot_path_length(self.fig3)
        self.canvas3.draw()
    
    def generate_report(self):
        """Genera y muestra un informe de comparación."""
        if not self.metrics.results:
            messagebox.showinfo("Información", "No hay resultados para generar un informe. Ejecute el benchmark primero.")
            return
        
        # Solicitar ruta para guardar el informe
        report_path = filedialog.asksaveasfilename(
            title="Guardar Informe",
            filetypes=[("Archivos de texto", "*.txt")],
            defaultextension=".txt"
        )
        
        if not report_path:
            return  # El usuario canceló la operación
        
        try:
            # Generar el informe
            self.log("Generando informe...")
            report_file = self.metrics.generate_comparison_report(report_path)
            
            # Preguntar si desea abrir el informe
            if messagebox.askyesno("Informe Generado", f"Informe guardado en {report_file}. ¿Desea abrirlo ahora?"):
                # Abrir el archivo con el visor predeterminado
                import os
                import subprocess
                
                if os.name == 'nt':  # Windows
                    os.startfile(report_file)
                elif os.name == 'posix':  # macOS, Linux
                    subprocess.call(('xdg-open', report_file))
            
            self.log(f"Informe guardado en {report_file}")
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error al generar el informe: {str(e)}")
    
    def save_plots(self):
        """Guarda los gráficos como archivos de imagen."""
        if not self.metrics.results:
            messagebox.showinfo("Información", "No hay gráficos para guardar. Ejecute el benchmark primero.")
            return
        
        # Solicitar directorio para guardar los gráficos
        save_dir = filedialog.askdirectory(title="Seleccionar directorio para guardar gráficos")
        
        if not save_dir:
            return  # El usuario canceló la operación
        
        try:
            # Guardar los gráficos
            self.log("Guardando gráficos...")
            
            # Tiempo de ejecución
            time_path = f"{save_dir}/tiempo_ejecucion.png"
            self.fig1.savefig(time_path)
            
            # Nodos expandidos
            nodes_path = f"{save_dir}/nodos_expandidos.png"
            self.fig2.savefig(nodes_path)
            
            # Longitud del camino
            path_path = f"{save_dir}/longitud_camino.png"
            self.fig3.savefig(path_path)
            
            self.log(f"Gráficos guardados en {save_dir}")
            messagebox.showinfo("Gráficos Guardados", f"Los gráficos se guardaron en {save_dir}")
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error al guardar los gráficos: {str(e)}")
    
    def run(self):
        """Inicia el bucle principal de la interfaz si es ventana principal."""
        if self.is_main_window:
            self.root.mainloop()


if __name__ == "__main__":
    # Ejemplo de uso independiente
    app = MetricsUI()
    app.run()