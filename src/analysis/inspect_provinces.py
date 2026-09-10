import geopandas as gpd

file_path = "data/boundaries/rwanda_provinces.geojson"

provinces = gpd.read_file(file_path)

print("Number of provinces:", len(provinces))
print("\nColumns:")
print(provinces.columns.tolist())

print("\nProvince names:")
print(provinces["prov_engl"].tolist())

print("\nCRS:")
print(provinces.crs)

print("\nGeometry types:")
print(provinces.geometry.geom_type.value_counts())

print("\nInvalid geometries:", (~provinces.geometry.is_valid).sum())