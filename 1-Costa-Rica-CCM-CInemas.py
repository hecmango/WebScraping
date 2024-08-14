import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import openpyxl
from datetime import date

# Configuración del driver de Chrome
driver = webdriver.Chrome()
driver.maximize_window()

# Lista de selectores para las películas y nombres de cine correspondientes
selectores = [
    ("a:nth-child(2) > img", "SAN RAMON PLAZA OCCIDENTE"),
    ("a:nth-child(4) > img", "SAN CARLOS PLAZA SAN CARLOS"),
    ("a:nth-child(6) > img", "ROHRMOSER PLAZA MAYOR"),
    ("a:nth-child(8) > img", "JACÓ PLAZA CORAL")
]

# Crear un libro de Excel
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.append(["Fecha", "Pais", "Cine", "Nombre Cine", "Título", "Formato", "Idioma", "Horario"])

def get_schedule_elements(driver, wait, href_index, nombre_cine):
    try:
        # Intentar obtener el nombre de la película
        contenedor_nombre_peli = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'spanLabelResumenTandas'))
        )
        nombre_pelicula = contenedor_nombre_peli.text.strip()
        print(f"Nombre de la película {href_index + 1}:", nombre_pelicula)

        # Obtener todos los contenedores de formatos y horarios
        lista_tandas_contenedores = driver.find_elements(By.CLASS_NAME, 'ListaTandasH3Calendario')

        if not lista_tandas_contenedores:
            print(f"No se encontraron contenedores de formatos para la película {href_index + 1}.")
            return False

        # Crear un diccionario para almacenar horarios por formato
        horarios_por_formato = {}
        formatos = []

        for lista_tanda in lista_tandas_contenedores:
            try:
                span_listatandas = lista_tanda.find_element(By.CLASS_NAME, 'ListatandasCalendario')
                contenido = span_listatandas.text
                formato, idioma = [x.strip() for x in contenido.split(',')]
                horarios_por_formato[formato] = {"idioma": idioma, "horarios": []}  # Inicializar la lista de horarios para cada formato
                formatos.append(lista_tanda)  # Guardar la referencia del contenedor
            except NoSuchElementException:
                continue

        # Obtener todos los contenedores de horarios
        tandas_contenedores = driver.find_elements(By.CLASS_NAME, 'TandasHoraContainer')
        for contenedor in tandas_contenedores:
            try:
                # Determinar el formato para el contenedor actual
                formato_actual = None
                for i, lista_tanda in enumerate(formatos):
                    if contenedor.location['y'] > lista_tanda.location['y']:
                        span_listatandas = lista_tanda.find_element(By.CLASS_NAME, 'ListatandasCalendario')
                        contenido = span_listatandas.text
                        formato_actual, _ = [x.strip() for x in contenido.split(',')]
                    else:
                        break

                if formato_actual:
                    # Obtener todos los horarios en el contenedor actual
                    tandas_calendarios = contenedor.find_elements(By.CLASS_NAME, 'TandasHoraCalendario')
                    for calendario in tandas_calendarios:
                        hora_texto = calendario.text.strip()
                        horarios_por_formato[formato_actual]["horarios"].append(hora_texto)
            except NoSuchElementException:
                continue

        # Imprimir los horarios agrupados por formato y guardar en el Excel
        datos_extraidos = False
        for formato, datos in horarios_por_formato.items():
            if datos["horarios"]:  # Verifica si hay horarios para el formato
                for hora in datos["horarios"]:
                    # Obtener la fecha actual
                    fecha_actual = date.today().strftime("%Y-%m-%d")

                    # Obtener el nombre de la sala
                    try:
                        sala_element = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#body-wrap #wrap header div.cactus-nav  #main-nav nav.navbar.navbar-default div.container div.navbar-header a.navbar-brand div.primary-logo img"))
                        )
                        nombre_sala = sala_element.get_attribute("title")
                    except TimeoutException:
                        nombre_sala = "No se pudo encontrar la sala."

                    # Agregar los datos al Excel
                    print(f"Guardando datos para: {nombre_pelicula}, Formato: {formato}, Idioma: {datos['idioma']}, Hora: {hora}")
                    sheet.append([fecha_actual, "Costa Rica", "CCMCinemas", nombre_cine, nombre_pelicula, formato, datos["idioma"], hora])
                    datos_extraidos = True

        return datos_extraidos

    except TimeoutException:
        return False

try:
    for selector, nombre_cine in selectores:
        driver.get("https://www.ccmcinemas.com")
        driver.implicitly_wait(5)
        wait = WebDriverWait(driver, 5)

        # Hacer clic en el selector actual para ir a la página de películas
        target_element = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        driver.execute_script("arguments[0].click();", target_element)

        # Esperar un momento para que la página cargue
        driver.implicitly_wait(5)

        # Verificar si el anuncio está presente y cerrarlo si es necesario
        try:
            anuncio = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="spu-2294"]')))
            if anuncio:
                close_button = driver.find_element(By.XPATH, '/html/body/div[4]/span[1]/i')
                driver.execute_script("arguments[0].click();", close_button)
                driver.implicitly_wait(7)
        except TimeoutException:
            print("No se encontró ningún anuncio para cerrar.")

        # Detectar dinámicamente el número de películas
        peliculas = driver.find_elements(By.CSS_SELECTOR, ".col-md-4 .pt-cv-content > ._self")
        num_peliculas = len(peliculas)
        print(f"Cantidad de películas encontradas: {num_peliculas}")

        # IDs posibles para los artículos
        possible_ids = ['post-1511', 'post-1513', 'post-1556']

        # Iterar por todas las películas
        for href_index in range(num_peliculas):
            attempt = 0
            max_attempts = 3
            while attempt < max_attempts:
                try:
                    # Intentar hacer clic en el elemento de la película
                    peliculas = driver.find_elements(By.CSS_SELECTOR, ".col-md-4 .pt-cv-content > ._self")
                    driver.execute_script("arguments[0].click();", peliculas[href_index])

                    # Esperar indefinidamente hasta que el body esté presente
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

                    # Seguir la jerarquía para encontrar el nombre de la película
                    contenedor_principal = wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'single-page-content'))
                    )

                    articulo_encontrado = False
                    for articulo_id in possible_ids:
                        try:
                            # Buscar el artículo con el ID actual
                            articulo = contenedor_principal.find_element(By.XPATH, f".//article[@id='{articulo_id}']")
                            articulo_encontrado = True
                            break
                        except NoSuchElementException:
                            continue

                    if not articulo_encontrado:
                        print(f"No se encontró ningún artículo con los IDs posibles para la película {href_index + 1}.")
                        driver.back()
                        break

                    contenedor_body_content = articulo.find_element(By.CLASS_NAME, 'body-content')
                    contenedor_vc_row = contenedor_body_content.find_element(By.CSS_SELECTOR, '.vc_row.wpb_row.vc_row-fluid')
                    contenedor_vc_column = contenedor_vc_row.find_element(By.CSS_SELECTOR, '.wpb_column.vc_column_container.vc_col-sm-12')
                    contenedor_vc_column_inner = contenedor_vc_column.find_element(By.CLASS_NAME, 'vc_column-inner')
                    contenedor_wpb_wrapper = contenedor_vc_column_inner.find_element(By.CLASS_NAME, 'wpb_wrapper')
                    contenedor_wpb_raw_code = contenedor_wpb_wrapper.find_element(By.CSS_SELECTOR, '.wpb_raw_code.wpb_content_element.wpb_raw_html')
                    contenedor_wpb_raw_code_wrapper = contenedor_wpb_raw_code.find_element(By.CLASS_NAME, 'wpb_wrapper')
                    contenedor_embed_container = contenedor_wpb_raw_code_wrapper.find_element(By.CLASS_NAME, 'embed-container')
                    iframe = contenedor_embed_container.find_element(By.ID, 'CCMTANDAS')

                    # Cambiar al contexto del iframe
                    driver.switch_to.frame(iframe)
                    html_element = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//html[@xmlns='http://www.w3.org/1999/xhtml']"))
                    )
                    formulario = html_element.find_element(By.ID, 'form1')
                    div_acordion = wait.until(
                        EC.presence_of_element_located((By.ID, 'ContentPlaceHolder1_accordion'))
                    )
                      # Verificar la fecha en el elemento con el ID "ContentPlaceHolder1_DropDown_Dias_Esquema"
                    elemento_fecha = wait.until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_DropDown_Dias_Esquema"]'))
                    )
                    fecha_texto = elemento_fecha.text.strip().split('\n')[0]  # Obtener solo el texto de la fecha

                    if not fecha_texto.startswith("HOY"):
                        print(f"La fecha '{fecha_texto}' no es 'HOY'. Se omite la película.")
                        driver.back()
                        break
                    # Intentar obtener los elementos del horario
                    if not get_schedule_elements(driver, wait, href_index, nombre_cine):
                        print(f"Intento {attempt + 1}: Fallo al obtener elementos del horario para la película {href_index + 1}.")
                        driver.switch_to.default_content()
                        driver.back()
                        attempt += 1
                        continue

                    # Volver atrás para seguir con la siguiente película
                    driver.switch_to.default_content()
                    driver.back()
                    break

                except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
                    print(f"Intento {attempt + 1}: Hubo un problema al procesar la película {href_index + 1}. Reintentando... {e}")
                    driver.switch_to.default_content()
                    driver.back()
                    attempt += 1

finally:
    # Guardar el archivo Excel
    workbook.save("horarios_peliculas.xlsx")
    print("Archivo de Excel guardado exitosamente.")

    # Cerrar el navegador
    driver.quit()
