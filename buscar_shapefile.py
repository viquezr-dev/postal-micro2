# -*- coding: utf-8 -*-
"""
buscar_shapefiles - Plugin para QGIS
Desarrollado por Raul Viquez (viquezr@gmail.com)
Version: 1.0 - Estable
"""

from qgis.PyQt.QtWidgets import (QAction, QDialog, QVBoxLayout, QHBoxLayout, 
                                QLabel, QLineEdit, QPushButton, QProgressBar,
                                QMessageBox, QGroupBox, QFileDialog, QFrame,
                                QApplication, QWidget, QSpacerItem, QSizePolicy,
                                QComboBox, QCheckBox)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal, QTimer
from qgis.PyQt.QtGui import QFont, QColor, QPixmap, QIcon
from qgis.core import (QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem,
                      QgsCoordinateTransform, QgsFeature, QgsVectorFileWriter,
                      QgsFields, QgsWkbTypes, QgsField)
from qgis.utils import iface
import os
import tempfile

# CRS por defecto (EPSG:32617 - WGS 84 / UTM zone 17N)
CRS_DEFAULT = QgsCoordinateReferenceSystem("EPSG:32617")

def verificar_y_convertir_crs(capa, crs_destino=CRS_DEFAULT):
    """
    Verifica si una capa está en el CRS destino y la convierte si es necesario.
    Retorna la capa original o una nueva capa convertida.
    """
    try:
        # Verificar CRS actual
        crs_actual = capa.crs()
        
        # Si ya está en el CRS destino, devolver la capa original
        if crs_actual.authid() == crs_destino.authid():
            return capa, False  # Capa original, sin conversión
        
        print(f"🔄 Convirtiendo capa '{capa.name()}' de {crs_actual.authid()} a {crs_destino.authid()}")
        
        # Crear nombre para la capa convertida
        nombre_convertido = f"{capa.name()}_convertido"
        
        # Crear archivo temporal para la capa convertida
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"temp_{nombre_convertido}.shp")
        
        # Configurar opciones de transformación
        transform_context = QgsProject.instance().transformContext()
        transform = QgsCoordinateTransform(crs_actual, crs_destino, transform_context)
        
        # Crear campos para la nueva capa
        fields = capa.fields()
        
        # Determinar tipo de geometría
        geom_type = capa.wkbType()
        
        # Crear writer para la capa convertida
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = "UTF-8"
        
        writer = QgsVectorFileWriter.create(
            temp_path,
            fields,
            geom_type,
            crs_destino,
            transform_context,
            options
        )
        
        if writer.hasError():
            print(f"Error creando archivo temporal: {writer.errorMessage()}")
            return None, False
        
        # Copiar y transformar features
        features = capa.getFeatures()
        features_convertidas = 0
        
        for feature in features:
            new_feature = QgsFeature(fields)
            new_feature.setAttributes(feature.attributes())
            
            if feature.hasGeometry():
                geom = feature.geometry()
                geom.transform(transform)
                new_feature.setGeometry(geom)
            
            writer.addFeature(new_feature)
            features_convertidas += 1
        
        # Cerrar writer
        del writer
        
        print(f"✅ {features_convertidas} features convertidas a {crs_destino.authid()}")
        
        # Cargar la capa convertida
        capa_convertida = QgsVectorLayer(temp_path, nombre_convertido, "ogr")
        
        if capa_convertida.isValid():
            return capa_convertida, True  # Capa convertida, nueva
        else:
            print("❌ Error: La capa convertida no es válida")
            return None, False
            
    except Exception as e:
        print(f"Error en conversión de CRS: {str(e)}")
        return None, False

def cargar_shapefile_seguro(ruta, nombre, crs_destino=CRS_DEFAULT, convertir_automatico=True):
    """Función mejorada para cargar shapefiles con verificación de CRS"""
    try:
        if not os.path.exists(ruta):
            print(f"Archivo no existe: {ruta}")
            return None, False
            
        base_path = os.path.splitext(ruta)[0]
        archivos_necesarios = ['.shp', '.shx', '.dbf']
        for ext in archivos_necesarios:
            archivo_check = base_path + ext
            if not os.path.exists(archivo_check):
                print(f"Falta archivo complementario: {archivo_check}")
                return None, False
        
        lyr = QgsVectorLayer(ruta, nombre, "ogr")
        
        if not lyr.isValid():
            print(f"Capa inválida: {ruta} - Error: {lyr.error().message()}")
            return None, False
            
        print(f"Shapefile cargado exitosamente: {nombre}")
        print(f"CRS original: {lyr.crs().authid()}")
        
        # Verificar y convertir CRS si es necesario
        if convertir_automatico and lyr.crs().authid() != crs_destino.authid():
            lyr_convertida, fue_convertida = verificar_y_convertir_crs(lyr, crs_destino)
            if lyr_convertida and fue_convertida:
                return lyr_convertida, True  # Capa convertida
            else:
                print("⚠️ No se pudo convertir la capa, se usará la original")
                return lyr, False  
        else:
            return lyr, False 
        
    except Exception as e:
        print(f"Error crítico cargando shapefile {ruta}: {str(e)}")
        return None, False

class BuscarShapefileThread(QThread):
    progress_updated = pyqtSignal(int, str)
    file_found = pyqtSignal(str, str)
    finished_search = pyqtSignal(list)

    def __init__(self, carpeta_raiz, nombre_capa):
        super().__init__()
        self.carpeta_raiz = carpeta_raiz
        self.nombre_capa = nombre_capa
        self._is_cancelled = False

    def run(self):
        try:
            rutas_encontradas = []
            
            self.progress_updated.emit(0, "🔍 Buscando shapefiles...")
            
            shapefiles_encontrados = []
            for root, dirs, files in os.walk(self.carpeta_raiz):
                if self._is_cancelled:
                    break
                    
                for file in files:
                    if file.lower().endswith(".shp"):
                        nombre_archivo = os.path.splitext(file)[0]
                        if nombre_archivo.lower() == self.nombre_capa.lower():
                            ruta = os.path.join(root, file)
                            if self.validar_shapefile(ruta):
                                shapefiles_encontrados.append((ruta, nombre_archivo))
            
            if not shapefiles_encontrados:
                self.finished_search.emit([])
                return
            
            self.progress_updated.emit(10, f"📦 Encontrados {len(shapefiles_encontrados)} shapefiles")
            self.finished_search.emit(shapefiles_encontrados)
            
        except Exception as e:
            print(f"Error en el hilo de búsqueda: {e}")
            self.finished_search.emit([])

    def validar_shapefile(self, ruta):
        """Validar que el shapefile tiene todos los archivos necesarios"""
        try:
            base_path = os.path.splitext(ruta)[0]
            archivos_necesarios = ['.shp', '.shx', '.dbf']
            
            for ext in archivos_necesarios:
                archivo_check = base_path + ext
                if not os.path.exists(archivo_check):
                    return False
            return True
        except:
            return False

    def cancel(self):
        self._is_cancelled = True

class BuscarShapefileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Buscar Shapefile")
        
        self.setFixedWidth(600)
        self.setMinimumHeight(550)
        self.setMaximumHeight(550)
        self.setup_ui()
        self.aplicar_estilo()
        self.shapefiles_a_cargar = []

    def aplicar_estilo(self):
        """Estilo simple y funcional como el original"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #d0d7de;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                background-color: white;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 6px 14px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #cbd5e0;
                color: #64748b;
            }
            QPushButton#btn_buscar {
                background-color: #22c55e;
                color: black;
                font-size: 12px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton#btn_buscar:hover {
                background-color: #16a34a;
                color: black;
            }
            QPushButton#btn_cancelar {
                background-color: #ef4444;
                color: black;
            }
            QPushButton#btn_cancelar:hover {
                background-color: #dc2626;
                color: black;
            }
            QLineEdit {
                border: 1px solid #cbd5e0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
            /* COMBO BOX SIMPLIFICADO - */
            QComboBox {
                border: 1px solid #cbd5e0;
                border-radius: 4px;
                padding: 5px;
                font-size: 11px;
                background-color: transparent;
                min-height: 20px;
                selection-background-color: #e2e8f0;
                selection-color: black;  /* Color del texto cuando está seleccionado */
            }
            QComboBox:hover {
                border: 1px solid #3b82f6;
                background-color: rgba(59, 130, 246, 0.1);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #64748b;
                margin-right: 4px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #cbd5e0;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #e2e8f0;
                selection-color: black;  /* Color del texto en el menú desplegable */
                outline: none;
            }
            /* Para asegurar que el texto siempre sea visible */
            QComboBox::item:selected {
                color: black;
                background-color: #e2e8f0;
            }
            QCheckBox {
                spacing: 5px;
                font-size: 11px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #cbd5e0;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #22c55e;
                border: 1px solid #16a34a;
            }
            QProgressBar {
                border: 1px solid #cbd5e0;
                border-radius: 4px;
                text-align: center;
                height: 20px;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #22c55e;
                border-radius: 4px;
            }
            QLabel#ruta_label {
                background-color: #f8fafc;
                border: 1px solid #cbd5e0;
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
            }
            QLabel#estado_label {
                background-color: #fef9e7;
                border: 1px solid #f6e58d;
                border-radius: 4px;
                padding: 8px;
                color: #7d6608;
                font-size: 11px;
            }
        """)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # === TÍTULO PRINCIPAL ===
        titulo_principal = QLabel("🔍 BUSCADOR INTELIGENTE DE SHAPEFILES")
        titulo_principal.setAlignment(Qt.AlignCenter)
        titulo_principal.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            background-color: #e8f4f8;
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 5px;
        """)
        layout.addWidget(titulo_principal)

        # Subtítulo con versión/descripción
        subtitulo = QLabel("v1.0 - Busca y convierte automáticamente al CRS deseado")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("color: #7f8c8d; font-size: 10px; margin-bottom: 10px;")
        layout.addWidget(subtitulo)

        # Línea separadora
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setFrameShadow(QFrame.Sunken)
        linea.setStyleSheet("background-color: #bdc3c7; max-height: 1px;")
        layout.addWidget(linea)
        
        # ========== GRUPO CARPETA ==========
        grupo_carpeta = QGroupBox("📁 Carpeta de búsqueda")
        layout_carpeta = QVBoxLayout()
        layout_carpeta.setSpacing(6)
        
        self.carpeta_label = QLabel("📂 No se ha seleccionado carpeta")
        self.carpeta_label.setObjectName("ruta_label")
        self.carpeta_label.setMinimumHeight(30)
        
        self.btn_seleccionar_carpeta = QPushButton("📁 Examinar...")
        self.btn_seleccionar_carpeta.setMaximumWidth(120)
        self.btn_seleccionar_carpeta.setMinimumHeight(30)
        self.btn_seleccionar_carpeta.clicked.connect(self.seleccionar_carpeta)
        
        carpeta_container = QHBoxLayout()
        carpeta_container.addWidget(self.carpeta_label, 1)
        carpeta_container.addWidget(self.btn_seleccionar_carpeta)
        
        layout_carpeta.addLayout(carpeta_container)
        grupo_carpeta.setLayout(layout_carpeta)
        layout.addWidget(grupo_carpeta)

        # ========== GRUPO NOMBRE ==========
        grupo_nombre = QGroupBox("📄 Nombre del shapefile")
        layout_nombre = QVBoxLayout()
        layout_nombre.setSpacing(6)
        
        nombre_container = QHBoxLayout()
        nombre_container.addWidget(QLabel("🗺️"))
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("ej: calles, parcelas, rios...")
        self.nombre_input.setMinimumHeight(30)
        
        nombre_container.addWidget(self.nombre_input, 1)
        
        layout_nombre.addLayout(nombre_container)
        layout_nombre.addWidget(QLabel("💡 La búsqueda no distingue mayúsculas/minúsculas"))
        
        grupo_nombre.setLayout(layout_nombre)
        layout.addWidget(grupo_nombre)

        # ========== GRUPO CRS SIMPLE ==========
        grupo_crs = QGroupBox("🗺️ Sistema de Coordenadas (CRS)")
        layout_crs = QVBoxLayout()
        layout_crs.setSpacing(8)

        # Checkbox simple
        self.check_convertir = QCheckBox("✓ Convertir automáticamente al CRS destino")
        self.check_convertir.setChecked(True)
        layout_crs.addWidget(self.check_convertir)

        # Selector de CRS - SIMPLIFICADO
        crs_row = QHBoxLayout()
        crs_row.addWidget(QLabel("CRS Destino:"))
        
        self.crs_combo = QComboBox()
        self.crs_combo.addItem("EPSG:32617 - UTM zone 17N", "EPSG:32617")
        self.crs_combo.addItem("EPSG:4326 - WGS 84", "EPSG:4326")
        self.crs_combo.addItem("EPSG:3857 - Web Mercator", "EPSG:3857")
        self.crs_combo.addItem("Otro...", "custom")
        self.crs_combo.setMinimumHeight(28)
        self.crs_combo.setMaximumHeight(28)
        
        crs_row.addWidget(self.crs_combo, 1)
        layout_crs.addLayout(crs_row)

        # Campo personalizado
        self.custom_container = QHBoxLayout()
        self.custom_container.addSpacing(20)
        self.custom_container.addWidget(QLabel("Código EPSG:"))
        
        self.custom_crs_input = QLineEdit()
        self.custom_crs_input.setPlaceholderText("Ej: 32616")
        self.custom_crs_input.setEnabled(False)
        self.custom_crs_input.setMinimumHeight(28)
        self.custom_crs_input.setMaximumWidth(150)
        
        self.custom_container.addWidget(self.custom_crs_input)
        self.custom_container.addStretch()
        layout_crs.addLayout(self.custom_container)

        grupo_crs.setLayout(layout_crs)
        layout.addWidget(grupo_crs)

        # ========== CONTENEDOR DE PROGRESO  ==========
        
        self.progress_widget = QWidget()
        self.progress_widget.setFixedHeight(65)  # Altura reservada
        progress_layout = QVBoxLayout(self.progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(5)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        
        self.estado_label = QLabel("")
        self.estado_label.setObjectName("estado_label")
        self.estado_label.setVisible(False)
        self.estado_label.setWordWrap(True)
        self.estado_label.setMinimumHeight(40)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.estado_label)
        
        layout.addWidget(self.progress_widget)

        # ========== STRECH ELÁSTICO ==========
        # Esto protege los elementos superiores de la compresión
        layout.addStretch()

        # ========== BOTONES ==========
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)
        
        self.btn_buscar = QPushButton("🚀 BUSCAR Y CARGAR")
        self.btn_buscar.setObjectName("btn_buscar")
        self.btn_buscar.setEnabled(False)
        self.btn_buscar.setMinimumHeight(40)
        self.btn_buscar.setMinimumWidth(160)
        self.btn_buscar.clicked.connect(self.buscar_shapefiles)
        
        self.btn_cancelar = QPushButton("✖ CERRAR")
        self.btn_cancelar.setObjectName("btn_cancelar")
        self.btn_cancelar.setMinimumHeight(40)
        self.btn_cancelar.setMinimumWidth(140)
        self.btn_cancelar.clicked.connect(self.reject)
        
        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_buscar)
        botones_layout.addWidget(self.btn_cancelar)
        botones_layout.addStretch()
        
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)

        # Conectar señales
        self.nombre_input.textChanged.connect(self.validar_formulario)
        self.crs_combo.currentIndexChanged.connect(self.cambiar_crs_seleccion)
        self.carpeta_raiz = ""
        
    def cambiar_crs_seleccion(self, index):
        """Activar/desactivar campo de CRS personalizado"""
        es_personalizado = self.crs_combo.currentData() == "custom"
        self.custom_crs_input.setEnabled(es_personalizado)
        if es_personalizado:
            self.custom_crs_input.setFocus()

    def obtener_crs_destino(self):
        """Obtener el CRS seleccionado"""
        if self.crs_combo.currentData() == "custom":
            codigo = self.custom_crs_input.text().strip()
            if not codigo:
                return QgsCoordinateReferenceSystem("EPSG:32617")
            # Formatear código
            if codigo.isdigit():
                codigo = f"EPSG:{codigo}"
            elif not codigo.upper().startswith("EPSG:"):
                codigo = f"EPSG:{codigo}"
            
            crs = QgsCoordinateReferenceSystem(codigo)
            if crs.isValid():
                return crs
            else:
                QMessageBox.warning(self, "⚠️ Error", f"CRS {codigo} no válido. Usando EPSG:32617.")
                return QgsCoordinateReferenceSystem("EPSG:32617")
        else:
            return QgsCoordinateReferenceSystem(self.crs_combo.currentData())

    def seleccionar_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta")
        if carpeta:
            self.carpeta_raiz = carpeta
            nombre = os.path.basename(carpeta)
            self.carpeta_label.setText(f"📁 {nombre}")
            self.carpeta_label.setToolTip(carpeta)
            self.validar_formulario()

    def validar_formulario(self):
        habilitar = bool(self.carpeta_raiz and self.nombre_input.text().strip())
        self.btn_buscar.setEnabled(habilitar)

    def buscar_shapefiles(self):
        if not self.carpeta_raiz or not self.nombre_input.text().strip():
            return

        nombre_capa = self.nombre_input.text().strip()
        
        # Validar CRS personalizado
        if self.crs_combo.currentData() == "custom" and not self.custom_crs_input.text().strip():
            QMessageBox.warning(self, "⚠️ Error", "Ingresa un código EPSG para CRS personalizado")
            return

        crs_destino = self.obtener_crs_destino()
        convertir = self.check_convertir.isChecked()

        # Deshabilitar controles
        for widget in [self.btn_buscar, self.btn_seleccionar_carpeta, self.nombre_input,
                      self.crs_combo, self.check_convertir, self.custom_crs_input]:
            widget.setEnabled(False)
        
        self.progress_bar.setVisible(True)
        self.estado_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.estado_label.setText("🚀 Buscando shapefiles...")

        self.crs_destino = crs_destino
        self.convertir = convertir

        # Iniciar búsqueda
        self.thread = BuscarShapefileThread(self.carpeta_raiz, nombre_capa)
        self.thread.progress_updated.connect(self.actualizar_progreso)
        self.thread.finished_search.connect(self.procesar_shapefiles)
        self.thread.start()

    def actualizar_progreso(self, valor, mensaje):
        self.progress_bar.setValue(valor)
        self.estado_label.setText(mensaje)

    def procesar_shapefiles(self, shapefiles):
        if not shapefiles:
            self.busqueda_completada(0, [], [])
            return

        self.estado_label.setText(f"📦 Procesando {len(shapefiles)} shapefile(s)...")
        
        cargadas = 0
        convertidas = 0
        errores = []
        convertidas_nombres = []
        
        for i, (ruta, nombre) in enumerate(shapefiles):
            progreso = 10 + int((i / len(shapefiles)) * 85)
            self.progress_bar.setValue(progreso)
            self.estado_label.setText(f"📄 {nombre} ({i+1}/{len(shapefiles)})")
            
            self.repaint()
            QApplication.processEvents()
            
            # Cargar con conversión si está activada
            resultado = cargar_shapefile_seguro(
                ruta, nombre, 
                crs_destino=self.crs_destino,
                convertir_automatico=self.convertir
            )
            
            if resultado:
                capa, fue_convertida = resultado
                if capa:
                    QgsProject.instance().addMapLayer(capa)
                    cargadas += 1
                    if fue_convertida:
                        convertidas += 1
                        convertidas_nombres.append(nombre)
                else:
                    errores.append(nombre)
            else:
                errores.append(nombre)
        
        self.busqueda_completada(cargadas, errores, convertidas_nombres)

    def busqueda_completada(self, cargadas, errores, convertidas):
        self.progress_bar.setValue(100)
        
        # === OCULTAR ELEMENTOS DE PROGRESO ===
        self.progress_bar.setVisible(False)
        self.estado_label.setVisible(False)
        self.progress_bar.setValue(0)
        
        # Restaurar controles
        for widget in [self.btn_buscar, self.btn_seleccionar_carpeta, self.nombre_input,
                      self.crs_combo, self.check_convertir]:
            widget.setEnabled(True)
        self.custom_crs_input.setEnabled(self.crs_combo.currentData() == "custom")

        if cargadas == 0:
            self.estado_label.setText("❌ No se encontraron shapefiles")
            QMessageBox.information(self, "Resultado", 
                f"No se encontraron shapefiles '{self.nombre_input.text()}'")
        else:
            crs_text = f" a {self.crs_destino.authid()}" if self.convertir else ""
            self.estado_label.setText(f"✅ {cargadas} capa(s) cargada(s){crs_text}")
            
            mensaje = f"✅ {cargadas} shapefile(s) cargados correctamente."
            if convertidas:
                mensaje += f"\n\n🔄 {len(convertidas)} convertido(s) a {self.crs_destino.authid()}"
            if errores:
                mensaje += f"\n\n⚠️ {len(errores)} error(es)"
            
            QMessageBox.information(self, "✅ Completado", mensaje)

class BuscarShapefile:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
       
        self.plugin_dir = os.path.dirname(__file__)

    def initGui(self):
        
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        
        
        if os.path.exists(icon_path):
            from qgis.PyQt.QtGui import QIcon
            self.action = QAction(QIcon(icon_path), "🔍 Buscar Shapefile (con CRS)", self.iface.mainWindow())
        else:
            
            print(f"⚠️ Icono no encontrado en: {icon_path}")
            self.action = QAction("🔍 Buscar Shapefile (con CRS)", self.iface.mainWindow())
        
        self.action.setWhatsThis("Buscar shapefiles y convertirlos automáticamente al CRS deseado")
        self.action.setStatusTip("Busca shapefiles y los convierte automáticamente al CRS seleccionado")
        self.action.triggered.connect(self.run)
        
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("Buscar Shapefile", self.action)

    def unload(self):
        self.iface.removePluginMenu("Buscar Shapefile", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        dialog = BuscarShapefileDialog(self.iface.mainWindow())
        dialog.exec_()