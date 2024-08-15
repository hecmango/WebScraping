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
url = 'https://www.cinesmodernopanama.com/'
driver.get(url)

try:
    cines = [
        {'nombre': 'David', 'id': 'Semana_551'},
        {'nombre': 'Chitré', 'id': 'Semana_552'},
        {'nombre': 'Santiago', 'id': 'Semana_553'},
        {'nombre': 'Coronado', 'id': 'Semana_555'},
    ]

    peliculas_info = []

    for cine in cines:
        # Abrir el menú y seleccionar cartelera
        menu = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'cd-menu-trigger')))
        menu.click()

        cartelera = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cd-lateral-nav"]/ul[1]/li/a')))
        cartelera.click()

        # Seleccionar el cine
        cine_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, cine['id'])))
        cine_link.click()

        # Esperar a que se carguen las películas
        peliculas = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="cartelera"]/div/div[5]/div')))

        for pelicula in peliculas:
            try:
                # Extraer el nombre, idioma, formato y horarios
                nombre = pelicula.find_element(By.CSS_SELECTOR, '.combopelititulo h2').text.strip()
                nombre = nombre.replace("2D", "").replace("3D", "").replace("VIP", "").replace("DOB", "").replace("SVIP", "").strip()

                # Intentar encontrar el idioma
                try:
                    idioma_element = pelicula.find_element(By.XPATH, './/div[contains(@class, "icosdetalle") and img[contains(@src, "icos-38.jpg")]]/p')
                    idioma = idioma_element.text.strip()
                except:
                    idioma = "Desconocido"

                if "Inglés" in idioma:
                    idioma = "Sub"
                elif "Español" in idioma:
                    idioma = "Dob"

                # Intentar encontrar el formato
                try:
                    formato_element = pelicula.find_element(By.XPATH, './/div[contains(@class, "icosdetalle") and img[contains(@src, "icos-42.png")]]/p')
                    formato = formato_element.text.strip()
                except:
                    formato = "Desconocido"

                if "2D" in formato:
                    formato = "2D"
                elif "3D" in formato:
                    formato = "3D"
                else:
                    formato = "Desconocido"  # En caso de que no se encuentre ni 2D ni 3D

                horarios = pelicula.find_elements(By.CLASS_NAME, 'func-horario')

                # Guardar la información de cada horario
                for horario in horarios:
                    horario = horario.text.split("(")[0].strip()
                    peliculas_info.append({
                        'Fecha': datetime.now().strftime("%d/%m/%y"),
                        'País': 'Panamá',
                        'Cine': 'Cines Modernos',
                        'Nombre Cine': cine['nombre'],
                        'Título': nombre,
                        'Hora': horario,
                        'Idioma': idioma,
                        'Formato': formato,
                    })
            except Exception as e:
                print(f"Error al procesar la película: {e}")

    # Crear un DataFrame de Pandas con la información
    df = pd.DataFrame(peliculas_info)

    # Exportar el DataFrame a una hoja de Excel
    df.to_excel('Panama-CinesModerno.xlsx', index=False)

    print("Datos exportados exitosamente a Panama-CinesModernos.xlsx")

except Exception as e:
    print(f"{e} No se encontraron peliculas")

finally:
    driver.quit()
