from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime
import pandas as pd
import time

# Inicialización del navegador y maximización de pantalla
driver = webdriver.Chrome()
driver.maximize_window()

# Navegar a la página
url = 'https://psiglonuevo.com/'
driver.get(url)
posibles_formatos = ["2D", "3D"]
posibles_idiomas = ["Subtitulada", "Doblada", "DOB", "SUBT"]


try:
     # Lista para almacenar la información de las películas
    peliculas_info = []

        # Esperar a que se cargue la sección con el CLASS_NAME especificado
    peliculas = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'fusion-no-lightbox'))
    )
    cines = {
        'León': 'fusion-tab-león',
        'Chinandega': 'fusion-tab-chinandega'
    }

    for pelicula in peliculas:
        try:
            pelicula.click()
            # Esperar a que se cargue el elemento con el XPath especificado
            nombre = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="wrapper"]/section/div/div/div/div/div[1]'))
            ).text.strip()

            for cine_nombre, cine_id in cines.items():
                # Esperar a que el cine esté visible y seleccionable
                cine = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, cine_id))
                )
                cine.click()
                time.sleep(1)
                cartelera = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'tab-pane.fade.fusion-clearfix.active')))
                
                # Extraer formato e idioma
                formato_idioma = cartelera.find_element(By.XPATH, './/div[contains(@class, "tanda-item") or contains(@class, "tandach-item")]')

                formato = next((f for f in posibles_formatos if f in formato_idioma.text), "N/A")
                idioma = next((f for f in posibles_idiomas if f in formato_idioma.text), "N/A")

                # Cambiar "Subtitulada" por "SUB" y "Doblada" por "DOB"
                if idioma in ["Subtitulada"]:
                    idioma = "SUB"
                elif idioma in ["Doblada"]:
                    idioma = "DOB"
    
                horarios_container = cartelera.find_elements(By.XPATH, './/div[@align="center"]')
                if(horarios_container):
                    horarios = horarios_container[0].find_elements(By.XPATH, './/div[contains(@class, "tanda-item") or contains(@class, "tandach-item")]')

                    for horario in horarios:
                        try:
                            hora = horario.text
                            idioma_en_horario = next((f for f in posibles_idiomas if f in horario.text), "N/A")
                            if idioma_en_horario != "N/A":
                                if idioma_en_horario == 'SUBT':
                                    idioma='SUB'
                                else:
                                    idioma='DOB'
                                hora = hora.replace(idioma_en_horario, "")

                            if not horario.text or horario.text == "NO DISPONIBLE":
                                hora = "Sin Horarios Disponibles"
                                
                            peliculas_info.append({
                                'Fecha': datetime.now().strftime("%m-%d-%y"),
                                'País': 'Nicaragua',
                                'Cine': 'Siglo Nuevo',
                                'Nombre Cine': cine_nombre,
                                'Título': nombre,
                                'Hora': hora,
                                'Idioma': idioma,
                                'Formato': formato,
                            })
                        except StaleElementReferenceException:
                            print("      Hora: No disponible")
                else:
                    # Caso donde no hay horarios
                    peliculas_info.append({
                        'Fecha': datetime.now().strftime("%m-%d-%y"),
                        'País': 'Nicaragua',
                        'Cine': 'Siglo Nuevo',
                        'Nombre Cine': cine_nombre,
                        'Título': nombre,
                        'Hora': "Sin Horarios Disponibles",
                        'Idioma': idioma,
                        'Formato': formato,
                    })
                                            
            driver.back()
            
        except Exception as e:
            print(f"Error al procesar el elemento: {e}")
        
 # Crear un DataFrame de Pandas con la información
    df = pd.DataFrame(peliculas_info)

    # Exportar el DataFrame a una hoja de Excel
    df.to_excel('Nicaragua-Siglonuevo.xlsx', index=False)

    print("Datos exportados exitosamente a Nicaragua-Siglonuevo.xlsx")
except Exception as e:
    print(f"Error al encontrar los elementos: {e}")
     
finally:
    driver.quit()



























#  nombreVariable List<SeleniumElements> = driver.getElements(xpath de los elementos de la cartelera que se llamen igual, seria los divs)
 
#  for para recorrer elementos (for each)
 
#  for (SeleniumElement nombreCartita: nombreVariable){
 
#  //cada nombre de tarjeta se puede manipular como elemento individual
 
#  nombreCartita.findElement(xpath del la hora de la pelicula, aca recuerde que va a comenzar el elemento desde el xpath de las cartitas)
 
#  nombreCartita.findElement(xpath del nombre de la pelicula, lo mismo de la parte anterior)
 
#  continuar asi con todos los elementos que se quiera obtener datos
 
#  // recuerdo hacer el get attribute o get Text depende que es lo que quiere mostrar
 
#  } 