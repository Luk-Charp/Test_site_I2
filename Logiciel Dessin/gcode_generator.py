import os
from path_optimizer import distance
from config import *
from config import MACHINE_WIDTH, MACHINE_HEIGHT, MARGIN


def compute_bounding_box(contours, height):
    min_x, min_y = float("inf"), float("inf")
    max_x, max_y = float("-inf"), float("-inf")

    for contour in contours:
        for point in contour:
            x = point[0][0]
            y = height - point[0][1]

            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

    return min_x, min_y, max_x, max_y


def generate_gcode(contours, height):

    gcode = []

    # ===== MÉTRIQUES =====
    total_distance = 0
    pen_lifts = 0
    total_points = 0

    # ===== SCALE AUTOMATIQUE =====
    min_x, min_y, max_x, max_y = compute_bounding_box(contours, height)

    drawing_width = max_x - min_x
    drawing_height = max_y - min_y

    available_width = MACHINE_WIDTH - 2 * MARGIN
    available_height = MACHINE_HEIGHT - 2 * MARGIN

    scale_x = available_width / drawing_width
    scale_y = available_height / drawing_height

    auto_scale = min(scale_x, scale_y)

    print(f"Scale automatique appliqué : {auto_scale:.3f}")

    gcode.append("G21")        # Unités en mm
    gcode.append("G90")        # Coordonnées absolues
    gcode.append("G92 X0 Y0")  # Définir origine (plus de Z)
    gcode.append(f"M3 S{PEN_UP_SPINDLE}")   # Stylo levé au démarrage

    last_point = None

    for contour in contours:
        first_point = contour[0][0]
        x_start = (first_point[0] - min_x) * auto_scale + MARGIN
        y_start = ((height - first_point[1]) - min_y) * auto_scale + MARGIN

        start_point = (x_start, y_start)

        # Vérifier si levée nécessaire
        if last_point is None or distance(last_point, start_point) > MIN_TRAVEL_DIST:
            gcode.append(f"M3 S{PEN_UP_SPINDLE}")
            gcode.append("G4 P0.05")            # Lever le stylo
            gcode.append(f"G0 X{x_start:.2f} Y{y_start:.2f}") # Déplacement rapide
            gcode.append(f"M3 S{PEN_DOWN_SPINDLE}")
            gcode.append("G4 P0.1")  # pause 0.1s           # Baisser le stylo
            pen_lifts += 1
        else:
            gcode.append(f"G1 X{x_start:.2f} Y{y_start:.2f} F{FEEDRATE}")
            total_distance += distance(last_point, start_point)

        last_point = start_point

        for point in contour:
            x = (point[0][0] - min_x) * auto_scale + MARGIN
            y = ((height - point[0][1]) - min_y) * auto_scale + MARGIN
            new_point = (x, y)

            gcode.append(f"G1 X{x:.2f} Y{y:.2f} F{FEEDRATE}")

            total_distance += distance(last_point, new_point)
            total_points += 1
            last_point = new_point

    gcode.append(f"M3 S{PEN_UP_SPINDLE}")
    gcode.append("G4 P0.05")  # Lever le stylo en fin de programme
    gcode.append("G0 X0 Y0")              # Retour à l'origine
    gcode.append("M5")                    # Arrêt moteur broche
    gcode.append("M2")                    # Fin programme

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(gcode))

    print("G-code optimisé généré avec succès.")

    # ===== STATISTIQUES =====
    estimated_time_min = total_distance / FEEDRATE

    print("\n------ STATISTIQUES ------")
    print(f"Points totaux : {total_points}")
    print(f"Distance totale : {total_distance:.2f} mm")
    print(f"Levées de stylo : {pen_lifts}")
    print(f"Temps estimé : {estimated_time_min:.2f} minutes (approx)")
    print("--------------------------\n")

    return total_points, total_distance, pen_lifts, estimated_time_min