import ctypes
import time
import hex_codes
import cv2
from matplotlib import pyplot as plt

if __name__ == '__main__':
    img = cv2.imread("water_74.png")

    if img is None:
        print("Erro ao carregar a imagem. Verifique o caminho.")
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)

        cv2.imshow("xesquedele", thresh)

        if cv2.waitKey(0) & 0xFF == ord("v"):
            cv2.destroyAllWindows()
