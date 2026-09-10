import geopandas as gpd
from pathlib import Path

# Path to district shapefile
district_path = Path("data/boundaries/district/district.shp")

# Load district shapefile
districts = gpd.read_file(district_path)

# Number of districts
print("Number of districts:", len(districts))

# Columns
print("\nColumns:")
print(districts.columns.tolist())

# Coordinate Reference System
print("\nCRS:")
print(districts.crs)

# Geometry types
print("\nGeometry types:")
print(districts.geometry.geom_type.value_counts())

# District names and IDs
print("\nDistricts:")
print(districts[["Dist_ID", "District"]].to_string(index=False))