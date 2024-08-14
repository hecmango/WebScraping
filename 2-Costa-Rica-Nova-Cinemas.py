from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
import time
from datetime import datetime
import unicodedata
import openpyxl

# Diccionario de días de la semana para comparación
DAYS_MAP = {
    'monday': 'lunes',
    'tuesday': 'martes',
    'wednesday': 'miércoles',
    'thursday': 'jueves',
    'friday': 'viernes',
    'saturday': 'sábado',
    'sunday': 'domingo'
}

# Diccionario de meses para comparación
MONTHS_MAP = {
    'january': 'enero',
    'february': 'febrero',
    'march': 'marzo',
    'april': 'abril',
    'may': 'mayo',
    'june': 'junio',
    'july': 'julio',
    'august': 'agosto',
    'september': 'septiembre',
    'october': 'octubre',
    'november': 'noviembre',
    'december': 'diciembre'
}

# Función para normalizar texto eliminando acentos y otros caracteres especiales
def normalize_string(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()

# Función para obtener la fecha actual en el formato requerido
def get_current_date_str():
    today = datetime.now()
    day_name = today.strftime('%A').lower()  # Nombre del día en minúsculas
    day_name = DAYS_MAP.get(day_name, day_name)  # Normalizar el nombre del día

    month_name = today.strftime('%B').lower()  # Nombre del mes en minúsculas
    month_name = MONTHS_MAP.get(month_name, month_name)  # Normalizar el nombre del mes

    formatted_date = today.strftime(f"{day_name} %d {month_name} %Y")
    return normalize_string(formatted_date)

# Función para crear y guardar el archivo Excel
def save_to_excel(data, filename):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Fecha", "Pais", "Cine", "Nombre Cine", "Titulo", "Formato", "Idioma", "Horario"])

    for row in data:
        sheet.append(row)

    workbook.save(filename)

# Configurar el controlador de Selenium
driver = webdriver.Chrome()
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

# Obtener la fecha actual en el formato requerido
current_date_str = get_current_date_str()
print(f"Fecha actual para comparación: {current_date_str}")

# Lista para almacenar los datos
data = []

# Iterar sobre las opciones del primer menú desplegable
for option_xpath in first_dropdown_options:
    # Hacer clic en el primer menú desplegable
    try:
        first_dropdown.click()
    except ElementClickInterceptedException:
        print("Un elemento está bloqueando el menú desplegable. Intentando continuar...")
        time.sleep(2)

    time.sleep(2)

    # Seleccionar la opción actual
    option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
    option_name = option.text
    print(f"Seleccionando cine: {option_name}")
    option.click()
    time.sleep(2)

    # Hacer clic en el segundo menú desplegable
    second_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, second_dropdown_xpath)))
    second_dropdown.click()
    time.sleep(5)

    # Encontrar y seleccionar la opción correspondiente a la fecha actual
    menu_items = driver.find_elements(By.XPATH, f'{second_menu_xpath}/li/a')
    if not menu_items:
        print("No se encontraron elementos de menú.")

    date_found = False
    for item in menu_items:
        date_attribute = item.get_attribute('data-date')
        if date_attribute:
            date_attribute = normalize_string(date_attribute)
            print(f"Fecha en el elemento: {date_attribute}")
            if current_date_str in date_attribute:
                item.click()
                date_found = True
                print(f"Seleccionado: {date_attribute}")
                break
        else:
            print("Atributo 'data-date' es None para uno de los elementos.")

    if not date_found:
        print(f"No se encontró la fecha actual en el segundo menú para el cine {option_name}. Saltando...")
        # Cerrar el segundo menú desplegable si no se encontró la fecha
        second_dropdown.click() 
        time.sleep(2)
        continue

    time.sleep(2)

    # Buscar el contenedor de películas para la fecha actual
    movie_containers = driver.find_elements(By.CSS_SELECTOR, '.movieDates.cols')

    if not movie_containers:
        print(f"No se encontraron contenedores de películas para el cine {option_name}.")
        continue

    for movie_container in movie_containers:
        # Extraer información de la película dentro de cada contenedor
        movie_name_element = movie_container.find_element(By.CSS_SELECTOR, '.titleAccordion')
        movie_name = movie_name_element.text

        # Encontrar todos los horarios dentro del contenedor de la película
        showtime_containers = movie_container.find_elements(By.CSS_SELECTOR, '.showTimes .item')
        for showtime_container in showtime_containers:
            horario = showtime_container.find_element(By.TAG_NAME, 'a').text
            formato_idioma = showtime_container.find_element(By.TAG_NAME, 'span').text
            parts = formato_idioma.split()
            formato = parts[0] if parts else ""
            idioma = parts[1] if len(parts) > 1 else ""

            # Imprimir solo si se ha extraído información válida
            if movie_name and horario and formato and idioma:
                data.append([
                    datetime.now().strftime("%d/%m/%Y"),
                    "Costa Rica",
                    "Novacinemas",
                    option_name,
                    movie_name,
                    formato,
                    idioma,
                    horario
                ])
                print(f"Película: {movie_name}, Horario: {horario}, Formato: {formato}, Idioma: {idioma}")

    # Volver al primer menú desplegable para la siguiente iteración
    first_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="select"]')))

# Cerrar el navegador
driver.quit()

# Guardar los datos en un archivo Excel
save_to_excel(data, "novacinemas_cartelera.xlsx")