# 🔍 Buscar Shapefile - Plugin para QGIS

**Versión:** 1.0 Estable  
**Autor:** Raul Viquez  
**Email:** viquezr@gmail.com

---

## 📋 Descripción

Plugin inteligente para QGIS que permite buscar archivos **shapefile** (.shp) en una carpeta y sus subcarpetas, cargarlos automáticamente en el proyecto y **convertirlos al Sistema de Coordenadas de Referencia (CRS) deseado** de forma transparente.

---

## ✨ Características principales

- 🔎 **Búsqueda recursiva** en carpetas y subcarpetas
- 🗺️ **Conversión automática de CRS** (WGS84, UTM, Web Mercator, o personalizado)
- ⚡ **Hilo de búsqueda independiente** (no bloquea la interfaz de QGIS)
- 📊 **Barra de progreso** y feedback visual
- 🔄 **Conversión transparente** - mantiene la geometría y atributos originales
- 🛡️ **Validación de shapefiles** (verifica archivos .shp, .shx, .dbf)
- 🎨 **Interfaz amigable** con estilo moderno

---

## 🚀 Instalación

### Método 1: Desde ZIP en QGIS
1. Descarga el plugin como archivo ZIP
2. En QGIS, ve a **Complementos → Administrar e Instalar Complementos**
3. Selecciona **Instalar desde ZIP**
4. Elige el archivo ZIP y haz clic en **Instalar complemento**

### Método 2: Manual
1. Copia la carpeta del plugin a:  
   - **Windows:** `C:\Users\TU_USUARIO\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`  
   - **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`  
   - **macOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
2. Reinicia QGIS o activa el plugin desde el menú de complementos

---

## 🎯 Cómo usar

1. **Abrir el plugin:**  
   - Botón en la barra de herramientas 🎛️  
   - Menú → Complementos → Buscar Shapefile

2. **Configurar búsqueda:**
   - 📁 **Seleccionar carpeta** donde buscar
   - 📄 **Nombre del shapefile** (sin extensión .shp)
   - 🗺️ **CRS destino** (EPSG:32617 por defecto)

3. **Opciones de conversión:**
   - ✓ **Convertir automáticamente** (activado por defecto)
   - Selección rápida de CRS comunes:
     - EPSG:32617 - UTM zone 17N
     - EPSG:4326 - WGS 84
     - EPSG:3857 - Web Mercator
     - **Personalizado** - ingresa cualquier código EPSG

4. **Ejecutar:**  
   Click en **🚀 BUSCAR Y CARGAR**

---

## 📊 Ejemplo de uso

**Escenario:** Necesitas cargar un shapefile llamado "parcelas" que está en una estructura de carpetas compleja.

1. Carpeta raíz: `D:\GIS\Proyectos\2024\`
2. Nombre a buscar: `parcelas`
3. CRS destino: `EPSG:32617` (UTM 17N)

El plugin buscará recursivamente en:

D:\GIS\Proyectos\2026
├── datos
│ └── shapefiles
│ └── parcelas.shp ✓ encontrado
└── backups
└── parcelas_old.shp ✓ encontrado


Cargará **todos los shapefiles** que coincidan con el nombre, convirtiéndolos automáticamente al CRS seleccionado.

---

## 🔧 Requisitos

- **QGIS 3.0** o superior
- Dependencias: Todas incluidas en QGIS base
- Sistema operativo: Windows / Linux / macOS

---

## ⚠️ Notas importantes

### Conversión de CRS
- El plugin **no modifica** los archivos originales
- Crea copias temporales para la conversión
- La conversión es transparente para el usuario

### Validación de shapefiles
- Verifica la existencia de archivos `.shp`, `.shx` y `.dbf`
- Si falta algún archivo, el shapefile no se carga

### Rendimiento
- La búsqueda se ejecuta en un **hilo separado** (no bloquea QGIS)
- Soporta búsqueda en miles de archivos sin problemas

---

## 🐛 Reporte de errores

Si encuentras algún problema o tienes sugerencias:

- 📧 **Email:** viquezr@gmail.com
- 🐙 **GitHub Issues:** [Crear issue](https://github.com/viquezr/buscar_shapefiles/issues)

Incluye en tu reporte:
1. Versión de QGIS
2. Sistema operativo
3. Pasos para reproducir el error
4. Captura de pantalla (si aplica)

---

## 📝 Registro de cambios

### Versión 1.0 (Estable) - 2024
- ✅ Búsqueda recursiva en carpetas
- ✅ Conversión automática de CRS
- ✅ Interfaz gráfica completa
- ✅ Barra de progreso y feedback visual
- ✅ Soporte para CRS personalizados
- ✅ Validación de archivos shapefile
- ✅ Hilo de búsqueda independiente

---

## 📄 Licencia

Este plugin es de **código abierto** y puede ser usado, modificado y distribuido libremente.

---

## 🙏 Agradecimientos

Desarrollado para la comunidad de usuarios de QGIS.

---

## 🔗 Enlaces útiles

- [Documentación de QGIS](https://qgis.org/docs/)
- [Sistemas de Coordenadas - EPSG](https://epsg.io/)
- [PyQGIS API](https://qgis.org/pyqgis/)

---

**¡Disfruta del plugin!** 🗺️✨

