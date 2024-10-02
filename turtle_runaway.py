import tkinter as tk
import turtle
import random
import time

class RunawayGame:
    def __init__(self, canvas, player, pickup, num_obstacles=5, catch_radius=50):
        self.canvas = canvas
        self.player = player
        self.pickup = pickup
        self.num_obstacles = num_obstacles
        self.obstacles = []
        self.catch_radius2 = catch_radius**2
        self.score = 0
        self.start_time = None

        # Define canvas boundaries using window_width and window_height
        self.canvas_width = canvas.window_width() / 2
        self.canvas_height = canvas.window_height() / 2

        self.player.shape('turtle')
        self.player.color('dodger blue')
        self.player.penup()

        self.pickup.shape('circle')
        self.pickup.color('light green')
        self.pickup.penup()

        # Create obstacles
        for _ in range(self.num_obstacles):
            obstacle = RandomMover(canvas)
            obstacle.shape('triangle')
            obstacle.color('dim gray')
            obstacle.penup()
            obstacle.setpos(random.randint(-self.canvas_width, self.canvas_width), 
                             random.randint(-self.canvas_height, self.canvas_height))
            self.obstacles.append(obstacle)

        self.drawer = turtle.RawTurtle(canvas)
        self.drawer.hideturtle()
        self.drawer.penup()

        # Draw the border
        self.draw_border()

    def draw_border(self):
        border_turtle = turtle.RawTurtle(self.canvas)
        border_turtle.penup()
        border_turtle.goto(-self.canvas_width, self.canvas_height)
        border_turtle.pendown()
        border_turtle.color("black")
        border_turtle.pensize(3)

        for _ in range(2):
            border_turtle.forward(self.canvas_width * 2)
            border_turtle.right(90)
            border_turtle.forward(self.canvas_height * 2)
            border_turtle.right(90)

        border_turtle.hideturtle()

    def is_collided(self, obj):
        p = self.player.pos()
        q = obj.pos()
        dx, dy = p[0] - q[0], p[1] - q[1]
        return dx**2 + dy**2 < self.catch_radius2

    def start(self, ai_timer_msec=100):
        self.player.setpos(0, 0)
        self.pickup.setpos(random.randint(-300, 300), random.randint(-300, 300))

        self.score = 0
        self.start_time = time.time()
        self.ai_timer_msec = ai_timer_msec
        self.update_score_display()
        self.canvas.ontimer(self.step, self.ai_timer_msec)

    def update_score_display(self):
        self.drawer.undo()
        self.drawer.penup()
        self.drawer.setpos(-300, 300)
        elapsed_time = round(time.time() - self.start_time, 1)
        self.drawer.write(f'Score: {self.score} | Time: {elapsed_time}s', font=("Arial", 16, "normal"))

    def step(self):
        self.player.run_ai(self.pickup.pos(), self.pickup.heading())
        self.pickup.run_ai(self.player.pos(), self.player.heading())

        # Move obstacles
        for obstacle in self.obstacles:
            obstacle.run_ai(self.player.pos(), self.player.heading())

        # Check for collisions with pickup and obstacles
        if self.is_collided(self.pickup):
            self.score += 1
            self.pickup.setpos(random.randint(-300, 300), random.randint(-300, 300))
        
        for obstacle in self.obstacles:
            if self.is_collided(obstacle):
                self.score -= 1
                obstacle.setpos(random.randint(-300, 300), random.randint(-300, 300))

        self.update_score_display()

        if self.score >= 10:
            elapsed_time = round(time.time() - self.start_time, 1)
            self.drawer.setpos(0, 0)
            self.drawer.write(f'You won! Time: {elapsed_time}s', align="center", font=("Arial", 24, "bold"))
        else:
            self.canvas.ontimer(self.step, self.ai_timer_msec)

    def wall_checker(self, turtle_obj):
        x, y = turtle_obj.pos()
        if x < -self.canvas_width:
            turtle_obj.setx(-self.canvas_width)
        elif x > self.canvas_width:
            turtle_obj.setx(self.canvas_width)

        if y < -self.canvas_height:
            turtle_obj.sety(-self.canvas_height)
        elif y > self.canvas_height:
            turtle_obj.sety(self.canvas_height)

class ManualMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn

        canvas.onkeypress(lambda: self.move_within_bounds('forward'), 'Up')
        canvas.onkeypress(lambda: self.move_within_bounds('backward'), 'Down')
        canvas.onkeypress(lambda: self.left(self.step_turn), 'Left')
        canvas.onkeypress(lambda: self.right(self.step_turn), 'Right')
        canvas.listen()

    def move_within_bounds(self, direction):
        if direction == 'forward':
            self.forward(self.step_move)
        elif direction == 'backward':
            self.backward(self.step_move)
        game.wall_checker(self)

    def run_ai(self, opp_pos, opp_heading):
        pass

class RandomMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.speed = -1
        self.step_move = step_move
        self.step_turn = step_turn
        self.canvas = canvas  # Store the canvas reference for wall checking

    def run_ai(self, opp_pos, opp_heading):
        # Randomly move the obstacle
        mode = random.randint(0, 2)
        if mode == 0:
            self.forward(self.step_move)
        elif mode == 1:
            self.left(self.step_turn)
        elif mode == 2:
            self.right(self.step_turn)

        # Check for walls after moving
        self.wall_checker()

    def wall_checker(self):
        x, y = self.pos()
        if x < -self.canvas.window_width() / 2:
            self.setx(-self.canvas.window_width() / 2)
        elif x > self.canvas.window_width() / 2:
            self.setx(self.canvas.window_width() / 2)
        if y < -self.canvas.window_height() / 2:
            self.sety(-self.canvas.window_height() / 2)
        elif y > self.canvas.window_height() / 2:
            self.sety(self.canvas.window_height() / 2)

if __name__ == '__main__':
    root = tk.Tk()
    canvas = tk.Canvas(root, width=700, height=700)
    canvas.pack()
    screen = turtle.TurtleScreen(canvas)
    screen.bgcolor("lavender blush")

    pickup = RandomMover(screen)
    player = ManualMover(screen)

    game = RunawayGame(screen, player, pickup, num_obstacles=5)  # Create a specified number of obstacles
    game.start()
    screen.mainloop()
