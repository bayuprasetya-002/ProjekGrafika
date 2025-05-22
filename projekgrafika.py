import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import math
from PIL import ImageGrab

root = tk.Tk()
root.title("Gambar Objek 2D dan 3D")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

canvas_width, canvas_height = 700, 500
canvas = tk.Canvas(root, bg="white", width=canvas_width, height=canvas_height)
canvas.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# === Variabel Utama ===
mode = tk.StringVar(value="2D")
shape_2d = tk.StringVar(value="square")
shape_3d = tk.StringVar(value="cube")
rotation = tk.DoubleVar(value=0)
translate_x = tk.DoubleVar(value=0)
translate_y = tk.DoubleVar(value=0)
scale_percent = tk.DoubleVar(value=100)

fill_color = "#00ccff"
outline_color = "#000000"
fill_var = tk.IntVar(value=1)
outline_var = tk.IntVar(value=1)

last_y = None
last_x = None

# === Fungsi Gambar ===
def rotate_point(x, y, angle_deg):
    angle_rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    return x * cos_a - y * sin_a, x * sin_a + y * cos_a

def project_3d(x, y, z):
    rx = math.radians(rotation.get())
    ry = math.radians(rotation.get())
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    cx = canvas_width // 2 + translate_x.get()
    cy = canvas_height // 2 + translate_y.get()
    return cx + x, cy - y

def draw():
    canvas.delete("all")
    cx = canvas_width // 2 + translate_x.get()
    cy = canvas_height // 2 + translate_y.get()
    size = scale_percent.get()
    fill = fill_color if fill_var.get() else ""
    outline = outline_color if outline_var.get() else ""

    if mode.get() == "2D":
        shape = shape_2d.get()
        if shape == "square":
            points = [(-size, -size), (size, -size), (size, size), (-size, size)]
        elif shape == "triangle":
            points = [(0, -size), (-size, size), (size, size)]
        elif shape == "circle":
            r = size
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=fill, outline=outline, width=2)
            return
        rotated = [rotate_point(x, y, rotation.get()) for x, y in points]
        coords = [coord for x, y in rotated for coord in (cx + x, cy + y)]
        canvas.create_polygon(coords, fill=fill, outline=outline, width=2)
    else:
        shape = shape_3d.get()
        if shape == "cube":
            s = size
            vertices = [(-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s),
                        (-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)]
            faces = [(0,1,2,3), (4,5,6,7), (0,1,5,4), (2,3,7,6), (1,2,6,5), (0,3,7,4)]
            projected = [project_3d(x, y, z) for x, y, z in vertices]
            for face in faces:
                coords = [coord for i in face for coord in projected[i]]
                canvas.create_polygon(coords, fill=fill, outline=outline, width=2)
        elif shape == "pyramid":
            s = size
            vertices = [(-s, -s, -s), (s, -s, -s), (0, -s, s), (0, s, 0)]
            faces = [(0,1,2), (0,1,3), (1,2,3), (2,0,3)]
            projected = [project_3d(x, y, z) for x, y, z in vertices]
            for face in faces:
                coords = [coord for i in face for coord in projected[i]]
                canvas.create_polygon(coords, fill=fill, outline=outline, width=2)
        elif shape == "cylinder":
            r = size
            h = size * 2
            top, bottom = [], []
            for deg in range(0, 360, 15):
                x = r * math.cos(math.radians(deg))
                z = r * math.sin(math.radians(deg))
                top.append(project_3d(x, h / 2, z))
                bottom.append(project_3d(x, -h / 2, z))
            for i in range(len(top) - 1):
                t1, t2 = top[i], top[i + 1]
                b1, b2 = bottom[i], bottom[i + 1]
                canvas.create_polygon([t1, t2, b2, b1], fill=fill, outline=outline, width=2)
            canvas.create_polygon([top[-1], top[0], bottom[0], bottom[-1]], fill=fill, outline=outline, width=2)
            canvas.create_polygon(top, fill=fill, outline=outline, width=2)
            canvas.create_polygon(bottom, fill=fill, outline=outline, width=2)
        elif shape == "sphere":
            r = size
            lat_lines, long_lines = 18, 36
            points = [[None for _ in range(long_lines + 1)] for _ in range(lat_lines + 1)]
            for i in range(lat_lines + 1):
                theta = math.pi * i / lat_lines
                for j in range(long_lines + 1):
                    phi = 2 * math.pi * j / long_lines
                    x = r * math.sin(theta) * math.cos(phi)
                    y = r * math.cos(theta)
                    z = r * math.sin(theta) * math.sin(phi)
                    points[i][j] = project_3d(x, y, z)
            for i in range(lat_lines):
                for j in range(long_lines):
                    p1, p2 = points[i][j], points[i][j + 1]
                    p3, p4 = points[i + 1][j + 1], points[i + 1][j]
                    canvas.create_polygon([p1, p2, p3, p4], fill=fill, outline=outline)

# === Fungsi UI ===
def pilih_fill():
    global fill_color
    color = colorchooser.askcolor()[1]
    if color:
        fill_color = color
        fill_btn.config(bg=fill_color)
        draw()

def pilih_outline():
    global outline_color
    color = colorchooser.askcolor()[1]
    if color:
        outline_color = color
        outline_btn.config(bg=outline_color)
        draw()

def save_canvas():
    filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
    if filepath:
        x = root.winfo_rootx() + canvas.winfo_x()
        y = root.winfo_rooty() + canvas.winfo_y()
        x1 = x + canvas.winfo_width()
        y1 = y + canvas.winfo_height()
        try:
            ImageGrab.grab().crop((x, y, x1, y1)).save(filepath)
            messagebox.showinfo("Berhasil", f"Gambar berhasil disimpan di:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan gambar: {e}")

def exit_app():
    root.quit()

def on_mouse_press(event):
    global last_y
    last_y = event.y

def on_mouse_drag(event):
    global last_y
    if last_y is not None:
        delta = event.y - last_y
        new_scale = max(10, min(200, scale_percent.get() - delta))
        scale_percent.set(new_scale)
        scale_entry.delete(0, tk.END)
        scale_entry.insert(0, str(int(new_scale)))
        draw()
        last_y = event.y

def on_keyboard_scale_enter(event):
    try:
        val = int(scale_entry.get())
        scale_percent.set(max(10, min(200, val)))
        draw()
    except ValueError:
        messagebox.showerror("Input Error", "Masukkan angka valid antara 10 - 200")

def on_keyboard_rotate_enter(event):
    try:
        val = float(rotate_entry.get()) % 360
        rotation.set(val)
        draw()
    except ValueError:
        messagebox.showerror("Input Error", "Masukkan angka rotasi yang valid")

def on_right_mouse_press(event):
    global last_x
    last_x = event.x

def on_right_mouse_drag(event):
    global last_x
    if last_x is not None:
        delta = event.x - last_x
        new_rotation = (rotation.get() + delta) % 360
        rotation.set(new_rotation)
        rotate_entry.delete(0, tk.END)
        rotate_entry.insert(0, str(int(new_rotation)))
        draw()
        last_x = event.x

def on_key_press(event):
    step = 10
    key = event.keysym.lower()
    if key == 'a':
        translate_x.set(translate_x.get() - step)
    elif key == 'd':
        translate_x.set(translate_x.get() + step)
    elif key == 'w':
        translate_y.set(translate_y.get() - step)
    elif key == 's':
        translate_y.set(translate_y.get() + step)
    draw()

# === Animasi Otomatis ===
animating = False

def animate():
    global animating
    if not animating:
        animating = True
        animation_loop()

def stop_animation():
    global animating
    animating = False

def animation_loop():
    if animating:
        rotation.set((rotation.get() + 2) % 360)
        rotate_entry.delete(0, tk.END)
        rotate_entry.insert(0, str(int(rotation.get())))
        draw()
        root.after(50, animation_loop)

# === UI Control Panel ===
ctrl = tk.Frame(root, bg="#f0f0f0")
ctrl.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

tk.Label(ctrl, text="Mode:", bg="#f0f0f0").grid(row=0, column=0)
tk.OptionMenu(ctrl, mode, "2D", "3D", command=lambda e: draw()).grid(row=0, column=1)

tk.Label(ctrl, text="2D Shape:", bg="#f0f0f0").grid(row=0, column=2)
tk.OptionMenu(ctrl, shape_2d, "square", "triangle", "circle", command=lambda e: draw()).grid(row=0, column=3)

tk.Label(ctrl, text="3D Shape:", bg="#f0f0f0").grid(row=1, column=2)
tk.OptionMenu(ctrl, shape_3d, "cube", "pyramid", "cylinder", "sphere", command=lambda e: draw()).grid(row=1, column=3)

tk.Label(ctrl, text="Rotate (°):", bg="#f0f0f0").grid(row=1, column=0)
rotate_entry = tk.Entry(ctrl, width=5)
rotate_entry.insert(0, str(int(rotation.get())))
rotate_entry.grid(row=1, column=1)
rotate_entry.bind("<Return>", on_keyboard_rotate_enter)

tk.Label(ctrl, text="Translate X:", bg="#f0f0f0").grid(row=2, column=0)
tk.Scale(ctrl, from_=-200, to=200, orient="horizontal", variable=translate_x, command=lambda e: draw(), length=120).grid(row=2, column=1)

tk.Label(ctrl, text="Translate Y:", bg="#f0f0f0").grid(row=2, column=2)
tk.Scale(ctrl, from_=-200, to=200, orient="horizontal", variable=translate_y, command=lambda e: draw(), length=120).grid(row=2, column=3)

tk.Label(ctrl, text="Scale (%):", bg="#f0f0f0").grid(row=3, column=0)
scale_entry = tk.Entry(ctrl, width=5)
scale_entry.insert(0, str(scale_percent.get()))
scale_entry.grid(row=3, column=1)
scale_entry.bind("<Return>", on_keyboard_scale_enter)

fill_btn = tk.Button(ctrl, text="Fill Color", bg=fill_color, command=pilih_fill)
fill_btn.grid(row=3, column=2)
outline_btn = tk.Button(ctrl, text="Line Color", bg=outline_color, command=pilih_outline)
outline_btn.grid(row=3, column=3)

tk.Checkbutton(ctrl, text="Fill", variable=fill_var, command=draw, bg="#f0f0f0").grid(row=4, column=0)
tk.Checkbutton(ctrl, text="Outline", variable=outline_var, command=draw, bg="#f0f0f0").grid(row=4, column=1)
tk.Button(ctrl, text="💾 Save", command=save_canvas).grid(row=4, column=2)
tk.Button(ctrl, text="❌ Exit", command=exit_app).grid(row=4, column=3)

tk.Button(ctrl, text="▶️ Animasi", command=animate).grid(row=6, column=0)
tk.Button(ctrl, text="⏹️ Stop", command=stop_animation).grid(row=6, column=1)

canvas.bind("<Button-1>", on_mouse_press)
canvas.bind("<B1-Motion>", on_mouse_drag)
canvas.bind("<Button-3>", on_right_mouse_press)
canvas.bind("<B3-Motion>", on_right_mouse_drag)
root.bind("<Key>", on_key_press)

draw()
root.mainloop()
