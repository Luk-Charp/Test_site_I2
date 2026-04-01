import cv2

def process_image(image_path):

    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Erreur : image introuvable.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 50, 150)

    # Thinning
    try:
        thresh = cv2.ximgproc.thinning(thresh)
    except:
        print("Thinning non disponible")

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_NONE
    )

    height = gray.shape[0]

    return contours, height