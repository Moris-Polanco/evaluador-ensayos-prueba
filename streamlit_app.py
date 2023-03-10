import streamlit as st
import pandas as pd
import openai
import os
import random

# Ocultar los detalles del archivo cargado en Streamlit
st.set_option('deprecation.showfileUploaderEncoding', False)

# Activar el wide mode
st.set_page_config(layout="wide")

# Accedemos a la clave de API de OpenAI a través de una variable de entorno
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Agregamos un título al principio
st.title('Evaluador de ensayos')

# Agregamos información de instrucciones
st.write('Suba un archivo .XLSX con los ensayos de sus alumnos. Máximo: 10 ensayos.')

# Crear una variable de estado para verificar si el usuario ya ha cargado un archivo
if 'archivo_cargado' not in st.session_state:
    st.session_state.archivo_cargado = False

# Pedimos al usuario que suba el archivo Excel
if not st.session_state.archivo_cargado:
    archivo = st.file_uploader('Cargar archivo Excel', type=['xlsx'])

    if archivo:
        # Leemos el archivo con pandas
        data = pd.read_excel(archivo)

        # Pedimos al usuario que seleccione las columnas con el título y el ensayo
        columnas = data.columns
        columna_titulo = st.selectbox('Selecciona la columna que contiene los títulos:', columnas)
        columna_ensayo = st.selectbox('Selecciona la columna que contiene los ensayos:', columnas)

        # Agregamos un botón para iniciar la evaluación
        if st.button('Evaluar'):
            # Obtenemos los títulos y los ensayos del archivo
            titulos = data[columna_titulo].tolist()
            ensayos = data[columna_ensayo].tolist()

            # Seleccionamos un ensayo al azar
            index = random.randint(0, len(ensayos)-1)
            ensayo = ensayos[index]
            titulo = titulos[index]

            # Utilizamos la API de GPT-3 para calificar el ensayo seleccionado
            prompt = f"Califica el ensayo titulado '{titulo}'. "
            prompt += f"Ensayo: {ensayo}. "
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature=0,
                max_tokens=512,
                n=1,
                stop=None
            )
            justificacion = response.choices[0].text.strip()

            # Agregamos sugerencias de mejora a la justificación
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Sugiere mejoras para el ensayo titulado '{titulo}'. Ensayo: {ensayo}",
                temperature=0,
                max_tokens=512,
                n=1,
                stop=None,
                timeout=60,
            )
            sugerencias = response.choices[0].text.strip()

            # Agregamos la calificación y las sugerencias de mejora a la tabla
            resultados = [{
                'Ensayo': titulo,
                'Justificación': justificacion,
                'Sugerencias de mejora': sugerencias,
            }]

            # Mostramos los resultados en una tabla
            st.write('Resultados:')
            tabla = pd.DataFrame(resultados)
            st.table(tabla)

            # Obtenemos un ensayo al azar del archivo
            ensayo = data[columna_ensayo].sample(n=1).iloc[0]
            titulo = data[columna_titulo][data[columna_ensayo] == ensayo].iloc[0]
            
            # Utilizamos la API de GPT-3 para calificar el ensayo al azar seleccionado
            prompt = f"Califica el ensayo titulado '{titulo}'. Ensayo: {ensayo}. "
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature=0,
                max_tokens=512,
                n=1,
                stop=None
            )
            justificacion = response.choices[0].text.strip()

            # Agregamos sugerencias de mejora a la justificación
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Sugiere mejoras para el ensayo titulado '{titulo}'. Ensayo: {ensayo}",
                temperature=0,
                max_tokens=512,
                n=1,
                stop=None,
                timeout=60,
            )
            sugerencias = response.choices[0].text.strip()

            # Agregamos la calificación y las sugerencias de mejora a la tabla
            resultados = [{
                'Ensayo': titulo,
                'Justificación': justificacion,
                'Sugerencias de mejora': sugerencias,
            }]

            # Mostramos el resultado en una tabla
            st.write('Resultado:')
            tabla = pd.DataFrame(resultados)
            st.table(tabla)

            # Guardar los resultados en un archivo de Excel
            nombre_archivo = 'resultados.xlsx'
            tabla.to_excel(nombre_archivo, index=False)

            # Descargar el archivo de Excel
            st.download_button(
                label='Descargar resultados en Excel',
                data=open(nombre_archivo, 'rb').read(),
                file_name=nombre_archivo,
                mime='application/vnd.ms-excel'
            )


