import cv2
import math

def distance(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

def simplify_contours(contours):
    simplified = []
    for contour in contours:
        epsilon = 0.003 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) > 2:
            simplified.append(approx)
    return simplified

def sort_contours(contours):
    contours = list(contours)
    sorted_contours = []

    current = contours.pop(0)
    sorted_contours.append(current)
    current_point = current[-1][0]

    while contours:
        min_dist = float("inf")
        min_index = 0
        reverse_needed = False

        for i, contour in enumerate(contours):
            start = contour[0][0]
            end = contour[-1][0]

            d_start = distance(current_point, start)
            d_end = distance(current_point, end)

            if d_start < min_dist:
                min_dist = d_start
                min_index = i
                reverse_needed = False

            if d_end < min_dist:
                min_dist = d_end
                min_index = i
                reverse_needed = True

        chosen = contours.pop(min_index)

        if reverse_needed:
            chosen = chosen[::-1]

        sorted_contours.append(chosen)
        current_point = chosen[-1][0]

    return sorted_contours

def optimize_paths(contours):
    contours = simplify_contours(contours)
    contours = sort_contours(contours)
    return contours