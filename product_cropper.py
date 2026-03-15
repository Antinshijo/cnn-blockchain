import cv2

def crop_product(image_path):

    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray,(5,5),0)

    edges = cv2.Canny(blur,50,150)

    contours,_ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:

        largest = max(contours, key=cv2.contourArea)

        x,y,w,h = cv2.boundingRect(largest)

        cropped = image[y:y+h, x:x+w]

        cv2.imwrite(image_path, cropped)

    return image_path