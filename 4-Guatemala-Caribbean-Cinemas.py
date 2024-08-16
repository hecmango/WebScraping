from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd

# Inicialización del navegador y maximización de pantalla
driver = webdriver.Chrome()
driver.maximize_window()

# Navegar a la página
url = 'https://cinestar.com.gt/'
driver.get(url)

def map_idioma(idioma_original):
    #Función para mapear el idioma a 'Dob' o 'Sub'
    idioma_map = {
        'ESPAÑOL': 'DOB',
        'SPANISH': 'DOB',
        'ENGLISH': 'SUB',
        'CXC ESPAÑOL': 'DOB'
    }
    return idioma_map.get(idioma_original, 'Desconocido')  # Valor predeterminado si no coincide

try:

    # Lista de cines a procesar
    cines = [
        {'nombre': 'Paseo Andaria'},
        {'nombre': 'Pradera Vistares'}
    ]

    # Lista para almacenar la información de las películas
    peliculas_info = []

    for cine in cines:
        # Seleccionar el cine
        teatros = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, 'TEATROS'))).click()
        cine_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, cine['nombre']))).click()

        # Esperar a que se carguen las películas
        peliculas = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="horarios"]/div')))

        for pelicula in peliculas:
            nombre = pelicula.find_element(By.TAG_NAME, 'h1').text.strip()
            idioma_original = pelicula.find_element(By.TAG_NAME, 'i').text.strip()
            idioma= map_idioma(idioma_original)
            horas = pelicula.find_elements(By.CLASS_NAME, 'myButton21')
            if not horas:
                horas = 'Sin horarios disponibles'

            for hora in horas:
                peliculas_info.append({
                    'Fecha': datetime.now().strftime("%m-%d-%y"),
                    'País': 'Guatemala',
                    'Cine': 'CineStar',
                    'Nombre Cine': cine['nombre'],
                    'Título': nombre,
                    'Hora': hora.text.strip(),
                    'Idioma': idioma,
                    'Formato': '2D',
                })

        # Volver a la página principal de teatros
        teatros = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, 'TEATROS')))
        teatros.click()

    # Crear un DataFrame de Pandas con la información
    df = pd.DataFrame(peliculas_info)

    # Exportar el DataFrame a una hoja de Excel
    df.to_excel('Guatemala-CaribbeanCinema.xlsx', index=False)

    print("Datos exportados exitosamente a Guatemala-CaribbeanCinema.xlsx")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()