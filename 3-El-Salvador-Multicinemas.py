from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import datetime

def extract_movie_data(container):
    """Extrae datos de un contenedor de película."""
    try:
        # Extrayendo el título
        title = container.find_element(By.XPATH, ".//span[@class='media-heading']").text

        # Extrayendo el nombre del cine desde el elemento <font>
        cinema_name = container.find_element(By.XPATH, ".//font[contains(text(),'Complejo')]").text

        # Extrayendo el idioma y formato desde el texto que contiene "Español 2D"
        format_language = container.find_element(By.XPATH, ".//font[contains(text(),'Español') or contains(text(),'Sub') or contains(text(),'Doblada')]").text.strip()
        
        # Dividimos el string para obtener el idioma y formato
        parts = format_language.split()
        if len(parts) >= 2:
            language, format_type = parts[:2]  # Asumiendo que siempre será algo como "Español 2D"
        else:
            language = format_language
            format_type = "Desconocido"
        
        # Ajustamos el idioma según la regla solicitada
        if language.lower() in ["doblada", "español"]:
            language = "Dob"
        elif language.lower() == "subtitulada":
            language = "Sub"
        
        # Extrayendo los horarios de las películas
        buttons = container.find_elements(By.XPATH, ".//button[@class='btn btn-info']")
        showtimes = [button.text for button in buttons]

        # Guardar los datos de la película
        movie_data = []
        for showtime in showtimes:
            movie_data.append([
                datetime.datetime.now().strftime("%m-%d-%Y"),
                "El Salvador",
                "Multicinema",
                cinema_name.replace("Complejo: ", ""),  
                title,
                showtime,
                language, 
                format_type,  
            ])
        return movie_data

    except Exception as e:
        print(f"Error al procesar un contenedor: {e}")
        return []

# --- Código principal ---
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')  # Desactiva la aceleración por GPU
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
url = "https://www.multicinema.com.sv/Cartelera.php"
driver.get(url)

data = []
today_date = datetime.datetime.now().strftime("%d/%m/%Y")

try:
    # Encontrar todos los contenedores de películas usando los IDs dinámicos que cambian
    i = 495356  # Empezamos desde el ID base que proporcionaste
    while True:
        try:
            # Intentamos encontrar el contenedor de la película con el ID actual
            container = driver.find_element(By.XPATH, f"//*[@id='horarios{i}']")
            # Si se encuentra, extraemos los datos de la película
            data.extend(extract_movie_data(container))
            i += 1  # Incrementamos el ID para el siguiente contenedor
        except Exception as e:
            
            break  # Si no se encuentra el siguiente contenedor, detenemos el bucle

finally:
    driver.quit()

# Exportamos los datos a Excel, sin las columnas de Clasificación, Promoción y Duración
df = pd.DataFrame(data, columns=["Fecha", "Pais", "Cine", "Nombre Cine", "Título", "Hora","Idioma", "Formato"])
df.to_excel("cartelera_multicinema.xlsx", index=False, engine='openpyxl')

print("Datos exportados a cartelera_multicinema.xlsx")
