import json
from pathlib import Path
import topojson as tp


# Project paths
input_file = Path("data/boundaries/district/rwanda_districts.geojson")
output_file = Path("data/boundaries/district/rwanda_districts.topojson")


# Read the GeoJSON file
with open(input_file, "r", encoding="utf-8") as file:
    geojson_data = json.load(file)


# Convert GeoJSON to TopoJSON
topology = tp.Topology(geojson_data)


# Save the TopoJSON file
with open(output_file, "w", encoding="utf-8") as file:
    file.write(topology.to_json())


print("TopoJSON conversion completed successfully.")
print(f"Input:  {input_file}")
print(f"Output: {output_file}")