# Tarea 1. HMI for signal processing

# Importar librerias
import sys
import os # Libreria de funcionalidades del sistema operativo
import librosa # Libreria para extraer audio
import numpy as np # Libreria para realizar calculos y manejar grandes volumenes de datos
import pyqtgraph as pg # Libreria para graficar seniales
import soundfile as sf # Libreria para exportar seniales
from scipy.signal import butter, filtfilt # Libreria para realizar los filtros
from pydub import AudioSegment # Libreria para generar archivo .mp3
from PyQt5.QtCore import Qt # Libreria de la interfaz
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QLabel, QComboBox, QSlider

class ventanaTarea(QMainWindow):
    def __init__(self):
        super().__init__()

        # Declarar variables
        self.audio_file = None
        self.audio_data = None
        self.sr = None
        self.cindex = None
        self.transform_flag = None
        self.tindex = None

        # Declarar elementos graficos (botones, sliders, menu desplegable, labels y graficos)
        self.setWindowTitle("Procesamiento de Señal")
        self.label = QLabel("Sube tu archivo de audio aquí:")

        self.button = QPushButton("Cargar Archivo", self)
        self.button.setGeometry(100, 80, 100, 30)
        self.button.clicked.connect(self.load_audio)

        self.label_originalS = QLabel("Señal Original:")
        self.label_space = QLabel(" ")
        self.label_transform = QLabel("Presiona aplicar la Transformada de Fourier:")

        self.button_transform = QPushButton("Aplicar Transformada de Fourier", self)
        self.button_transform.setGeometry(100, 80, 100, 30)
        self.button_transform.clicked.connect(self.first_transform)

        self.original_signal = pg.PlotWidget()
        self.original_transform = pg.PlotWidget()

        self.label_filtro = QLabel("Selecciona el filtro a poner:")

        self.select_filter = QComboBox()
        self.select_filter.addItems(['Filtro Pasa-Bajas', 'Filtro Pasa-Altas', 'Filtro Pasa-Banda'])
        self.select_filter.activated.connect(self.check_index)

        self.label_cutoff = QLabel("Selecciona la Frecuencia de Corte (si el filtro es Pasa-Banda, esta será la frecuencia de corte alta):")
        self.slider_cutoff = QSlider()
        self.slider_cutoff.setOrientation(Qt.Horizontal)
        self.slider_cutoff.setRange(20, 20000)
        self.slider_cutoff.setValue(1000)
        self.slider_cutoff.valueChanged.connect(self.update_cutoff)
        self.cutoffvalue_label = QLabel(f"{self.slider_cutoff.value()} Hz")

        self.label_cutoff_low = QLabel("Selecciona la frecuencia baja del filtro Pasa-Banda")
        self.slider_cutoff_low = QSlider()
        self.slider_cutoff_low.setOrientation(Qt.Horizontal)
        self.slider_cutoff_low.setRange(20, 20000)
        self.slider_cutoff_low.setValue(500)
        self.slider_cutoff_low.valueChanged.connect(self.update_cutoff_low)
        self.cutoffLOWvalue_label = QLabel(f"{self.slider_cutoff_low.value()} Hz")

        self.label_order = QLabel("Selecciona el Orden del Filtro:")
        self.slider_order = QSlider()
        self.slider_order.setOrientation(Qt.Horizontal)
        self.slider_order.setRange(1, 10)
        self.slider_order.setValue(5)
        self.slider_order.valueChanged.connect(self.update_order)
        self.ordervalue_label = QLabel(f"{self.slider_order.value()}")

        self.button_apply = QPushButton("Aplicar Filtro", self)
        self.button_apply.setGeometry(100, 80, 100, 30)
        self.button_apply.clicked.connect(self.apply_filters)

        self.button_filteredtransform = QPushButton("Aplicar Transformada de Fourier", self)
        self.button_filteredtransform.setGeometry(100, 80, 100, 30)
        self.button_filteredtransform.clicked.connect(self.second_transform)

        self.label_resultado = QLabel("Tu audio filtrado:")
        self.label_resultado_transform = QLabel("La Transformada de Fourier con el audio filtrado:")

        self.filtered_signal = pg.PlotWidget()
        self.filtered_transform = pg.PlotWidget()

        self.save_label = QLabel("Para salvar el audio resultante seleccione el tipo de archivo de salida y presione guardar")

        self.select_type = QComboBox()
        self.select_type.addItems(['.wav', '.mp3'])
        self.select_type.activated.connect(self.check_option)

        self.button_save = QPushButton("Guardar Resultado", self)
        self.button_save.setGeometry(100, 80, 100, 30)
        self.button_save.clicked.connect(self.save_archive)

        # Declarar layout y aniadir elementos a la venta principal
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)
        self.transform_layout = QHBoxLayout()
        self.layout.addLayout(self.transform_layout)
        self.transform_layout.addWidget(self.label_originalS)
        self.transform_layout.addWidget(self.label_space)
        self.transform_layout.addWidget(self.label_transform)
        self.transform_layout.addWidget(self.button_transform)
        self.original_layout = QHBoxLayout()
        self.layout.addLayout(self.original_layout)
        self.original_layout.addWidget(self.original_signal)
        self.original_layout.addWidget(self.original_transform)
        self.layout.addWidget(self.label_filtro)
        self.filtOption_layout = QHBoxLayout()
        self.layout.addLayout(self.filtOption_layout)
        self.filtOption_layout.addWidget(self.select_filter)
        self.filtOption_layout.addWidget(self.button_apply)
        self.filtOption_layout.addWidget(self.button_filteredtransform)
        self.cutofflayout = QHBoxLayout()
        self.layout.addLayout(self.cutofflayout)
        self.cutofflayout.addWidget(self.label_cutoff)
        self.cutofflayout.addWidget(self.cutoffvalue_label)
        self.layout.addWidget(self.slider_cutoff)
        self.cutoffLOWlayout = QHBoxLayout()
        self.layout.addLayout(self.cutoffLOWlayout)
        self.cutoffLOWlayout.addWidget(self.label_cutoff_low)
        self.cutoffLOWlayout.addWidget(self.cutoffLOWvalue_label)
        self.layout.addWidget(self.slider_cutoff_low)
        '''Ocultar elementos para que solo aparezcan con la seleccion del filtro PasaBanda'''
        self.label_cutoff_low.hide()
        self.cutoffLOWvalue_label.hide()
        self.slider_cutoff_low.hide()

        self.orderlayout = QHBoxLayout()
        self.layout.addLayout(self.orderlayout)
        self.orderlayout.addWidget(self.label_order)
        self.orderlayout.addWidget(self.ordervalue_label)
        self.layout.addWidget(self.slider_order)
        self.filtresult_layout = QHBoxLayout()
        self.layout.addLayout(self.filtresult_layout)
        self.filtresult_layout.addWidget(self.label_resultado)
        self.filtresult_layout.addWidget(self.label_resultado_transform)
        self.filtered_layout = QHBoxLayout()
        self.layout.addLayout(self.filtered_layout)
        self.filtered_layout.addWidget(self.filtered_signal)
        self.filtered_layout.addWidget(self.filtered_transform)
        self.savelayout = QHBoxLayout()
        self.layout.addLayout(self.savelayout)
        self.savelayout.addWidget(self.save_label)
        self.savelayout.addWidget(self.select_type)
        self.savelayout.addWidget(self.button_save)

        # Declarar contenedor de la pagina
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def load_audio(self): # Funcion de carga de audio
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo de Audio", "", "Archivos de Audio (*.wav *.mp3)")
        if file_name:
            self.audio_file = file_name
            print(f"Archivo de audio subido correctamente: {file_name}")
            self.audio_procesado(file_name)

    def audio_procesado(self, file_name): # Funcion de procesamiento de audio
        self.audio_data, self.sr = librosa.load(file_name, sr=None)
        time = np.linspace(0, len(self.audio_data) / self.sr, num=len(self.audio_data))
        self.original_signal.plot(time, self.audio_data, pen='b')

    def first_transform(self): # Apagar bandera de transformada para seleccion de senial a transformar
        self.transform_flag = 0
        self.fourier_transform()

    def second_transform(self): # Encender bandera de transformada para seleccion de senial a transformar
        self.transform_flag = 1
        self.fourier_transform()

    def fourier_transform(self): # Funcion de transformada de fourier
        if self.transform_flag == 0:
            self.original_transform.clear()
            # transformada de Fourier de la señal original
            print("Aplicando Transformada de Fourier a la señal original")
            yf = np.fft.fft(self.audio_data)
            xf = np.fft.fftfreq(len(self.audio_data), 1 / self.sr)
            self.original_transform.plot(xf, np.abs(yf), pen='b')
        elif self.transform_flag == 1:
            self.filtered_transform.clear()
            # transformada de Fourier de la señal filtrada
            print("Aplicando Transformada de Fourier a la señal filtrada")
            if hasattr(self, 'y_filtered'):
                yf = np.fft.fft(self.y_filtered)
                xf = np.fft.fftfreq(len(self.y_filtered), 1 / self.sr)
                self.filtered_transform.plot(xf, np.abs(yf), pen='r')
            else:
                print("No se ha aplicado ningún filtro a la señal aún.")

    def check_index(self): # Identificar indice de seleccion de filtro
        self.cindex = self.select_filter.currentIndex()
        if self.cindex == 2:
            self.label_cutoff_low.show()
            self.cutoffLOWvalue_label.show()
            self.slider_cutoff_low.show()
        else:
            self.label_cutoff_low.hide()
            self.cutoffLOWvalue_label.hide()
            self.slider_cutoff_low.hide()

    def update_cutoff(self): # Imprimir valor del filtro
        self.cutoffvalue_label.setText(f"{self.slider_cutoff.value()}")

    def update_cutoff_low(self):
        self.cutoffLOWvalue_label.setText(f"{self.slider_cutoff_low.value()}")

    def update_order(self): # Imprimir valor de ordenada
        self.ordervalue_label.setText(f"{self.slider_order.value()}")

    def apply_filters(self): # Identificacion de filtro a usar dependiendo de la seleccion
        cutoff = self.slider_cutoff.value()
        lowcutoff = self.slider_cutoff_low.value()
        order = self.slider_order.value()
        if self.cindex == 0:
            self.pasaBajas_filter(cutoff, order)
            print(f"Seleccion {self.cindex} -> Filtro Pasa-Bajas seleccionado ")
        elif self.cindex == 1:
            self.pasaAltas_filter(cutoff, order)
            print(f"Seleccion {self.cindex} -> Filtro Pasa-Altas seleccionado ")
        elif self.cindex == 2:
            self.pasaBandas_filter(cutoff, lowcutoff, order)
            print(f"Seleccion {self.cindex} -> Filtro Pasa-Banda seleccionado ")
        else:
            print(f"Seleccion invalida -> Index: {self.cindex}")


    def pasaBajas_filter(self, cutoff, order): # Funcion filtro pasa-bajas
        if self.audio_data is not None and self.sr is not None:
            self.filtered_signal.clear()
            nyquist = 0.5 * self.sr
            normal_cutoff = cutoff / nyquist
            b, a = butter(order, normal_cutoff, btype='low', analog=False)
            self.y_filtered = filtfilt(b, a, self.audio_data)
            time = np.linspace(0, len(self.audio_data) / self.sr, num=len(self.audio_data))
            self.filtered_signal.plot(time, self.y_filtered, pen='r', name='Filtrada Pasa-Bajas')

    def pasaAltas_filter(self, cutoff, order): # Funcion filtro pasa-altas
        if self.audio_data is not None and self.sr is not None:
            self.filtered_signal.clear()
            nyquist = 0.5 * self.sr
            normal_cutoff = cutoff / nyquist
            b, a = butter(order, normal_cutoff, btype='high', analog=False)
            self.y_filtered = filtfilt(b, a, self.audio_data)
            time = np.linspace(0, len(self.audio_data) / self.sr, num=len(self.audio_data))
            self.filtered_signal.plot(time, self.y_filtered, pen='g', name='Filtrada Pasa-Altas')

    def pasaBandas_filter(self, cutoff, lowcutoff, order): # Funcion filtro pasa-bandas
        if self.audio_data is not None and self.sr is not None:
            self.filtered_signal.clear()
            nyquist = 0.5 * self.sr
            low_cutoff = lowcutoff / nyquist
            high_cutoff = cutoff / nyquist
            b, a = butter(order, [low_cutoff, high_cutoff], btype='band', analog=False)
            self.y_filtered = filtfilt(b, a, self.audio_data)
            time = np.linspace(0, len(self.audio_data) / self.sr, num=len(self.audio_data))
            self.filtered_signal.plot(time, self.y_filtered, pen='m', name='Filtrada Pasa-Banda')

    def check_option(self): # Identificar indice de seleccion de tipo de archivo
        self.tindex = self.select_type.currentIndex()

    def save_archive(self): # Exportar archivos wav y mp3
        print("Salvando archivo...")
        if self.tindex == 0:
            print("Creando .wav...")
            if hasattr(self, 'y_filtered'):
                filename = "filtered.wav"
                if self.cindex == 0:
                    filename = "pasaBajas_audio.wav"
                elif self.cindex == 1:
                    filename = "pasaAltas_audio.wav"
                elif self.cindex == 2:
                    filename = "pasaBandas_audio.wav"
                else:
                    filename = "filtered_audio.wav"
                sf.write(filename, self.y_filtered, self.sr)
                print(f"Archivo {filename} exportado correctamente.")
            else:
                print("No hay señal filtrada para exportar.")
        elif self.tindex == 1:
            print("Creando .mp3...")
            if hasattr(self, 'y_filtered'):
                temp_archive = "temp.wav"
                sf.write(temp_archive, self.y_filtered, self.sr)
                audio = AudioSegment.from_wav(temp_archive)
                filename = "filtered.mp3"
                if self.cindex == 0:
                    filename = "pasaBajas_audio.mp3"
                elif self.cindex == 1:
                    filename = "pasaAltas_audio.mp3"
                elif self.cindex == 2:
                    filename = "pasaBandas_audio.mp3"
                else:
                    filename = "filtered_audio.mp3"
                audio.export(filename, format="mp3")
                print(f"Archivo {filename} exportado correctamente")
                os.remove(temp_archive)
            else: 
                print("No hay señal filtrada para exportar.")
        else:
            print(f"Seleccion invalida -> Index: {self.tindex}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ventanaTarea()
    window.show()
    sys.exit(app.exec_())
