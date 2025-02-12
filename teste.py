import cv2
import pytesseract
from PIL import Image

# Caminho do Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Caminho da imagem
image_path = "assets/teste2.png"

# Carregar a imagem
image = cv2.imread(image_path)

# Converter para escala de cinza
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Testar a binarização padrão (ajuste o valor do threshold se necessário)
_, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)  # Teste com THRESH_BINARY e THRESH_BINARY_INV

# Dilatação para melhorar a detecção da barra "/"
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
binary = cv2.dilate(binary, kernel, iterations=1)

# Salvar a imagem processada para conferência
cv2.imwrite("temp_processed.png", binary)

# Configuração do Tesseract para reconhecer apenas números e "/"
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist="0123456789 /"'

# Extrair o texto da imagem processada
text = pytesseract.image_to_string(binary, config=custom_config)

# Exibir o resultado
print("Texto extraído da imagem:")
print(text[0:4])
