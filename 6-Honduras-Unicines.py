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
url = 'https://unicines.com/cartelera.php'
driver.get(url)

try: 
    cines = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="cat_nav"]/li/a')))
    nombres_cines = [cine.text for cine in cines]
    enlaces = [cine.get_attribute('href') for cine in cines]

    cines_info = [{'nombre': nombre, 'direccion': enlace} for nombre, enlace in zip(nombres_cines, enlaces)]

    peliculas_info = []

    for cine in cines_info:
        driver.get(cine['direccion'])

        for i in range(1, len(cines_info)+1):
            try:
                xpath = f'//*[@id="collapse_{i}"]/div/div'
                peliculas = WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
                if peliculas:
                    break
            except Exception as e:
                continue

        for pelicula in peliculas:
            try:
                # Extraer el nombre de la película
                nombre_pelicula = pelicula.find_element(By.TAG_NAME, 'h3').text.strip()

                detalles = pelicula.find_elements(By.CSS_SELECTOR, 'div.tour_list_desc > div > span')
                
                for detalle in detalles:
                    contenido_html = detalle.get_attribute('innerHTML')
                    partes = contenido_html.split('<br>')

                    for parte in partes:
                        try:
                            formato_e_idioma = parte.split('</span>')[1].replace('<strong>', '').split('</strong>')[0].strip()

                            if '2D' in formato_e_idioma:  
                                formato = '2D'
                            else:
                                formato = '3D'

                            idioma = formato_e_idioma.split(' ')[2]

                            # Extraer horario
                            horario = parte.split('</strong>')[1].strip().split('-')[1].strip()

                            peliculas_info.append({
                                'Fecha': datetime.now().strftime("%m-%d-%Y"),
                                'País': 'Honduras',
                                'Cine': 'Unicines',
                                'Nombre Cine': cine['nombre'],
                                'Título': nombre_pelicula,
                                'Hora': horario,
                                'Idioma': idioma.upper(),
                                'Formato': formato,  
                            })
                        except Exception as e:
                            print(f"Error al procesar la parte: {parte}, Error: {e}")

            except Exception as e:
                print(f"No se econtraron peliculas para el cine: {cine['nombre']}, Error: {e}")
                continue

    # Crear un DataFrame de Pandas con la información
    df = pd.DataFrame(peliculas_info)

    # Exportar el DataFrame a una hoja de Excel
    df.to_excel('Honduras-Unicines.xlsx', index=False)

    print("Datos exportados exitosamente a Honduras-Unicines.xlsx")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()
