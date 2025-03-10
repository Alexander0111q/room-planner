import sqlite3
import tkinter as tk
from tkinter import messagebox
from pygame.locals import *
import pygame
import sqlite3

class RoomPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Room Planner")

        # Create and configure the menu bar
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Create room management section
        self.room_frame = tk.Frame(root, padx=10, pady=10)
        self.room_frame.pack()

        room_name_label = tk.Label(self.room_frame, text="Room name")
        room_name_label.pack()
        self.room_name_entry = tk.Entry(self.room_frame)
        self.room_name_entry.pack()

        add_room_button = tk.Button(self.room_frame, text="Add room", command=self.add_room, bg="green", fg="white", padx=10, pady=5)
        add_room_button.pack(pady=10)

        room_id_label = tk.Label(self.room_frame, text="Room ID to delete")
        room_id_label.pack()
        self.room_id_entry = tk.Entry(self.room_frame)
        self.room_id_entry.pack()

        delete_room_button = tk.Button(self.room_frame, text="Delete room", command=self.delete_room, bg="red", fg="white", padx=10, pady=5)
        delete_room_button.pack()

        # Create furniture management section
        self.furniture_frame = tk.Frame(root, padx=10, pady=10)
        self.furniture_frame.pack()

        furniture_name_label = tk.Label(self.furniture_frame, text="Furniture name")
        furniture_name_label.pack()
        self.furniture_name_entry = tk.Entry(self.furniture_frame)
        self.furniture_name_entry.pack()

        furniture_x_label = tk.Label(self.furniture_frame, text="Furniture x")
        furniture_x_label.pack()
        self.furniture_x_entry = tk.Entry(self.furniture_frame)
        self.furniture_x_entry.pack()

        furniture_y_label = tk.Label(self.furniture_frame, text="Furniture y")
        furniture_y_label.pack()
        self.furniture_y_entry = tk.Entry(self.furniture_frame)
        self.furniture_y_entry.pack()

        furniture_rotation_label = tk.Label(self.furniture_frame, text="Furniture rotation")
        furniture_rotation_label.pack()
        self.furniture_rotation_entry = tk.Entry(self.furniture_frame)
        self.furniture_rotation_entry.pack()

        add_furniture_button = tk.Button(self.furniture_frame, text="Add furniture", command=self.add_furniture, bg="green", fg="white", padx=10, pady=5)
        add_furniture_button.pack(pady=10)

        furniture_id_label = tk.Label(self.furniture_frame, text="Furniture ID to delete")
        furniture_id_label.pack()
        self.furniture_id_entry = tk.Entry(self.furniture_frame)
        self.furniture_id_entry.pack()

        delete_furniture_button = tk.Button(self.furniture_frame, text="Delete furniture", command=self.delete_furniture, bg="red", fg="white", padx=10, pady=5)
        delete_furniture_button.pack()

        show_room = tk.Button(root, text="Show", command=self.start)
        show_room.pack()


        # Initialize the room planner
        self.init_room_planner()

    def start(self):


        pygame.init()
        screen_width = 800
        screen_height = 600
        background_color = (230, 230, 230)

        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Планирование комнаты")

        def create_database():
            conn = sqlite3.connect("room.db")
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS room_sizes (room_id INTEGER, width INTEGER, height INTEGER, FOREIGN KEY(room_id) REFERENCES rooms(id))"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS furniture (id INTEGER PRIMARY KEY AUTOINCREMENT, room_id INTEGER, name TEXT, x INTEGER, y INTEGER, rotation INTEGER, FOREIGN KEY(room_id) REFERENCES rooms(id))"
            )
            conn.commit()
            conn.close()

        def add_room_size(room_id, width, height):
            conn = sqlite3.connect("room.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO room_sizes (room_id, width, height) VALUES (?, ?, ?)",
                (room_id, width, height)
            )
            conn.commit()
            conn.close()

        create_database()

        def create_database():
            conn = sqlite3.connect("room.db")
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS furniture (id INTEGER PRIMARY KEY AUTOINCREMENT, room_id INTEGER, name TEXT, x INTEGER, y INTEGER, rotation INTEGER)"
            )
            conn.commit()
            conn.close()

        create_database()

        class Furniture:
            def __init__(self, name, x, y, rotation):
                self.name = name
                self.x = x
                self.y = y
                self.rotation = rotation
                self.image = pygame.image.load(f"{name}.png")

            def draw(self, surface):
                rotated_image = pygame.transform.rotate(self.image, self.rotation)
                rect = rotated_image.get_rect()
                rect.center = (self.x, self.y)
                surface.blit(rotated_image, rect)

            def is_clicked(self, pos):
                return self.image.get_rect(topleft=(self.x, self.y)).collidepoint(pos)

        def get_all_furniture(room_id):
            conn = sqlite3.connect("room.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM furniture WHERE room_id=?", (room_id,))
            furniture_data = cursor.fetchall()
            conn.close()

            furniture_objects = []
            for furniture in furniture_data:
                furniture_objects.append(Furniture(furniture[2], furniture[3], furniture[4], furniture[5]))

            return furniture_objects

        def get_furniture_at_cursor(pos, furniture_list):
            for furniture in furniture_list:
                if furniture.is_clicked(pos):
                    return furniture
            return None

        def check_collision(rect1, rect2):
            return rect1.colliderect(rect2)

        def move_furniture(selected_furniture, new_x, new_y, furniture_list):
            old_x, old_y = selected_furniture.x, selected_furniture.y
            selected_furniture.x, selected_furniture.y = new_x, new_y

            selected_rect = selected_furniture.image.get_rect(topleft=(new_x, new_y))
            for furniture in furniture_list:
                if furniture is not selected_furniture:
                    furniture_rect = furniture.image.get_rect(topleft=(furniture.x, furniture.y))
                    if check_collision(selected_rect, furniture_rect):
                        selected_furniture.x, selected_furniture.y = old_x, old_y  # Вернуть мебель обратно, если есть коллизия
                        return

            update_furniture_position_in_db(selected_furniture)

        def update_furniture_position_in_db(furniture):
            conn = sqlite3.connect("room.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE furniture SET x=?, y=? WHERE name=?",
                (furniture.x, furniture.y, furniture.name)
            )
            conn.commit()
            conn.close()

        def draw_furniture(furniture_list):
            for furniture in furniture_list:
                furniture.draw(screen)

        def main():
            running = True
            selected_furniture = None
            grabbed_offset_x = 0
            grabbed_offset_y = 0
            furniture_list = get_all_furniture(1)  # предполагаем, что у нас есть комната с id 1
            while running:
                screen.fill(background_color)
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                    if event.type == MOUSEBUTTONDOWN:
                        if event.button == 1:
                            mouse_pos = pygame.mouse.get_pos()
                            selected_furniture = get_furniture_at_cursor(mouse_pos, furniture_list)
                            if selected_furniture:
                                grabbed_offset_x = mouse_pos[0] - selected_furniture.x
                                grabbed_offset_y = mouse_pos[1] - selected_furniture.y
                    if event.type == MOUSEBUTTONUP:
                        if event.button == 1:
                            selected_furniture = None
                if selected_furniture:
                    mouse_pos = pygame.mouse.get_pos()
                    new_x = mouse_pos[0] - grabbed_offset_x
                    new_y = mouse_pos[1] - grabbed_offset_y
                    move_furniture(selected_furniture, new_x, new_y, furniture_list)
                draw_furniture(furniture_list)
                pygame.display.flip()
            pygame.quit()

        main()
    def init_room_planner(self):
        # Connect to the database and create necessary tables
        conn = sqlite3.connect("room.db")
        cursor = conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS furniture (id INTEGER PRIMARY KEY AUTOINCREMENT, room_id INTEGER, name TEXT, x INTEGER, y INTEGER, rotation INTEGER)"
        )

        conn.commit()
        conn.close()

    def add_room(self):
        name = self.room_name_entry.get()
        conn = sqlite3.connect("room.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rooms (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Info", "Room added successfully")

    def delete_room(self):
        room_id = self.room_id_entry.get()
        conn = sqlite3.connect("room.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rooms WHERE id=?", (room_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Info", "Room deleted successfully")

    def add_furniture(self):
        room_id = self.room_id_entry.get()
        name = self.furniture_name_entry.get()
        x = self.furniture_x_entry.get()
        y = self.furniture_y_entry.get()
        rotation = self.furniture_rotation_entry.get()

        conn = sqlite3.connect("room.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO furniture (room_id, name, x, y, rotation) VALUES (?, ?, ?, ?, ?)",
            (room_id, name, x, y, rotation),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Info", "Furniture added successfully")

    def delete_furniture(self):
        furniture_id = self.furniture_id_entry.get()
        conn = sqlite3.connect("room.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM furniture WHERE id=?", (furniture_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Info", "Furniture deleted successfully")


root = tk.Tk()
app = RoomPlannerApp(root)
root.mainloop()
