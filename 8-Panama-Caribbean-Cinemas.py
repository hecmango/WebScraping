from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd

# Inicialización del navegador y maximización de pantalla
driver = webdriver.Edge()
driver.maximize_window()

# Navegar a la página
url = 'https://caribbeancinemas.com/location/panama/'
driver.get(url)

try:

    # Lista de cines a procesar
    cines = [
        {'nombre': 'Santiago'},
        {'nombre': 'Penonomé'}
    ]

    # Lista para almacenar la información de las películas
    peliculas_info = []

    # Seleccionar el cine
    teatros = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, 'TEATROS')))
    teatros.click()
    cine_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Santiago')))
    cine_link.click()

    for cine in cines:
        
        # Esperar a que se carguen las películas
        peliculas = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="horarios"]/div')))

        for pelicula in peliculas:
            nombre = pelicula.find_element(By.TAG_NAME, 'h1').text.strip()
            idioma = pelicula.find_element(By.TAG_NAME, 'i').text.strip()
            horas = pelicula.find_elements(By.CLASS_NAME, 'myButton21') + pelicula.find_elements(By.CLASS_NAME, 'myButton2')

            for hora in horas:
                peliculas_info.append({
                    'Fecha': datetime.now().strftime("%d/%m/%y"),
                    'País': 'Panama',
                    'Cine': 'CaribeanCinema',
                    'Nombre Cine': cine['nombre'],
                    'Título': nombre,
                    'Hora': hora.text.strip(),
                    'Idioma': idioma,
                    'Formato': '2D',
                })
        # Volver a la página principal de teatros
        teatros = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="menu-main-menu"]/a')))
        teatros.click()
       

    # Crear un DataFrame de Pandas con la información
    df = pd.DataFrame(peliculas_info)

    # Exportar el DataFrame a una hoja de Excel
    df.to_excel('Panama-Caribbeancinema.xlsx', index=False)

    print("Datos exportados exitosamente a Panama-Caribbeancinema.xlsx")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()
