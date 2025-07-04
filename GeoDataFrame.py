import geopandas as gpd
import matplotlib.pyplot as plt

# Reemplaza 'ruta/a/tu/archivo.geojson' con la ubicación real de tu archivo
try:
    gdf_comarcas = gpd.read_file('/Users/enrique/code/EFRdev/00 - Post-Bootcamp/Hate_Crimes/data/divisions-administratives-v2r1-20250101/divisions-administratives-v2r1-municipis-5000-20250101.json')
    print("Archivo cargado exitosamente. Las primeras 5 filas:")
    print(gdf_comarcas.head())
    print(gdf_comarcas.shape)
    print("\nColumnas disponibles:")
    print(gdf_comarcas.columns)
    print("\nTipo de geometría:")
    print(gdf_comarcas.geometry.name) # Esto suele ser 'geometry'
    # Intenta hacer un plot rápido para ver si dibuja algo
    gdf_comarcas.plot()
    plt.title("Visualización rápida del GeoJSON")
    plt.show()
except Exception as e:
    print(f"Error al cargar el archivo: {e}")
    print("Asegúrate de que la ruta sea correcta y el archivo sea un GeoJSON válido.")

# Puedes probar con diferentes archivos que sospeches que sean los correctos
# gdf_municipios = gpd.read_file('ruta/a/tu/archivo_municipis.geojson')
# gdf_provincias = gpd.read_file('ruta/a/tu/archivo_provincies.geojson')
