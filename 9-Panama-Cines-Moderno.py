from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd

# Inicializacion del navegador y maximizacion de pantalla
driver = webdriver.Chrome()
driver.maximize_window()

# Navegar a la pagina de los cines modernos en Panama
driver.get('https://www.cinesmodernopanama.com/')

try:
    # Lista de cines con sus nombres y IDs correspondientes
    cines = [
        {'nombre': 'David', 'id': 'Semana_551'},
        {'nombre': 'Chitré', 'id': 'Semana_552'},
        {'nombre': 'Santiago', 'id': 'Semana_553'},
        {'nombre': 'Coronado', 'id': 'Semana_555'},
    ]

    # Lista para almacenar la informacion de las peliculas
    peliculas_info = []

    for cine in cines:
        # Espera y hacer clic en el menu para desplegar opciones
        menu = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'cd-menu-trigger')))
        menu.click()

        # Espera y hacer clic en la opcion de cartelera
        cartelera = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cd-lateral-nav"]/ul[1]/li/a')))
        cartelera.click()

        # Espera y seleccionar el cine especifico usando su ID
        cine_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, cine['id'])))
        cine_link.click()

        # Espera a que se carguen las peliculas del cine seleccionado
        peliculas = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="cartelera"]/div/div[5]/div')))

        for pelicula in peliculas:
            try:
                # Extrae y limpia el nombre de la pelicula
                nombre = pelicula.find_element(By.CSS_SELECTOR, '.combopelititulo h2').text.strip()
                nombre = nombre.replace("2D", "").replace("3D", "").replace("VIP", "").replace("DOB", "").replace("SVIP", "").strip()

                # Extrae el idioma de la pelicula, si esta disponible
                try:
                    idioma_element = pelicula.find_element(By.XPATH, './/div[contains(@class, "icosdetalle") and img[contains(@src, "icos-38.jpg")]]/p')
                    idioma = idioma_element.text.strip()
                except:
                    idioma = "Desconocido"

                # Normaliza el idioma a los valores "SUB" o "DOB" y convierte a mayusculas
                if "Inglés" in idioma:
                    idioma = "SUB"
                elif "Español" in idioma:
                    idioma = "DOB"

                # Extrae el formato de la pelicula, si esta disponible
                try:
                    formato_element = pelicula.find_element(By.XPATH, './/div[contains(@class, "icosdetalle") and img[contains(@src, "icos-42.png")]]/p')
                    formato = formato_element.text.strip()
                except:
                    formato = "Desconocido"

                # Normaliza el formato a "2D" o "3D"
                if "2D" in formato:
                    formato = "2D"
                elif "3D" in formato:
                    formato = "3D"
                else:
                    formato = "Desconocido"

                # Extrae los horarios de la pelicula
                horarios = pelicula.find_elements(By.CLASS_NAME, 'func-horario')

                # Guarda la informacion de cada horario en la lista de peliculas
                for horario in horarios:
                    horario = horario.text.split("(")[0].strip()  # Limpia el horario
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

    # Crea un DataFrame de Pandas con la informacion obtenida
    df = pd.DataFrame(peliculas_info)

    # Exportar el DataFrame a una hoja de Excel
    df.to_excel('Panama-CinesModerno.xlsx', index=False)

    print("Datos exportados exitosamente a Panama-CinesModernos.xlsx")

except Exception as e:
    print(f"{e} No se encontraron peliculas")

finally:
    # Cerrar el navegador
    driver.quit()
