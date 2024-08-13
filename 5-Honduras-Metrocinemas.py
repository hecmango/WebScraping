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
url = 'https://www.metrocinemas.hn/'
driver.get(url)

try:

        cines = [
              {'nombre': 'America', 'id': 'Semana_501'},
              {'nombre': 'Metromall', 'id': 'Semana_502'},
              {'nombre': 'Miraflores', 'id': 'Semana_504'},
              {'nombre': 'MegaMall', 'id': 'Semana_509'},
              {'nombre': 'Novacentro', 'id': 'Semana_510'},
              {'nombre': 'Choloma', 'id': 'Semana_511'},
              {'nombre': 'Cortes', 'id': 'Semana_512'},
              {'nombre': 'Santa Rosa', 'id': 'Semana_513'},
        ]

        peliculas_info =[]

        for cine in cines:
            menu = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'cd-menu-trigger'))).click()

            cartelera = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cd-lateral-nav"]/ul[1]/li/a'))).click()
            # Seleccionar el cine
            cine_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, cine['id'])))
            cine_link.click()

            # Esperar a que se carguen las peliculas
            peliculas = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="cartelera"]/div/div[5]/div')))

            for pelicula in peliculas:
                try:
                    nombre = pelicula.find_element(By.CSS_SELECTOR, '.combopelititulo h2').text.strip()
                    nombre = nombre.replace("2D", "").replace("3D", "").replace("VIP", "").replace("DOB", "").replace("SVIP", "").strip()
                    idioma = pelicula.find_element(By.XPATH, './/div[contains(@class, "icosdetalle") and img[@src="./App_Themes/1002/img/icos-38.jpg"]]/p').text.strip()
                    formato = pelicula.find_element(By.XPATH, './/div[contains(@class, "icosdetalle") and img[@src="./App_Themes/1002/img/icos-42.png"]]/p').text.strip()
                    formato = formato.replace("|","").strip()
                    horarios = pelicula.find_elements(By.CLASS_NAME, 'func-horario')

                    for horario in horarios:
                        horario = horario.text.split("(")[0].strip()
                        peliculas_info.append({
                            'Fecha': datetime.now().strftime("%d/%m/%y"),
                            'País': 'Honduras',
                            'Cine': 'MetroCinemas',
                            'Nombre Cine': cine['nombre'],
                            'Título': nombre,
                            'Hora': horario,
                            'Idioma': idioma,
                            'Formato': formato,
                        })
                except Exception as e:
                    print(f"Error al procesar la película: {e}")

        #Crear un DataFrame de Pandas con la información
        df = pd.DataFrame(peliculas_info)

        # Exportar el DataFrame a una hoja de Excel
        df.to_excel('Honduras-Metrocinemas.xlsx', index=False)

        print("Datos exportados exitosamente a Honduras-Metrocinemas.xlsx")

except Exception as e:
     print(f"Error: {e}")

finally:
    driver.quit()