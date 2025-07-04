# HateMap: Dades per una Catalunya Diversa i Sense Odi

## Idiomas / Languages / Idiomes
- [Español](#español)
- [English](#english)
- [Català](#català)

---

## Español

## Índice
- [Descripción del Proyecto](#descripción-del-proyecto)
- [Características](#características)
- [Aplicación](#aplicación)
- [¿Cómo se Llevó a Cabo la Investigación?](#cómo-se-llevó-a-cabo-la-investigación)
- [Futuras Actualizaciones](#futuras-actualizaciones)

##

## Descripción del Proyecto
HateMap es una aplicación interactiva desarrollada con Streamlit que permite explorar la evolución de los delitos de odio más relevantes en Cataluña. Este proyecto se centra en la visualización de datos relacionados con la LGTBIQ+fobia, el odio étnico/racial y el sexismo, ofreciendo una perspectiva geográfica por provincias y comarcas, así como análisis temporales y por tipo de delito.

El objetivo principal de HateMap es informar a la ciudadanía, promover la acción contra la discriminación y contribuir a la transformación social hacia una Cataluña más justa y libre de odio. La aplicación también proporciona enlaces útiles y recursos para identificar estos delitos y saber cómo denunciarlos.

## Características
Mapas Interactivos: Visualización de la distribución de delitos de odio por provincia y comarca utilizando Folium.

Análisis Temporal Dinámico: Gráficos de líneas que muestran la evolución anual del número de víctimas por tipo de delito (LGTBIQ+fobia, étnico/racial, sexismo), actualizándose según la provincia o comarca seleccionada en el mapa.

Distribución por Tipo de Delito: Gráficos de barras que detallan la proporción de víctimas por cada tipo de delito de odio, también adaptándose a la selección geográfica.

Filtrado Geográfico: Todos los gràficos y mapas se actualizan dinámicamente según la provincia o comarca seleccionada.

Datos Agrupados de Municipios Especiales: Tabla con datos agregados para zonas con agrupaciones municipales específicas que no se visualizan individualmente en el mapa.

Recursos y Contactos: Información actualizada sobre dónde encontrar apoyo y cómo denunciar delitos de odio.

##  Aplicación

Puedes explorar la aplicación en la URL: ----------

La aplicación sigue en desarrollo.

## ¿Cómo se Llevó a Cabo la Investigación?
Este proyecto se construyó a partir de un análisis exhaustivo de datos de delitos de odio en Cataluña, utilizando herramientas de Python para la manipulación, limpieza y visualización de datos.

### Fuentes de Datos:

Delitos de Odio: La información principal proviene de un conjunto de datos de delictes d'odi en Cataluña, cargado desde un archivo CSV (o pickle/Excel, según la configuración final) denominado df_clean_hatecrimes_catalunya.csv. Este DataFrame contiene detalles sobre el tipo de delito, el número de víctimas y la ubicación geográfica.

FUENTES: -----

Geometrías Geográficas: Para la representación cartográfica, se utilizaron archivos GeoJSON que definen las divisiones administrativas de Cataluña: provincias (divisions-administratives-v2r1-provincies-5000-20250101.json), comarcas (divisions-administratives-v2r1-comarques-5000-20250101.json) y municipios (divisions-administratives-v2r1-municipis-50000-20250101.json).

FUENTES: -----

### Análisis Realizado:

El análisis se centró en tres categorías principales de delitos de odio: **lgtbi fobia, etnic/origen racial y sexisme.**

Se realizó una agregación de las víctimas por año para observar la evolución temporal de cada tipo de delito.

Los datos también se agruparon por niveles geográficos (provincia y comarca) para entender la distribución espacial de los incidentes. (la visualización por Municipios sigue en desarrollo)

Se gestionaron agrupaciones especiales de municipios (como "selva litoral", "rp metropolitana barcelona", "baix ebre", y "resta municipis") para consolidar los datos de áreas que no tenían una correspondencia directa con una única geometría municipal en los GeoJSON, permitiendo una representación más precisa de la realidad de los datos.

### Limpieza y Normalización de Textos:

Una parte crucial del proceso fue la limpieza y normalización de los nombres geográficos en el DataFrame de delitos. Se implementó una función cleaning_text que convierte el texto a minúsculas, elimina tildes y caracteres no ASCII, suprime prefijos comunes como "municipi de ", y elimina espacios extra.

Además, se utilizó un diccionario de reemplazos (reemplazos_raw) para corregir inconsistencias y mapear nombres alternativos o abreviados de comarcas y municipios a un formato unificado que coincidiera con los nombres en los archivos GeoJSON. Esto fue fundamental para poder realizar las uniones (merge) entre los datos de delitos y las geometrías geográficas.

### Tipos de Gráficas Generadas:

**Mapas Coropléticos (Folium):** Se generaron mapas interactivos para visualizar la densidad de delitos de odio por provincia y comarca. Estos mapas permiten una exploración visual de las áreas más afectadas, mostrando el número de víctimas al pasar el ratón sobre cada región.

(Aquí puedes insertar una captura de pantalla de un mapa generado en tu notebook)

**Gráficos de Líneas (Plotly Express):** Se crearon gráficos para mostrar la "Evolución Anual del Número de Víctimas de Delitos de Odio por Tipo". Estos gràficos permiten observar las tendencias a lo largo del tiempo para cada categoría de odio (LGTBIQ+fobia, étnico/racial, sexismo) y se actualizan dinámicamente según la selección geográfica del usuario.

(Aquí puedes insertar una captura de pantalla del gráfico de evolución anual de tu notebook)

**Gráficos de Barras (Plotly Express):** Se utilizaron para visualizar la "Distribución del Número de Víctimas por Tipo de Delicte de Odio". Estos gràficos resumen el total de víctimas por cada categoría de odio y también se adaptan a la región seleccionada por el usuario.

(Aquí puedes insertar una captura de pantalla del gráfico de barras de tu notebook, similar al que mostraste en el hate_crimes.py snippet)

## Futuras Actualizaciones
Este proyecto está concebido como una herramienta viva y en constante evolución. Tenemos previsto realizar las siguientes actualizaciones:

**Actualización Anual de Dades:** La página se renovará anualmente con las dades más recientes de delictes d'odi a Catalunya para garantizar la relevancia y precisión de la información.

**Desenvolupament d'Aplicació Mòbil:** Para mejorar la accesibilidad y la utilización, se trabajará en el desarrollo de una aplicación móvil que permita a los usuarios acceder a las dades y recursos desde cualquier dispositivo.

Con estas mejoras, esperamos que HateMap continúe siendo una herramienta valiosa en la lucha contra el odio y la discriminación.

---

## English

*Coming soon...*

---

## Català

*Properament...*
