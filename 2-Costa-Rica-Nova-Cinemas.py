from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import locale
import openpyxl

# Configurar el locale para que coincida con el formato de fecha en el sitio web
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Función para obtener la fecha actual en el formato requerido
def get_current_date_str():
    return datetime.now().strftime("%A %d %B %Y").lower()

# Función para crear y guardar el archivo Excel
def save_to_excel(data, filename):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Fecha", "Pais", "Cine", "Nombre Cine", "Titulo", "Formato", "Idioma", "Horario"])
    
    for row in data:
        sheet.append(row)
    
    workbook.save(filename)

# Configurar el controlador de Selenium
driver = webdriver.Chrome()  # Asegúrate de tener el driver de Chrome descargado y configurado
driver.maximize_window()

# Abrir la URL
driver.get("https://www.novacinemas.cr/cartelera/")

# Esperar a que el primer menú desplegable sea interactivo
wait = WebDriverWait(driver, 20)
first_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="select"]')))

# Crear una lista con los XPaths de las opciones del primer menú desplegable
first_dropdown_options = [
    '//*[@id="ui-id-1"]',
    '//*[@id="ui-id-2"]',
    '//*[@id="ui-id-3"]'
]

# XPath del segundo menú desplegable
second_dropdown_xpath = '//*[@id="cartelera"]/div[2]/nav/a'
second_menu_xpath = '//*[@id="menu-cines"]'

# Crear una lista con los XPaths del contenedor con display:block para cada cine
date_containers_xpaths = [
    '/html/body/main/div/div[1]/div[5]/ul/div[1]',  # Primer cine
    '/html/body/main/div/div[1]/div[7]/ul/div[1]',  # Segundo cine
    '/html/body/main/div/div[1]/div[9]/ul/div[1]'   # Tercer cine
]

# Obtener la fecha actual en el formato requerido
current_date_str = get_current_date_str()

# Lista para almacenar los datos
data = []

# Iterar sobre las opciones del primer menú desplegable
for index, option_xpath in enumerate(first_dropdown_options):
    # Hacer clic en el primer menú desplegable
    first_dropdown.click()
    time.sleep(2)  # Aumenta el tiempo de espera para asegurarte de que se cargue completamente
    
    # Seleccionar la opción actual
    option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
    option_name = option.text  # Obtener el nombre de la opción seleccionada
    print(f"Seleccionando cine: {option_name}")
    option.click()
    time.sleep(2)  # Aumenta el tiempo de espera para asegurarte de que se cargue completamente
    
    # Hacer clic en el segundo menú desplegable
    second_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, second_dropdown_xpath)))
    second_dropdown.click()
    time.sleep(2)  # Aumenta el tiempo de espera para asegurarte de que se cargue completamente
    
    # Encontrar y seleccionar la opción correspondiente a la fecha actual
    menu_items = driver.find_elements(By.XPATH, f'{second_menu_xpath}/li/a')
    date_found = False
    for item in menu_items:
        date_attribute = item.get_attribute('data-date')
        if date_attribute and current_date_str in date_attribute.lower():
            item.click()
            date_found = True
            break
    
    if not date_found:
        print(f"No se encontró la fecha actual en el segundo menú para el cine {option_name}. Saltando...")
        continue

    time.sleep(2)  # Aumenta el tiempo de espera para asegurarte de que se cargue completamente

    # Verificar el contenedor con display:block para el cine actual
    date_container_xpath = date_containers_xpaths[index]
    date_containers = driver.find_elements(By.XPATH, f'{date_container_xpath}[contains(@style, "display: block;")]')
    if not date_containers:
        print(f"No se encontraron contenedores con 'display: block;' para el cine {option_name}.")
        continue

    for container in date_containers:
        # Encontrar todos los elementos con la clase titleAccordion dentro del contenedor
        movie_titles = container.find_elements(By.CLASS_NAME, 'titleAccordion')
        
        for title in movie_titles:
            movie_name = title.text  # Extraer el nombre de la película
            print(f"Película: {movie_name}")
            
            # Encontrar el contenedor rowTimes relacionado con el título de la película
            row_times_container = title.find_element(By.XPATH, 'following-sibling::div[contains(@class, "rowTimes") and contains(@style, "display: block;")]')
            if row_times_container:
                items = row_times_container.find_elements(By.CLASS_NAME, 'item')
                for item in items:
                    time_element = item.find_element(By.TAG_NAME, 'a')
                    format_element = item.find_element(By.TAG_NAME, 'span')
                    horario = time_element.text
                    formato, idioma = format_element.text.split()[:2]
                    
                    # Agregar los datos a la lista
                    data.append([
                        datetime.now().strftime("%d/%m/%Y"),  # Fecha actual
                        "Costa Rica",
                        "Novacinemas",
                        option_name,
                        movie_name,
                        formato,
                        idioma,
                        horario
                    ])
                    print(f"Horario: {horario}, Formato: {formato}, Idioma: {idioma}")

    # Volver al primer menú desplegable para seleccionar el siguiente cine
    first_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="select"]')))
    time.sleep(2)

# Cerrar el navegador
driver.quit()

# Guardar los datos en un archivo Excel
save_to_excel(data, "novacinemas_cartelera.xlsx")
