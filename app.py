import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium # Importació correcta per a Streamlit
from folium.features import GeoJsonTooltip
import unicodedata
import re
import json
import numpy as np # Necessari per a la generació de bins més robusta
import plotly.express as px # Per als gràfics interactius

# --- Configuració de la pàgina de Streamlit ---
st.set_page_config(layout="wide", page_title="HateMap: Dades per una Catalunya Diversa i Sense Odi", page_icon=":police_car:")

# Centrar el títol i el subtítol usant HTML
st.markdown("""<h1 style='text-align: center;'>HateMap: Dades per una Catalunya Diversa i Sense Odi</h1>""", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center;'>
        <h2>Informa’t, Actua, Transforma</h2>
        <p>Aquesta aplicació interactiva et permet explorar com han evolucionat els delictes d’odi més rellevants a Catalunya. També hi trobaràs enllaços útils i fòrums on aprendre a identificar aquest tipus de delictes i saber com denunciar-los.
        Amb la teva participació, podem construir una societat més justa, lliure d’odi, discriminació i violència cap a les minories. Junts podem fer la diferència.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Rutes dels fitxers (AJUSTA AIXÒ A LES TEVES RUTES REALS) ---
# S'assumeix que aquests fitxers estan a la mateixa carpeta que aquest script de Streamlit.
# Si no, si us plau, actualitza les rutes.
# IMPORTANT: Utilitza raw strings (r"...") per a les rutes per evitar problemes amb les barres invertides
PATH_GEOJSON_COMARCAS = r"data/divisions-administratives-v2r1-20250101/divisions-administratives-v2r1-comarques-5000-20250101.json"
PATH_GEOJSON_MUNICIPIOS = r"data/divisions-administratives-v2r1-20250101/Others/divisions-administratives-v2r1-municipis-50000-20250101.json" # Encara es carrega per a la lògica d'agrupació
PATH_GEOJSON_PROVINCIAS = r"data/divisions-administratives-v2r1-20250101/divisions-administratives-v2r1-provincies-5000-20250101.json"
PATH_DELITOS_DATA = r"df_clean_hatecrimes_catalunya.csv" # ¡ACTUALITZA AIXÒ amb el nom i extensió correctes!

# --- Càrrega de dades (amb memòria cau per millorar el rendiment) ---
@st.cache_data
def load_data():
    try:
        # Carregar GeoJSONs
        gdf_comarcas = gpd.read_file(PATH_GEOJSON_COMARCAS)
        gdf_municipios = gpd.read_file(PATH_GEOJSON_MUNICIPIOS) # Encara es carrega per a la lògica d'agrupació
        gdf_provincias = gpd.read_file(PATH_GEOJSON_PROVINCIAS)

        # Carregar DataFrame de delictes
        if PATH_DELITOS_DATA.endswith('.pkl'):
            df = pd.read_pickle(PATH_DELITOS_DATA)
            # st.success(f"DataFrame de delictes carregat correctament des de '{PATH_DELITOS_DATA}' (pickle).") # Eliminat
        elif PATH_DELITOS_DATA.endswith('.xlsx'):
            df = pd.read_excel(PATH_DELITOS_DATA)
            # st.success(f"DataFrame de delictes carregat correctament des de '{PATH_DELITOS_DATA}' (Excel).") # Eliminat
        else:
            try:
                df = pd.read_csv(PATH_DELITOS_DATA, encoding='utf-8')
                # st.success(f"DataFrame de delictes carregat correctament des de '{PATH_DELITOS_DATA}' (CSV UTF-8).") # Eliminat
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(PATH_DELITOS_DATA, encoding='latin1')
                    # st.success(f"DataFrame de delictes carregat correctament des de '{PATH_DELITOS_DATA}' (CSV Latin1).") # Eliminat
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(PATH_DELITOS_DATA, encoding='ISO-8859-1')
                        # st.success(f"DataFrame de delictes carregat correctament des de '{PATH_DELITOS_DATA}' (CSV ISO-8859-1).") # Eliminat
                    except UnicodeDecodeError:
                        df = pd.read_csv(PATH_DELITOS_DATA, encoding='cp1252')
                        # st.success(f"DataFrame de delictes carregat correctament des de '{PATH_DELITOS_DATA}' (CSV cp1252).") # Eliminat

        # Convertir la columna 'Date' a format datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        else:
            st.warning("La columna 'Date' no s'ha trobat al DataFrame de delictes. El filtratge per any podria no funcionar correctament.")

        return gdf_comarcas, gdf_municipios, gdf_provincias, df
    except FileNotFoundError as e:
        st.error(f"Error en carregar el fitxer: {e}. Si us plau, verifica les rutes dels fitxers GeoJSON i del teu DataFrame de delictes.")
        st.stop()
    except Exception as e:
        st.error(f"Ha ocorregut un error inesperat en carregar les dades: {e}. Si us plau, revisa el format i la codificació de '{PATH_DELITOS_DATA}'.")
        st.stop()

gdf_comarcas, gdf_municipios, gdf_provincias, df = load_data()

# --- Funció de normalització (¡CRÍTICA: HA DE SER LA MATEIXA QUE JA UTILITZES!) ---
def cleaning_text(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = text.lower()
    text = text.replace("municipi de ", "")
    text = text.replace("resta municipis abp ", "")
    text = text.replace("abp ", "")
    text = text.replace("l'", "")
    text = text.replace("-", " ")
    text = text.replace("'", "")
    text = " ".join(text.split())
    return text

# --- Diccionari de reemplaçaments (¡CRÍTICA: HA DE SER EL MATEIX QUE JA UTILITZES, ARA ACTUALITZAT!) ---
reemplazos_raw = {
    'baix emporda   la bisbal': 'la bisbal demporda',
    'baix camp   priorat': 'reus',
    'selva interior': 'santa coloma de farners',
    'vall daran   alta ribagorca': 'vielha e mijaran',
    'segarra   urgell': 'tarrega',
    'segria   garrigues   pla durgell': 'cervera',
    'baix emporda   sant feliu': 'sant feliu de guixols',
    'girones   pla de estany': 'girona',
    'alt emporda   roses': 'roses',
    'bages': 'manresa',
    'tarragones': 'tarragona',
    'anoia': 'igualada',
    'garraf': 'vilanova i la geltru',
    'osona': 'vic',
    'solsones': 'solsona',
    'bergueda': 'berga',
    'cerdanyola': 'cerdanyola del valles',
    'calonge' : 'calonge i sant antoni',
    'castell platja daro': 'castell daro, platja daro i sagaro',
    'platja daro': 'platja daro i sagaro',
    'montcada' : 'montcada i reixac'
}
reemplazos = {cleaning_text(k): v for k, v in reemplazos_raw.items()}


# --- Definir les llistes de municipis per a les noves agrupacions (noms normalitzats) ---
selva_litoral_munis_clean = [
    cleaning_text(m) for m in [
        'Blanes', 'Lloret de Mar', 'Tossa de Mar', 'Amer', 'Anglès', 'Arbúcies', 'Breda', 'Brunyola',
        'Caldes de Malavella', 'Fogars de la Selva', 'Hostalric', 'La Cellera de Ter', 'Maçanet de la Selva',
        'Massanes', 'Osor', 'Riells i Viabrea', 'Riudarenes', 'Riudellots de la Selva',
        'Sant Feliu de Buixalleu', 'Sant Hilari Sacalm', 'Sant Julià de Llor i Bonmatí',
        'Santa Coloma de Farners', 'Sils', 'Susqueda', 'Vidreres', 'Vilobí d\'Onyar'
    ]
]
rp_metropolitana_barcelona_munis_clean = [
    cleaning_text(m) for m in [
        'Badalona', 'Barcelona', 'L\'Hospitalet de Llobregat', 'Sant Adrià de Besòs',
        'Santa Coloma de Gramenet', 'Cornellà de Llobregat', 'El Prat de Llobregat',
        'Sant Boi de Llobregat', 'Viladecans', 'Gavà', 'Castelldefels',
        'Esplugues de Llobregat', 'Sant Just Desvern', 'Sant Feliu de Llobregat',
        'Sant Joan Despí', 'Molins de Rei', 'Sant Vicenç dels Horts', 'Pallejà',
        'Sant Andreu de la Barca', 'Castellbisbal', 'Cervelló', 'Corbera de Llobregat',
        'La Palma de Cervelló', 'Torrelles de Llobregat', 'Begues', 'Vallirana',
        'Olesa de Montserrat', 'Abrera', 'Esparreguera', 'Martorell',
        'Sant Esteve Sesrovires', 'Collbató', 'el Papiol', 'Santa Coloma de Cervelló',
        'Montcada i Reixac', 'Ripollet', 'Cerdanyola del Vallès',
        'Sant Cugat del Vallès', 'Barberà del Vallès', 'Montgat', 'Tiana'
    ]
]
baix_ebre_agrupado_munis_clean = [ # Renombrado de "Baix empordá" a "baix ebre (agrupado)"
    cleaning_text(m) for m in [
        'L\'Aldea', 'Aldover', 'Alfara de Carles', 'L\'Ametlla de Mar', 'L\'Ampolla',
        'Benifallet', 'Camarles', 'Deltebre', 'Paüls', 'El Perelló', 'Roquetes',
        'Tivenys', 'Tortosa', 'Xerta'
    ]
]

# --- Funció per mapejar municipis a les noves agrupacions ---
def get_municipio_for_analysis(municipio_clean_name):
    if municipio_clean_name in selva_litoral_munis_clean:
        return 'selva litoral (agrupado)'
    elif municipio_clean_name in rp_metropolitana_barcelona_munis_clean:
        return 'rp metropolitana barcelona (agrupado)'
    elif municipio_clean_name in baix_ebre_agrupado_munis_clean:
        return 'baix ebre (agrupado)'
    elif municipio_clean_name == 'resta municipis':
        return 'resta municipis (agrupado)'
    else:
        return municipio_clean_name

# --- Aplicar normalització i reemplaçaments al DataFrame de delictes ---
# Aquest bloc s'executa un cop amb el DataFrame original 'df'
# S'assumeix que les columnes 'Província_clean', 'Comarca_clean', 'Municipi_clean' i 'Àmbit fet'
# ja existeixen i estan netes en el DataFrame 'df' carregat de PATH_DELITOS_DATA.
# Si no existeixen, hauràs de descomentar i adaptar les línies de neteja originals del teu notebook aquí.

# Aquestes comprovacions són per assegurar que les columnes existeixen abans d'intentar accedir-hi
# Si el teu CSV ja té les columnes '_clean', aquests blocs no faran res.
if 'Província_clean' not in df.columns:
    if 'Província' in df.columns:
        df['Província_clean'] = df['Província'].apply(cleaning_text)
    else:
        st.error("La columna 'Província' o 'Província_clean' no s'ha trobat al DataFrame. Revisa el teu fitxer de dades.")
        st.stop()

if 'Comarca_clean' not in df.columns:
    if 'Comarca' in df.columns:
        df['Comarca_clean'] = df['Comarca'].apply(cleaning_text).replace(reemplazos)
    else:
        st.error("La columna 'Comarca' o 'Comarca_clean' no s'ha trobat al DataFrame. Revisa el teu fitxer de dades.")
        st.stop()

if 'Municipi_clean' not in df.columns:
    if 'Municipi' in df.columns:
        df['Municipi_clean'] = df['Municipi'].apply(cleaning_text)
    else:
        st.error("La columna 'Municipi' o 'Municipi_clean' no s'ha trobat al DataFrame. Revisa el teu fitxer de dades.")
        st.stop()

# Assegura't que 'Municipi_clean' ja existeix abans d'aplicar 'get_municipio_for_analysis'
if 'Municipi_clean' in df.columns:
    df['Municipi_for_analysis'] = df['Municipi_clean'].apply(get_municipio_for_analysis)
else:
    st.error("La columna 'Municipi_clean' no s'ha trobat al DataFrame. Impossible crear 'Municipi_for_analysis'.")
    st.stop()


# --- Normalitzar columnes als GeoDataFrames ---
gdf_comarcas['NOMCOMAR_clean'] = gdf_comarcas['NOMCOMAR'].apply(cleaning_text)
gdf_municipios['NOMMUNI_clean'] = gdf_municipios['NOMMUNI'].apply(cleaning_text)
gdf_provincias['NOMPROV_clean'] = gdf_provincias['NOMPROV'].apply(cleaning_text)


# --- Filtrar el DataFrame per als tipus de delicte d'interès ---
if 'Àmbit fet' not in df.columns:
    st.error("La columna 'Àmbit fet' no s'ha trobat al DataFrame. Revisa el teu fitxer de dades.")
    st.stop()

tipos_de_delito_interes = ['lgtbi fobia', 'etnic/origen nacional/origen racial', 'sexisme']
# df_filtered_delitos_base es el DataFrame base antes de aplicar filtros geográficos específicos
df_filtered_delitos_base = df[df['Àmbit fet'].isin(tipos_de_delito_interes)].copy()


# --- Preparar dades per als merges (només per a mapes de Província i Comarca) ---
@st.cache_data
def prepare_data_for_maps(df_filtered_geo, _gdf_comarcas, _gdf_provincias):
    # Dades per Comarca
    if 'Comarca_clean' not in df_filtered_geo.columns:
        st.error("La columna 'Comarca_clean' no s'ha trobat en el DataFrame filtrat. Revisa la càrrega i neteja de dades.")
        return None, None # Retorna None per evitar errors posteriors

    df_comarca_victimas = df_filtered_geo.groupby('Comarca_clean')['Nombre víctimes'].sum().reset_index()
    gdf_comarcas_con_datos = _gdf_comarcas.merge(df_comarca_victimas,
                                               left_on='NOMCOMAR_clean',
                                               right_on='Comarca_clean',
                                               how='left')
    gdf_comarcas_con_datos['Nombre víctimes'] = gdf_comarcas_con_datos['Nombre víctimes'].fillna(0)

    # Dades per Província
    if 'Província_clean' not in df_filtered_geo.columns:
        st.error("La columna 'Província_clean' no s'ha trobat en el DataFrame filtrat. Revisa la càrrega i neteja de dades.")
        return None, None

    df_provincia_victimas = df_filtered_geo.groupby('Província_clean')['Nombre víctimes'].sum().reset_index()
    gdf_provincias_con_datos = _gdf_provincias.merge(df_provincia_victimas,
                                                     left_on='NOMPROV_clean',
                                                     right_on='Província_clean',
                                                     how='left')
    gdf_provincias_con_datos['Nombre víctimes'] = gdf_provincias_con_datos['Nombre víctimes'].fillna(0)

    return gdf_comarcas_con_datos, gdf_provincias_con_datos

# Preparar dades per a la taula d'agrupacions de municipis (independent del mapa)
@st.cache_data
def prepare_municipal_aggregations(df_filtered_geo, _gdf_municipios):
    # Assegura't que 'Municipi_for_analysis' existeix abans de continuar
    if 'Municipi_for_analysis' not in df_filtered_geo.columns:
        st.error("La columna 'Municipi_for_analysis' no s'ha trobat en el DataFrame filtrat. Impossible preparar les agrupacions municipals.")
        return pd.DataFrame() # Retorna un DataFrame buit per evitar errors

    municipios_en_geojson = set(_gdf_municipios['NOMMUNI_clean'].unique())
    explicit_aggregates = [
        'selva litoral (agrupado)',
        'rp metropolitana barcelona (agrupado)',
        'baix ebre (agrupado)',
        'resta municipis (agrupado)'
    ]

    df_municipio_victimas = df_filtered_geo.groupby('Municipi_for_analysis')['Nombre víctimes'].sum().reset_index()

    df_municipio_victimas_individuales = df_municipio_victimas[
        ~df_municipio_victimas['Municipi_for_analysis'].isin(explicit_aggregates)
    ].copy()

    df_agrupaciones_municipales = df_municipio_victimas[
        df_municipio_victimas['Municipi_for_analysis'].isin(explicit_aggregates)
    ].copy()

    non_matching_individual_munis = df_municipio_victimas_individuales[
        ~df_municipio_victimas_individuales['Municipi_for_analysis'].isin(municipios_en_geojson)
    ].copy()

    total_victimas_resta_dinamica = non_matching_individual_munis['Nombre víctimes'].sum()

    # Afegir la categoria "resta municipis (agrupado)" si hi ha víctimes
    if total_victimas_resta_dinamica > 0:
        resta_df = pd.DataFrame([{
            'Municipi_for_analysis': 'resta municipis (agrupado)',
            'Nombre víctimes': total_victimas_resta_dinamica
        }])
        df_agrupaciones_municipales = pd.concat([df_agrupaciones_municipales, resta_df], ignore_index=True)

    # Assegurar que 'Nombre víctimes' estigui omplert per a la visualització
    df_agrupaciones_municipales['Nombre víctimes'] = df_agrupaciones_municipales['Nombre víctimes'].fillna(0)
    return df_agrupaciones_municipales


# --- Selectors per filtrar per zona geogràfica ---
level = st.selectbox(
    "Selecciona el nivell geogràfic per visualitzar:",
    ("Província", "Comarca")
)

selected_province = None
selected_comarca = None
geo_filter_name = "Catalunya" # Valor predeterminat per al títol dels gràfics

if level == "Província":
    provinces = sorted(df_filtered_delitos_base['Província_clean'].unique())
    selected_province = st.selectbox("Selecciona una província:", ['Totes les Províncies'] + provinces)
    if selected_province != 'Totes les Províncies':
        df_filtered_geo = df_filtered_delitos_base[df_filtered_delitos_base['Província_clean'] == selected_province].copy()
        geo_filter_name = selected_province
    else:
        df_filtered_geo = df_filtered_delitos_base.copy()
        geo_filter_name = "Catalunya"
elif level == "Comarca":
    comarcas = sorted(df_filtered_delitos_base['Comarca_clean'].unique())
    selected_comarca = st.selectbox("Selecciona una comarca:", ['Totes les Comarques'] + comarcas)
    if selected_comarca != 'Totes les Comarques':
        df_filtered_geo = df_filtered_delitos_base[df_filtered_delitos_base['Comarca_clean'] == selected_comarca].copy()
        geo_filter_name = selected_comarca
    else:
        df_filtered_geo = df_filtered_delitos_base.copy()
        geo_filter_name = "Catalunya"

# Ara, df_filtered_delitos_base es converteix en df_filtered_geo per als següents passos
# Això assegura que els gràfics i la taula d'agrupacions reaccionin al filtre geogràfic.
df_filtered_delitos = df_filtered_geo.copy()


# Se revisa si prepare_data_for_maps retorna valors vàlids abans de desempaquetar
prepared_map_data = prepare_data_for_maps(df_filtered_delitos, gdf_comarcas, gdf_provincias)

if prepared_map_data is None:
    st.stop()
else:
    gdf_comarcas_con_datos, gdf_provincias_con_datos = prepared_map_data

# Preparar les dades per a la taula d'agrupacions de municipis
df_agrupaciones_municipales = prepare_municipal_aggregations(df_filtered_delitos, gdf_municipios)


# --- Funció per crear el mapa de Folium ---
def create_folium_map(gdf, column, name_column, title):
    # Calcular el centre de Catalunya per centrar el mapa
    # Això és una aproximació, pots ajustar les coordenades si és necessari
    catalonia_center = [41.7, 2.0]
    m = folium.Map(location=catalonia_center, zoom_start=8, tiles="cartodbpositron")

    # Crear un colormap per a la llegenda
    min_val = gdf[column].min()
    max_val = gdf[column].max()

    # Lògica més robusta per als bins: assegura sempre almenys 3 rangs (4 punts)
    if min_val == max_val:
        # Si tots els valors són iguals, crea 4 bins artificials
        if max_val == 0:
            bins = [0, 1, 2, 3] # Per a tots els zeros
        else:
            bins = [max_val, max_val + 1, max_val + 2, max_val + 3]
    else:
        try:
            bins = list(gdf[column].quantile([0, 0.25, 0.5, 0.75, 1]))
            bins = sorted(list(set(bins))) # Eliminar duplicats i ordenar
            # Assegurar almenys 4 bins únics (3 intervals)
            if len(bins) < 4:
                # Fallback a bins espaiats linealment si els quantils no proporcionen prou
                bins = np.linspace(min_val, max_val, 4).tolist()
                bins = sorted(list(set(bins)))
        except Exception: # Fallback si els quantils fallen per alguna raó
            bins = np.linspace(min_val, max_val, 4).tolist()
            bins = sorted(list(set(bins)))

    # Salvaguarda final: assegura que 'bins' té almenys 4 valors únics
    while len(bins) < 4:
        if len(bins) == 0: bins = [0, 1, 2, 3]
        elif len(bins) == 1: bins = [bins[0], bins[0]+1, bins[0]+2, bins[0]+3]
        elif len(bins) == 2: bins = [bins[0], bins[1], bins[1]+1, bins[1]+2]
        elif len(bins) == 3: bins = [bins[0], bins[1], bins[2], bins[2]+1]
        bins = sorted(list(set(bins)))


    # Crear el mapa coroplètic
    folium.Choropleth(
        geo_data=json.loads(gdf.to_json()), # Convertir a diccionari GeoJSON
        name="choropleth",
        data=gdf,
        columns=[name_column, column],
        key_on=f"feature.properties.{name_column}",
        fill_color="YlOrRd", # Paleta de colors
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"Nombre de Víctimes de Delictes d'Odi per {title}",
        bins=bins, # Passar els bins calculats
        highlight=True,
    ).add_to(m)

    # Afegir tooltips per mostrar informació al passar el ratolí
    style_function = lambda x: {'fillColor': '#ffffff', 'color':'#000000', 'fillOpacity': 0.1, 'weight': 0.1}
    highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.50, 'weight': 0.1}
    NIL = folium.features.GeoJson(
        gdf,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=GeoJsonTooltip(
            fields=[f'{name_column}', f'{column}'],
            aliases=[f'{title}:', 'Víctimes:'],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                color: #333333;
                font-family: arial;
                font-size: 12px;
                padding: 10px;
            """,
            max_width=800
        )
    )
    m.add_child(NIL)
    m.keep_in_front(NIL)
    folium.LayerControl().add_to(m)
    return m

# --- Renderitzar el mapa segons la selecció de l'usuari ---
if level == "Província":
    st.markdown("<h3 style='text-align: center;'>🗺️ Mapa de Delictes d'Odi per Província</h3>", unsafe_allow_html=True)
    col_map = st.columns([1, 2, 1])[1] # Centrar el mapa
    with col_map:
        m = create_folium_map(gdf_provincias_con_datos, 'Nombre víctimes', 'NOMPROV_clean', 'Província')
        st_folium(m, height=500, width=1000) # Utilitzar st_folium
elif level == "Comarca":
    st.markdown("<h3 style='text-align: center;'>🗺️ Mapa de Delictes d'Odi per Comarca</h3>", unsafe_allow_html=True)
    col_map = st.columns([1, 2, 1])[1] # Centrar el mapa
    with col_map:
        m = create_folium_map(gdf_comarcas_con_datos, 'Nombre víctimes', 'NOMCOMAR_clean', 'Comarca')
        st_folium(m, height=500, width=1000)


# --- Secció de Gràfics Addicionals ---
st.markdown("---")
st.markdown("### 📈 Anàlisi Temporal i per Tipus de Delicte")

# Gràfic 1: Evolució Anual de Delictes d'Odi
st.markdown("#### Evolució Anual de Delictes d'Odi per Tipus")
# Agrupar per any i tipus de delicte, i sumar les víctimes
df_annual_evolution = df_filtered_delitos.groupby([df_filtered_delitos['Date'].dt.year, 'Àmbit fet'])['Nombre víctimes'].sum().reset_index()
df_annual_evolution.columns = ['Any', 'Tipus de Delicte', 'Total Víctimes']

fig_line = px.line(df_annual_evolution, x='Any', y='Total Víctimes', color='Tipus de Delicte',
                   title=f'Evolució Anual del Nombre de Víctimes de Delictes d\'Odi per Tipus en {geo_filter_name}',
                   labels={'Any': 'Any', 'Total Víctimes': 'Nombre Total de Víctimes'},
                   markers=True)
fig_line.update_layout(hovermode="x unified") # Millora la interactivitat del tooltip
st.plotly_chart(fig_line, use_container_width=True)

# Gràfic 2: Distribució de Delictes per Tipus (per a la zona seleccionada)
st.markdown("#### Distribució de Delictes d'Odi per Tipus")
df_type_distribution = df_filtered_delitos.groupby('Àmbit fet')['Nombre víctimes'].sum().reset_index()
df_type_distribution.columns = ['Tipus de Delicte', 'Total Víctimes']

fig_bar = px.bar(df_type_distribution, x='Tipus de Delicte', y='Total Víctimes',
                 title=f'Distribució del Nombre de Víctimes per Tipus de Delicte d\'Odi en {geo_filter_name}',
                 labels={'Tipus de Delicte': 'Tipus de Delicte', 'Total Víctimes': 'Nombre Total de Víctimes'},
                 color='Tipus de Delicte') # Coloreja per tipus de delicte
st.plotly_chart(fig_bar, use_container_width=True)


# --- Organització visual en dues columnes (per a la taula d'agrupacions i informació de contacte) ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("#### 📊 Dades Agrupades de Municipis Especials")
    if not df_agrupaciones_municipales.empty:
        st.dataframe(
            df_agrupaciones_municipales.set_index('Municipi_for_analysis'),
            use_container_width=True,
            height=350
        )
    else:
        st.info("No hi ha dades per a les agrupacions especials de municipis.")

with col2:
    st.markdown("""
    <div style="background-color:transparent; border:2px solid #444444; border-radius:8px; padding:18px 14px 14px 14px; margin-bottom:10px;">
        <h4 style="text-align:center; margin-top:0;">🚨 Actua pren l'odi:</h4>
        <ul style="padding-left:18px; font-size:16px;">
            <li>🏳️‍🌈 <b>LGTBIQ+</b>: Assegura’t suport i responsabilitat amb <b>Línia Arcoíris (028)</b>. Per mes informació visita: <a href="https://plataformalgtbi.cat/" target="_blank" style="color:#1E90FF; text-decoration:underline;">Plataforma LGBT Cat</a></li>
            <li>✊ <b>Ètnia/racial</b>: Troba ajuda a la teva <b>SAiD SOS Racisme</b> (<a href='https://sosracisme.org/es/said-5/' target='_blank' style='color:#1E90FF; text-decoration:underline;'>https://sosracisme.org/es/said-5/</a>)</li>
            <li>🚺 <b>Sexisme</b>: Si és urgent, truca a <b>112</b> o contacta directament amb la <b>Guàrdia Civil (062)</b> (<a href='https://serveiocupacio.gencat.cat/es/soc/igualtat-de-genere-i-ocupacio/recursos-per-donar-suport-a-dones-victimes-de-la-violencia-masclista/' target='_blank' style='color:#1E90FF; text-decoration:underline;'>més informació aquí</a>)</li>
            <li>📞 Si vols denunciar un delicte d’odi, contacta amb la <b>Policia Nacional (091)</b> o la <b>Guàrdia Civil (062)</b></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- Enllaços i recursos addicionals ---
st.markdown("""
---
### Dades i Consideracions Tècniques:
* **Font de Dades:** Aquesta aplicació utilitza dades de delictes d'odi a Catalunya, filtrades per tipus específics (LGTBIQ+, ètnia/racial, sexisme) i agrupades per nivells geogràfics (província, comarca, municipi).
* **Visualització:** Els mapes es generen utilitzant Folium i Streamlit, permetent una visualització interactiva de les dades geogràfiques.
* **Dependències:** Aquesta aplicació requereix les biblioteques `streamlit`, `geopandas`, `pandas`, `folium`, `streamlit-folium`, `numpy`, i `plotly` per al seu funcionament.
""")
