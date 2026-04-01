import tkinter as ttk
from tkinter import filedialog, messagebox
import config
from image_processing import process_image
from path_optimizer import optimize_paths
from gcode_generator import generate_gcode


class PlotterApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Logiciel Dessin Groupe 04 v1.0")
        self.root.geometry("600x500")
        self.root.configure(bg="#2c3e50")

        self.image_path = config.IMAGE_PATH

        self.create_widgets()

    def create_widgets(self):

        main_frame = ttk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ttk.Label(
            main_frame,
            text="Logiciel Machine That Draws",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title.pack(pady=20)

        ttk.Button(
            main_frame,
            text="Choisir une image",
            command=self.select_image
        ).pack(pady=10)

        ttk.Button(
            main_frame,
            text="Générer G-code",
            command=self.generate
        ).pack(pady=10)

        self.stats_text = ttk.Text(
            main_frame,
            height=10,
            width=60,
            bg="#ecf0f1"
        )
        self.stats_text.pack(pady=20)

        self.precision_slider = ttk.Scale(self.root, from_=1, to=10, orient="horizontal")
        self.precision_slider.set(3)
        self.precision_slider.pack()

        self.speed_entry = ttk.Entry(self.root)
        self.speed_entry.insert(0, "1200")
        self.speed_entry.pack()

    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.image_path = file_path
            messagebox.showinfo("Image sélectionnée", file_path)

    def generate(self):
        try:
            contours, height = process_image(self.image_path)
            contours = optimize_paths(contours)
            config.FEEDRATE = int(self.speed_entry.get())
            stats = generate_gcode(contours, height)

            self.display_stats(stats)

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def display_stats(self, stats):
        total_points, total_distance, pen_lifts, estimated_time = stats

        self.stats_text.delete("1.0", ttk.END)
        self.stats_text.insert(ttk.END, "----- STATISTIQUES -----\n")
        self.stats_text.insert(ttk.END, f"Points totaux : {total_points}\n")
        self.stats_text.insert(ttk.END, f"Distance totale : {total_distance:.2f} mm\n")
        self.stats_text.insert(ttk.END, f"Levées de stylo : {pen_lifts}\n")
        self.stats_text.insert(ttk.END, f"Temps estimé : {estimated_time:.2f} min\n")
        self.stats_text.insert(ttk.END, "------------------------\n")


if __name__ == "__main__":
    root = ttk.Tk()
    app = PlotterApp(root)
    root.mainloop()