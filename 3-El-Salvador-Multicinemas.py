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
        title = WebDriverWait(container, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//span[@class='media-heading']"))
        ).text

        format_and_language_element = WebDriverWait(container, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//font[contains(text(),'Español')]"))
        )
        format_and_language = format_and_language_element.text

        # XPath corregido para Complejo
        complejo_text = container.find_element(By.XPATH, ".//div[@class='panel-heading']/h3[2]/center").text
        complejo = complejo_text.split(":")[1].strip()

        buttons = container.find_elements(By.XPATH, ".//button[@class='btn btn-info']")
        showtimes = [button.text for button in buttons]

        format_and_language_parts = format_and_language.split()
        language = format_and_language_parts[0]
        format_type = ' '.join(format_and_language_parts[1:])

        movie_data = []
        for showtime in showtimes:
            movie_data.append([
                today_date,
                "El Salvador",
                "Multicinema",
                complejo,
                title,
                format_type,
                language,
                showtime
            ])
        return movie_data

    except Exception as e:
        print(f"Error al procesar un contenedor: {e}")
        return []

# --- Código principal ---
driver = webdriver.Chrome()
driver.maximize_window()
url = "https://www.multicinema.com.sv/Cartelera.php"
driver.get(url)

data = []
today_date = datetime.datetime.now().strftime("%d/%m/%Y")

try:
    containers = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'panel panel-info')]"))
    )

    for container in containers:
        data.extend(extract_movie_data(container))

finally:
    driver.quit()

df = pd.DataFrame(data, columns=["Fecha", "Pais", "Cine", "Nombre Cine", "Título", "Formato", "Idioma", "Horario"])
df.to_excel("cartelera_multicinema.xlsx", index=False, engine='openpyxl')

print("Datos exportados a cartelera_multicinema.xlsx")