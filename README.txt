# 🔍 Search Shapefile - QGIS Plugin

**Version:** 1.0 Stable  
**Author:** Raul Viquez  
**Email:** viquezr@gmail.com  

---

## 📋 Description

Search Shapefile is a smart QGIS plugin designed to efficiently locate **shapefile (.shp)** files within a folder and its subfolders. It automatically loads them into your QGIS project and **converts them to a desired Coordinate Reference System (CRS)** seamlessly.

---

## ✨ Key Features

- 🔎 Recursive search in folders and subfolders  
- 🗺️ Automatic CRS conversion (WGS84, UTM, Web Mercator, or custom EPSG)  
- ⚡ Non-blocking search (runs in a separate thread)  
- 📊 Progress bar with real-time feedback  
- 🔄 Transparent conversion (preserves geometry and attributes)  
- 🛡️ Shapefile validation (.shp, .shx, .dbf required)  
- 🎨 Clean and user-friendly interface  

---

## 🚀 Installation

### Option 1: Install from ZIP (Recommended)
1. Download the plugin as a ZIP file  
2. Open QGIS  
3. Go to **Plugins → Manage and Install Plugins**  
4. Click **Install from ZIP**  
5. Select the ZIP file and install  

### Option 2: Manual Installation
1. Copy the plugin folder to:

Windows:
C:\Users\YOUR_USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\

Linux:
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/

macOS:
~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/

2. Restart QGIS or enable the plugin manually  

---

## 🎯 Usage

1. Open the plugin:
   - Toolbar button 🎛️  
   - Plugins → Search Shapefile  

2. Configure:
   - Select the root folder  
   - Enter shapefile name (without .shp)  
   - Choose target CRS (default: EPSG:32617)  

3. Conversion Options:
   - Enable automatic CRS conversion  
   - Choose from common CRS:
     - EPSG:32617 (UTM Zone 17N)
     - EPSG:4326 (WGS84)
     - EPSG:3857 (Web Mercator)
     - Custom EPSG code  

4. Run:
   Click **SEARCH AND LOAD**

---

## 📊 Example

Searching for "parcelas" inside:

D:\GIS\Projects\2026\

The plugin will scan:

data/
  shapefiles/
    parcelas.shp ✓
backups/
  parcelas_old.shp ✓

All matching files will be loaded and converted automatically.

---

## 🔧 Requirements

- QGIS 3.0 or higher  
- No additional dependencies required  

---

## ⚠️ Notes

- Original files are never modified  
- Temporary layers are used for CRS conversion  
- Missing shapefile components will prevent loading  

---

## 🐛 Bug Reports

Report issues or suggestions:

GitHub:
https://github.com/viquezr/buscar_shapefiles/issues  

Email:
viquezr@gmail.com  

Include:
- QGIS version  
- OS  
- Steps to reproduce  
- Screenshot if possible  

---

## 📝 Changelog

### Version 1.0 (2024)
- Recursive search  
- CRS conversion  
- Full GUI  
- Progress feedback  
- Custom CRS support  
- Shapefile validation  
- Multi-threading support  

---

## 📄 License

Open source – free to use, modify, and distribute.

---

## 🙏 Acknowledgements

Developed for the QGIS community.

---

## 🔗 Useful Links

QGIS Docs: https://qgis.org/docs/  
EPSG Reference: https://epsg.io/  
PyQGIS API: https://qgis.org/pyqgis/  

---

**Enjoy the plugin!** 🚀
