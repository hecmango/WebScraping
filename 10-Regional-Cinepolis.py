from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import pandas as pd
import unicodedata
import time

# Inicialización del navegador y maximización de pantalla
driver = webdriver.Chrome()
driver.maximize_window()

def transformar_ciudad(ciudad):
    resultado = ciudad.lower()
    resultado = ''.join(c for c in unicodedata.normalize('NFD', resultado) if unicodedata.category(c) != 'Mn')
    resultado = resultado.replace(',', '')
    resultado = resultado.replace(' ', '-')
    return resultado

def cerrar_publicidad():
    try:
        publicidad = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "tk")))
        if publicidad:
            cerrar_boton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'takeover-close')))
            cerrar_boton.click()
    except Exception:
        pass

def extraer_datos_cinepolis(urls):
    peliculas_info = []
    idiomas = ["DOB", "SUB", "ESP"]
    for url in urls:
        driver.get(url['url'])
        cerrar_publicidad()

        cartelera = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="header-principal"]/form/button')))
        cartelera.click()

        ciudades = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/div[1]/div/header/form/div[1]/select/option')))
        lista_ciudades = [f'{url["url"]}cartelera/{transformar_ciudad(ciudad.text)}' for ciudad in ciudades[1:]]

        for ciudad_url in lista_ciudades:
            driver.get(ciudad_url)
            cerrar_publicidad()
            try:
                cines = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="listBillboards"]/div')))
                for cine in cines:
                    cine_name = cine.find_element(By.TAG_NAME, 'h2').text
                    peliculas = cine.find_elements(By.CLASS_NAME, 'SingleScheduleMovie__SingleScheduleComponent-sc-1n3hti2-0')

                    for pelicula in peliculas:
                        nombre_pelicula_element = WebDriverWait(pelicula, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'nombre')))
                        nombre_pelicula = nombre_pelicula_element.find_element(By.TAG_NAME, 'h3').text

                        idiomas_formatos = pelicula.find_elements(By.CLASS_NAME, 'formato')
                        for idioma_formato in idiomas_formatos:
                            try:
                                formato_imagen_element = idioma_formato.find_element(By.CLASS_NAME, 'formato-imagen')
                                formato_nombre = formato_imagen_element.find_element(By.TAG_NAME, 'img').get_attribute('alt')
                                formato = '3D' if '3D' in formato_nombre else '2D'
                            except:
                                formato = '2D'

                            idioma = idioma_formato.find_element(By.CLASS_NAME, 'formato-nombre').text
                            idioma = next((i for i in idiomas if i in idioma), "N/A")

                            horas_div = idioma_formato.find_element(By.CLASS_NAME, 'horas')
                            horarios = [hora.text for hora in horas_div.find_elements(By.TAG_NAME, 'p')]
                            for horario in horarios:
                                peliculas_info.append({
                                    'Fecha': datetime.now().strftime("%m-%d-%Y"),
                                    'Pais': url['pais'],
                                    'Cine': 'Cinepolis',
                                    'Nombre Cine': cine_name,
                                    'Pelicula': nombre_pelicula,
                                    'Hora': horario,
                                    'Idioma': idioma,
                                    'Formato': formato,
                                })
            except Exception:
                print(f'Error: No hay datos en {ciudad_url}')
                continue
    return peliculas_info

def extraer_datos_panama():
    data = []
    url_panama = 'https://cinepolis.com.pa/'
    IDIOMAS = {"DOB", "SUB"}
    FORMATOS = {"2D", "3D", "DIG"}

    driver.get(url_panama)

    try:
        # Verificar si aparece el modal de video y cerrarlo si es el caso
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'tk-video')))
        
        try:
            # Buscar el botón de cerrar el modal y hacer clic en él
            cerrar_boton = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'takeover-close')))
            cerrar_boton.click()
            print("Modal cerrado.")
        except Exception as e:
            print("No se encontró el botón de cerrar del modal o no se pudo hacer clic: ", e)

    except TimeoutException:
        print("No se mostró el modal de video.")
    cartelera_panama = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="busqueda"]/div[3]/input')))
    cartelera_panama.click()

    ciudades_panama = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="cmbCiudades"]/option')))
    lista_ciudades_panama = [f'{url_panama}cartelera/{transformar_ciudad(ciudad.text)}' for ciudad in ciudades_panama[1:]]

    for ciudad_url_panama in lista_ciudades_panama:
        try:
            driver.get(ciudad_url_panama)
            sucursales = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="carteleraCiudad"]/section[2]//div[contains(@class, "divComplejo")]')))

            for sucursal in sucursales:
                cine_nombre = sucursal.find_element(By.TAG_NAME, 'h2').text
                movies = sucursal.find_elements(By.CSS_SELECTOR, "article.tituloPelicula")
                
                for movie in movies:
                    title_element = movie.find_element(By.CSS_SELECTOR, "header h3 a")
                    title = title_element.text.strip()
                    
                    formats = movie.find_elements(By.CSS_SELECTOR, "div.horarioExp")
                    for format_section in formats:
                        format_text = format_section.find_element(By.CSS_SELECTOR, "div.col3.cf").text.strip().replace('\n', ' ')
                        showtimes = format_section.find_elements(By.CSS_SELECTOR, "time.btn.btnhorario a")
                        showtimes_text = [showtime.text.strip() for showtime in showtimes if showtime.text.strip()]

                        format_type = "2D"
                        language = "N/A"
                        for part in format_text.split():
                            if part in IDIOMAS:
                                language = part
                            elif part in FORMATOS:
                                format_type = part

                        for showtime in showtimes_text:
                            data.append({
                                'Fecha': datetime.now().strftime("%m-%d-%Y"),
                                'Pais': "Panama",
                                'Cine': "Cinepolis",
                                'Nombre Cine': cine_nombre,
                                'Pelicula': title,
                                'Hora': showtime,
                                'Idioma': language,
                                'Formato': format_type,
                            })
        except Exception:
            print(f'Error: No hay datos en {ciudad_url_panama}')
            continue
    return data

def extraer_datos_honduras():
    formatos = ["2D", "3D"]
    idiomas = ["SUBTITLE", "DUB", "SUB"]
    url_honduras = "https://cinepolis.com.hn/"
    driver.get(url_honduras)
    data_honduras = []

    try:
        close_button = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]')
        close_button.click()
    except NoSuchElementException:
        pass

    boton_cartelera = driver.find_element(By.XPATH, '//*[@id="sticky-header"]/div/div[2]/div[3]/a/span')
    boton_cartelera.click()

    cinemas = driver.find_elements(By.XPATH, '//*[@id="popup-cinemas"]/div/div/div[2]/div/div')

    lista_cines_honduras = []
    for cinema in cinemas:
        try:
            cinema_name = cinema.find_element(By.TAG_NAME, 'h4').text
            ciudad_url = f'{url_honduras}cartelera/{transformar_ciudad(cinema_name)}'
            lista_cines_honduras.append((ciudad_url, cinema_name))
        except NoSuchElementException:
            print(f"No se encontró el nombre del cine en uno de los elementos.")

    for cine_url, cine_nombre in lista_cines_honduras:
        driver.get(cine_url)
        time.sleep(2)  # Esperar a que la página cargue completamente

        peliculas = driver.find_elements(By.XPATH, '//*[@id="form-reservation"]/div[4]/div/div/div')

        for pelicula in peliculas:
            try:
                nombre_pelicula = pelicula.find_element(By.TAG_NAME, 'h2').text
                print(nombre_pelicula)
                horarios = pelicula.find_elements(By.XPATH, './/ul/li')
                for horario in horarios:
                    hora = horario.find_element(By.TAG_NAME, 'label').text.split()[0]
                    formato_lenguaje = horario.find_element(By.TAG_NAME, 'span').get_attribute('title')
                    partes = formato_lenguaje.split(', ')

                    # Obtener el formato y el idioma

                    # formato = partes[len(partes) - 2] if len(partes) > 2 else partes[len(partes) - 1]
                    # idioma = partes[len(partes) - 1] if len(partes) > 2 else partes[len(partes) - 2]

                    formato = next((f for f in formatos if f in formato_lenguaje), "N/A")
                    idioma = next((i for i in idiomas if i in formato_lenguaje), "N/A")

                    data_honduras.append({
                        "Fecha": datetime.now().strftime("%m-%d-%Y"),
                        "Pais": "Honduras",
                        "Cine": "Cinépolis",
                        "Nombre Cine": cine_nombre,
                        "Pelicula": nombre_pelicula,
                        "Hora": hora,
                        "Formato": formato,
                        "Idioma": idioma,
                    })

            except NoSuchElementException:
                print("No se pudo obtener la información de una película.")

    return data_honduras

try:
    urls = [
        {'url': 'https://cinepolis.com.gt/', 'pais': 'Guatemala'}, 
        {'url': 'https://cinepolis.com.sv/', 'pais': 'El Salvador'},
        {'url': 'https://cinepolis.co.cr/', 'pais': 'Costa Rica'},
    ]
    
    datos_cinepolis = extraer_datos_cinepolis(urls)
    datos_panama = extraer_datos_panama()
    datos_honduras = extraer_datos_honduras()

    df = pd.DataFrame( datos_cinepolis+ datos_panama + datos_honduras)
    df.to_excel(f"cartelera_{datetime.now().strftime('%Y-%m-%d')}.xlsx", index=False)
    print(f"Datos exportados exitosamente a cartelera_{datetime.now().strftime('%Y-%m-%d')}.xlsx")
finally:
    driver.quit()
