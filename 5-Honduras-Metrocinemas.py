from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd

# Inicia el navegador Chrome y maximiza la ventana
driver = webdriver.Chrome()
driver.maximize_window()

# Navega a la página principal de MetroCinemas
driver.get('https://www.metrocinemas.hn/')

try:
    # Abre el menú y selecciona la cartelera
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'cd-menu-trigger'))).click()
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cd-lateral-nav"]/ul[1]/li/a'))).click()

    # Obtén todos los elementos de cine disponibles
    cines_elements = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="cines"]/div/a')))

    # Crea un diccionario dinámico con los nombres de los cines y sus respectivos IDs
    cines_dict = {cine.text: cine.get_attribute('id') for cine in cines_elements}

    peliculas_info = []  # Lista para almacenar la información de las películas

    # Iterar sobre cada cine en la lista
    for nombre_cine, id_cine in cines_dict.items():
        try:
            # Seleccionar el cine específico basado en su ID
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, id_cine))).click()

            # Esperar a que se carguen las películas en la cartelera del cine seleccionado
            peliculas = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="cartelera"]/div/div[5]/div')))

            # Iterar sobre cada película listada para extraer su información
            for pelicula in peliculas:
                try:
                    # Extraer el nombre de la película, eliminando cualquier etiqueta de formato o idioma
                    nombre = pelicula.find_element(By.CSS_SELECTOR, '.combopelititulo h2').text.strip()
                    nombre = nombre.replace("2D", "").replace("3D", "").replace("VIP", "").replace("DOB", "").replace("SVIP", "").strip()
                    
                    # Extraer el idioma de la película
                    idioma = pelicula.find_element(By.XPATH, './/div[contains(@class, "icosdetalle") and img[@src="./App_Themes/1002/img/icos-38.jpg"]]/p').text.strip()
                    if "Ingles" in idioma:
                        idioma = "SUB"
                    elif "Español" in idioma:
                        idioma = "DOB"
                    
                    # Extraer el formato de la película basado en un ícono específico
                    formato = pelicula.find_element(By.XPATH, './/div[contains(@class, "icosdetalle") and img[@src="./App_Themes/1002/img/icos-42.png"]]/p').text.strip()
                    if "2D" in formato:
                        formato = "2D"
                    elif "3D" in formato:
                        formato = "3D"
                    else:
                        formato = "Desconocido"

                    # Extraer los horarios de la película
                    horarios = pelicula.find_elements(By.CLASS_NAME, 'func-horario')

                    # Iterar sobre cada horario y guardar la información en la lista
                    for horario in horarios:
                        hora = horario.text.split("(")[0].strip()  # Limpiar el horario, eliminando paréntesis y espacios
                        peliculas_info.append({
                            'Fecha': datetime.now().strftime("%d/%m/%y"),  # Fecha actual
                            'País': 'Honduras',
                            'Cine': 'MetroCinemas',
                            'Nombre Cine': nombre_cine,
                            'Título': nombre,
                            'Hora': hora,
                            'Idioma': idioma,
                            'Formato': formato,
                        })
                except Exception as e:
                    # Capturar y mostrar errores específicos para la película actual
                    print(f"Error al procesar la película en el cine {nombre_cine}: {e}")
        
        except Exception as e:
            # Continuar con el siguiente cine en caso de error al intentar cargar las películas
            print(f"Error al procesar el cine {nombre_cine}: {e}")
            continue

    # Si se ha recopilado información, crear un DataFrame y exportarlo a un archivo Excel
    if peliculas_info:
        df = pd.DataFrame(peliculas_info)
        df.to_excel('Honduras-Metrocinemas.xlsx', index=False)  # Exportar los datos a un archivo Excel
        print("Datos exportados exitosamente a Honduras-Metrocinemas.xlsx")
    else:
        print("No se encontraron datos para ningún cine.")  # Mensaje si no se encontró ninguna película

except Exception as e:
    # Capturar y mostrar cualquier error general que ocurra durante la ejecución
    print(f"Error: {e}")

finally:
    driver.quit()
