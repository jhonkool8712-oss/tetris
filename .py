import tkinter as tk
import random

try:
    import winsound
except ImportError:
    winsound = None

# Parametros del juego
ANCHO = 300
ALTO = 600
TAM_BLOQUE = 30
COLUMNAS = ANCHO // TAM_BLOQUE
FILAS = ALTO // TAM_BLOQUE
PUNTOS_PARA_GANAR = 100
COLORES = ["red", "blue", "green", "yellow", "purple", "orange", "cyan"]
PIEZAS = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "L": [[1, 0, 0], [1, 1, 1]],
    "J": [[0, 0, 1], [1, 1, 1]]
}

class TetrisGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Tetris")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=ANCHO, height=ALTO, bg="black")
        self.canvas.pack()

        self.sonidos_activados = True

        control_frame = tk.Frame(self.root, bg="black")
        control_frame.pack(fill="x", pady=4)

        self.score_label = tk.Label(control_frame, text="Puntos: 0", fg="white", bg="black", font=("Arial", 10, "bold"))
        self.score_label.pack(side="left", padx=8)

        self.level_label = tk.Label(control_frame, text="Nivel: 1", fg="white", bg="black", font=("Arial", 10, "bold"))
        self.level_label.pack(side="left", padx=8)

        self.start_button = tk.Button(control_frame, text="Iniciar juego", command=self.iniciar_juego, bg="#3cb371", fg="white")
        self.start_button.pack(side="right", padx=8)

        self.instrucciones = tk.Label(
            self.root,
            text="← → Mover | ↑ Rotar | Espacio Fijar rápido",
            fg="white",
            bg="black",
            font=("Arial", 10),
        )
        self.instrucciones.pack(pady=(0, 4))

        self.root.bind("<Left>", self.mover_izquierda)
        self.root.bind("<Right>", self.mover_derecha)
        self.root.bind("<Up>", self.rotar)
        self.root.bind("<space>", lambda event: self.fijar_pieza())

        self.reset_game()

    def reset_game(self):
        self.tablero = [[0] * COLUMNAS for _ in range(FILAS)]
        self.pieza_actual = None
        self.color_actual = None
        self.pos_x = 0
        self.pos_y = 0
        self.game_active = False
        self.score = 0
        self.level = 1
        self.speed = 500
        self.score_label.config(text="Puntos: 0")
        self.level_label.config(text="Nivel: 1")
        self.canvas.delete("all")

    def reproducir_sonido(self, frecuencia=750, duracion=100):
        if winsound is None or not self.sonidos_activados:
            return
        try:
            winsound.Beep(frecuencia, duracion)
        except RuntimeError:
            pass

    def nueva_pieza(self):
        self.pieza_actual = random.choice(list(PIEZAS.values()))
        self.color_actual = random.choice(COLORES)
        self.pos_x = COLUMNAS // 2 - len(self.pieza_actual[0]) // 2
        self.pos_y = 0
        if self.colision(self.pos_x, self.pos_y, self.pieza_actual):
            self.game_over()

    def ganar_juego(self):
        self.game_active = False
        self.reproducir_sonido(1200, 400)
        self.canvas.create_text(
            ANCHO // 2,
            ALTO // 2,
            text="¡Ganaste!",
            fill="white",
            font=("Arial", 24, "bold"),
        )
        self.canvas.create_text(
            ANCHO // 2,
            ALTO // 2 + 40,
            text=f"Puntos: {self.score} | Nivel: {self.level}",
            fill="white",
            font=("Arial", 14),
        )

    def dibujar(self):
        self.canvas.delete("all")
        for y in range(FILAS):
            for x in range(COLUMNAS):
                if self.tablero[y][x]:
                    self.canvas.create_rectangle(
                        x * TAM_BLOQUE,
                        y * TAM_BLOQUE,
                        (x + 1) * TAM_BLOQUE,
                        (y + 1) * TAM_BLOQUE,
                        fill=self.tablero[y][x],
                        outline="gray",
                    )
        if self.pieza_actual is not None:
            for y in range(len(self.pieza_actual)):
                for x in range(len(self.pieza_actual[0])):
                    if self.pieza_actual[y][x]:
                        self.canvas.create_rectangle(
                            (self.pos_x + x) * TAM_BLOQUE,
                            (self.pos_y + y) * TAM_BLOQUE,
                            (self.pos_x + x + 1) * TAM_BLOQUE,
                            (self.pos_y + y + 1) * TAM_BLOQUE,
                            fill=self.color_actual,
                            outline="white",
                        )

    def colision(self, px, py, pieza):
        for y in range(len(pieza)):
            for x in range(len(pieza[0])):
                if pieza[y][x]:
                    if px + x < 0 or px + x >= COLUMNAS or py + y >= FILAS:
                        return True
                    if py + y >= 0 and self.tablero[py + y][px + x]:
                        return True
        return False

    def fijar_pieza(self):
        if not self.game_active or self.pieza_actual is None:
            return
        for y in range(len(self.pieza_actual)):
            for x in range(len(self.pieza_actual[0])):
                if self.pieza_actual[y][x] and self.pos_y + y >= 0:
                    self.tablero[self.pos_y + y][self.pos_x + x] = self.color_actual
        self.limpiar_lineas()
        self.score += 1
        self.score_label.config(text=f"Puntos: {self.score}")
        self.reproducir_sonido(1000, 80)
        if self.score >= PUNTOS_PARA_GANAR:
            self.ganar_juego()
            return
        if self.score % 10 == 0:
            self.level += 1
            self.speed = max(100, self.speed - 50)
            self.level_label.config(text=f"Nivel: {self.level}")
            self.reproducir_sonido(900, 150)
        self.nueva_pieza()

    def limpiar_lineas(self):
        nuevas_filas = [fila for fila in self.tablero if any(c == 0 for c in fila)]
        lineas_eliminadas = FILAS - len(nuevas_filas)
        for _ in range(lineas_eliminadas):
            nuevas_filas.insert(0, [0] * COLUMNAS)
        self.tablero = nuevas_filas

    def bajar(self):
        if not self.game_active:
            return
        if not self.colision(self.pos_x, self.pos_y + 1, self.pieza_actual):
            self.pos_y += 1
            self.reproducir_sonido(800, 40)
        else:
            self.fijar_pieza()
            if not self.game_active:
                return
            self.reproducir_sonido(600, 100)
        self.dibujar()
        if self.game_active:
            self.root.after(self.speed, self.bajar)

    def mover_izquierda(self, event=None):
        if self.game_active and not self.colision(self.pos_x - 1, self.pos_y, self.pieza_actual):
            self.pos_x -= 1
            self.dibujar()

    def mover_derecha(self, event=None):
        if self.game_active and not self.colision(self.pos_x + 1, self.pos_y, self.pieza_actual):
            self.pos_x += 1
            self.dibujar()

    def rotar(self, event=None):
        if not self.game_active:
            return
        rotada = [list(fila) for fila in zip(*self.pieza_actual[::-1])]
        if not self.colision(self.pos_x, self.pos_y, rotada):
            self.pieza_actual = rotada
            self.dibujar()

    def game_over(self):
        self.game_active = False
        self.reproducir_sonido(300, 400)
        self.canvas.create_text(
            ANCHO // 2,
            ALTO // 2,
            text="Juego terminado",
            fill="white",
            font=("Arial", 24, "bold"),
        )
        self.canvas.create_text(
            ANCHO // 2,
            ALTO // 2 + 40,
            text=f"Puntos: {self.score} | Nivel: {self.level}",
            fill="white",
            font=("Arial", 14),
        )

    def iniciar_juego(self):
        self.reset_game()
        self.game_active = True
        self.nueva_pieza()
        self.dibujar()
        self.bajar()


def run_tetris(root):
    TetrisGame(root)


if __name__ == "__main__":
    ventana = tk.Tk()
    run_tetris(ventana)
    ventana.mainloop()
