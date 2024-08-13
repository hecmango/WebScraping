from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import datetime

# Configura las opciones del navegador
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Inicia el navegador en pantalla completa

# Inicia el driver de Chrome con las opciones configuradas
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# Abre la URL
url = "https://www.multicinema.com.sv/Cartelera.php"
driver.get(url)

# Lista para almacenar los datos
data = []

# Obtiene la fecha actual
today_date = datetime.datetime.now().strftime("%d/%m/%Y")

# Espera hasta que los contenedores de películas estén presentes
try:
    # Encuentra todos los contenedores de películas usando el XPath general
    containers = driver.find_elements(By.XPATH, "//div[contains(@id, 'horarios')]")
    
    for container in containers:
        try:
            # Extrae el título
            title = container.find_element(By.XPATH, ".//span[@class='media-heading']").text
            
            # Extrae el formato y idioma
            format_and_language = container.find_element(By.XPATH, ".//font[contains(text(),'Español')]").text

            # Extrae el dato "Complejo"
            complejo_text = container.find_element(By.XPATH, ".//font[contains(text(), 'Complejo')]").text
            complejo = complejo_text.split(":")[1].strip()
            
            # Extrae los horarios
            buttons = container.find_elements(By.XPATH, ".//button[@class='btn btn-info']")
            showtimes = [button.text for button in buttons]

            # Divide formato e idioma
            format_and_language_parts = format_and_language.split()
            language = format_and_language_parts[0]
            format_type = ' '.join(format_and_language_parts[1:])

            # Agrega los datos a la lista
            for showtime in showtimes:
                data.append([
                    today_date,
                    "El Salvador",
                    "Multicinema",
                    complejo,
                    title,
                    format_type,
                    language,
                    showtime
                ])

        except Exception as e:
            print(f"Error al procesar un contenedor: {e}")

finally:
    # Espera 10 segundos para que puedas ver la página antes de cerrar el navegador
    import time
    time.sleep(10)
    driver.quit()

# Crea un DataFrame y guarda los datos en un archivo Excel
df = pd.DataFrame(data, columns=["Fecha", "Pais", "Cine", "Nombre Cine", "Título", "Formato", "Idioma", "Horario"])
df.to_excel("cartelera_multicinema.xlsx", index=False, engine='openpyxl')

print("Datos exportados a cartelera_multicinema.xlsx")
