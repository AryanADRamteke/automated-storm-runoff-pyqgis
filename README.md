# Automated Urban Storm Runoff & SCS-CN Spatial Estimator (PyQGIS)

An automated Python-based GIS spatial workflow developed within QGIS to evaluate surface runoff depth ($Q$) across urban and suburban sub-basins during extreme precipitation events. The tool fetches live historical weather station/reanalysis data for the Nag River Catchment (Nagpur, India) and applies the USDA NRCS Soil Conservation Service Curve Number (SCS-CN) method.

![Nagpur Storm Runoff Intensity Map](runoff_map.png)

---

## Technical Highlights
* **Automated Data Pipeline:** Pulls historical daily rainfall records directly from the Open-Meteo Historical Weather API (ERA5 ECMWF reanalysis) without downloading heavy raster datasets.
* **Vector Grid Discretization:** Generates dynamic sub-basin boundaries programmatically across defined spatial bounding boxes.
* **SCS-CN Hydrologic Modeling:** Computes potential maximum retention ($S$), initial abstraction ($I_a$), and surface runoff ($Q$) for varying urban land-use Curve Numbers.
* **GIS Automation:** Built using native `PyQGIS` libraries (`QgsVectorLayer`, `QgsFeature`, `QgsGraduatedSymbolRenderer`).

---

## Methodology & Equations

The SCS Curve Number method determines runoff depth ($Q$) based on precipitation ($P$) and land surface characteristics:

1. **Potential Maximum Retention ($S$):**
   $$S = \frac{25400}{CN} - 254 \quad \text{(mm)}$$

2. **Initial Abstraction ($I_a$):**
   $$I_a = 0.2 \times S \quad \text{(mm)}$$

3. **Direct Surface Runoff Depth ($Q$):**
   $$Q = \begin{cases} \frac{(P - I_a)^2}{P + 0.8S}, & \text{if } P > I_a \\ 0, & \text{if } P \le I_a \end{cases}$$

Where $CN$ represents the composite Curve Number based on hydrologic soil group and land cover attributes.

---

## Project Structure
```text
├── runoff_map.png             # Exported spatial runoff intensity map
├── scripts/
│   └── runoff_generator.py    # Main PyQGIS automation script
└── README.md                  # Project documentation
