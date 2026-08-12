import json
import urllib.request
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsField, QgsProject
from qgis.PyQt.QtCore import QVariant

print("Setup completed successfully!")

# 1. Define spatial grid (Nagpur Nag River Catchment area)
min_lon, max_lon = 79.02, 79.14
min_lat, max_lat = 21.10, 21.18

cols, rows = 3, 2
dx = (max_lon - min_lon) / cols
dy = (max_lat - min_lat) / rows

# Curve Numbers (CN) for sub-basins (Urban core vs Suburban fringe)
cn_matrix = [
    [75, 82, 88],
    [72, 80, 85]
]

# 2. Create Polygon GIS Layer in memory
layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "Nagpur_SubBasins_StormRunoff", "memory")
provider = layer.dataProvider()
provider.addAttributes([
    QgsField("SubBasinID", QVariant.String),
    QgsField("CurveNumber", QVariant.Int),
    QgsField("Rain_mm", QVariant.Double),
    QgsField("Runoff_mm", QVariant.Double)
])
layer.updateFields()

print("Fetching real storm data & generating spatial polygons...")

# 3. Iterate spatial sub-basins and compute SCS Runoff
for r in range(rows):
    for c in range(cols):
        b_min_x = min_lon + c * dx
        b_max_x = b_min_x + dx
        b_min_y = min_lat + r * dy
        b_max_y = b_min_y + dy
        
        cent_x = (b_min_x + b_max_x) / 2
        cent_y = (b_min_y + b_max_y) / 2
        
        # Real historical storm API call for July 20, 2024
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={cent_y}&longitude={cent_x}&start_date=2024-07-20&end_date=2024-07-20&daily=rain_sum&timezone=auto"
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode('utf-8'))
        P = data['daily']['rain_sum'][0] or 0.0
        
        CN = cn_matrix[r][c]
        S = (25400 / CN) - 254  # Potential max retention (mm)
        Ia = 0.2 * S             # Initial abstraction (mm)
        
        Q = ((P - Ia) ** 2) / (P + 0.8 * S) if P > Ia else 0.0
        
        # Build polygon boundary
        poly_pts = [
            QgsPointXY(b_min_x, b_min_y),
            QgsPointXY(b_max_x, b_min_y),
            QgsPointXY(b_max_x, b_max_y),
            QgsPointXY(b_min_x, b_max_y),
            QgsPointXY(b_min_x, b_min_y)
        ]
        
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPolygonXY([poly_pts]))
        feat.setAttributes([f"SB_{r+1}{c+1}", CN, round(P, 2), round(Q, 2)])
        provider.addFeature(feat)

layer.updateExtents()
QgsProject.instance().addMapLayer(layer)
print("SUCCESS: Sub-basin vector spatial layer loaded into QGIS!")

import os
from qgis.core import (QgsProject, QgsGraduatedSymbolRenderer, 
                       QgsRendererRange, QgsSymbol)
from qgis.PyQt.QtGui import QColor

layer = QgsProject.instance().mapLayersByName("Nagpur_SubBasins_StormRunoff")[0]

# Define 3 Runoff ranges with Blue color gradient
symbol1 = QgsSymbol.defaultSymbol(layer.geometryType())
symbol1.setColor(QColor("#deebf7")) # Light blue

symbol2 = QgsSymbol.defaultSymbol(layer.geometryType())
symbol2.setColor(QColor("#9ecae1")) # Medium blue

symbol3 = QgsSymbol.defaultSymbol(layer.geometryType())
symbol3.setColor(QColor("#3182bd")) # Dark blue

# Create ranges based on runoff depth (mm)
ranges = [
    QgsRendererRange(0, 20, symbol1, "0 - 20 mm (Low)"),
    QgsRendererRange(20, 50, symbol2, "20 - 50 mm (Moderate)"),
    QgsRendererRange(50, 150, symbol3, "50+ mm (High)")
]

renderer = QgsGraduatedSymbolRenderer("Runoff_mm", ranges)
layer.setRenderer(renderer)
layer.triggerRepaint()

# Export map canvas as PNG image for GitHub
output_img = os.path.join(os.path.expanduser("~"), "runoff_map.png")
iface.mapCanvas().saveAsImage(output_img)
print(f"SUCCESS: Map colored and saved to {output_img}")