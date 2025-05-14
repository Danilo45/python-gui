import sys
import serial
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPlainTextEdit, QPushButton, QGridLayout, QLabel, QProgressBar
)
from PySide6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Senzor temperature, pritiska i vlaznosti vazduha")
        self.setFixedSize(1200, 800)

        # Kreiraj glavni widget i raspored
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        grid_layout = QGridLayout(main_widget)

        # Kreiraj QPlainTextEdit za terminal
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        grid_layout.addWidget(self.terminal, 0, 0, 1, 3)

        # Kreiraj QPushButton za pokretanje i zaustavljanje komunikacije
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        grid_layout.addWidget(self.start_button, 1, 0)
        grid_layout.addWidget(self.stop_button, 1, 1)

        # Kreiraj QLabel i QProgressBar za temperaturu
        self.temp_label = QLabel("Temperatura: (-40-60)")
        self.temp_progress = QProgressBar()
        self.temp_progress.setRange(-40, 60)  # Podesi opseg na osnovu očekivanih vrednosti temperature
        self.temp_value_label = QLabel("0 °C")
        grid_layout.addWidget(self.temp_label, 2, 0)
        grid_layout.addWidget(self.temp_progress, 2, 1)
        grid_layout.addWidget(self.temp_value_label, 2, 2)

        # Kreiraj QLabel i QProgressBar za pritisak
        self.pressure_label = QLabel("Pritisak: (900-1100)")
        self.pressure_progress = QProgressBar()
        self.pressure_progress.setRange(900, 1100)  # Podesi opseg na osnovu očekivanih vrednosti pritiska
        self.pressure_value_label = QLabel("0 hPa")
        grid_layout.addWidget(self.pressure_label, 3, 0)
        grid_layout.addWidget(self.pressure_progress, 3, 1)
        grid_layout.addWidget(self.pressure_value_label, 3, 2)

        # Kreiraj QLabel i QProgressBar za vlažnost
        self.humidity_label = QLabel("Vlažnost: (0-100%)")
        self.humidity_progress = QProgressBar()
        self.humidity_progress.setRange(0, 100)  # Podesi opseg na osnovu očekivanih vrednosti vlažnosti
        self.humidity_value_label = QLabel("0 %")
        grid_layout.addWidget(self.humidity_label, 4, 0)
        grid_layout.addWidget(self.humidity_progress, 4, 1)
        grid_layout.addWidget(self.humidity_value_label, 4, 2)

        # Postavi osnovne stilove
        self.temp_progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        self.pressure_progress.setStyleSheet("QProgressBar::chunk { background-color: lightgreen; }")
        self.humidity_progress.setStyleSheet("QProgressBar::chunk { background-color: lightblue; }")

        # Poveži dugmad sa metodama
        self.start_button.clicked.connect(self.start_communication)
        self.stop_button.clicked.connect(self.stop_communication)

        # Podesi serijski port i tajmer
        self.serial_port = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial_data)

        # Podesi matplotlib grafikon za prikaz
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax1 = self.figure.add_subplot(311)
        self.ax2 = self.figure.add_subplot(312)
        self.ax3 = self.figure.add_subplot(313)

        # Inicijalizuj skladištenje podataka za grafikon
        self.temp_data = []
        self.pressure_data = []
        self.humidity_data = []
        self.time_data = []

        grid_layout.addWidget(self.canvas, 5, 0, 1, 3)

    def start_communication(self):
        try:
            self.serial_port = serial.Serial('COM17', 115200, timeout=1)
            self.timer.start(1000)  # Proveri podatke svake sekunde
            self.terminal.appendPlainText("Serijska komunikacija pokrenuta.")
        except serial.SerialException as e:
            self.terminal.appendPlainText(f"Greška: {e}")

    def stop_communication(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.timer.stop()
            self.terminal.appendPlainText("Serijska komunikacija zaustavljena.")

    def read_serial_data(self):
        if self.serial_port and self.serial_port.in_waiting:
            data = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8')
            try:
                temp, pritisak, vlaznost = data.split(',')
                temp = float(temp)
                pritisak = float(pritisak)
                vlaznost = int(vlaznost)

                self.terminal.appendPlainText(f"Temperatura je {temp} °C")
                self.terminal.appendPlainText(f"Pritisak je {pritisak} hPa")
                self.terminal.appendPlainText(f"Vlažnost je {vlaznost} %")
                
                # Ažuriraj progres barove i vrednosti etiketa
                self.temp_progress.setValue(temp)
                self.pressure_progress.setValue(pritisak)
                self.humidity_progress.setValue(vlaznost)

                self.temp_value_label.setText(f"{temp:.1f} °C")
                self.pressure_value_label.setText(f"{pritisak:.1f} hPa")
                self.humidity_value_label.setText(f"{vlaznost} %")

                # Ažuriraj liste podataka za grafikon
                self.time_data.append(len(self.time_data))
                self.temp_data.append(temp)
                self.pressure_data.append(pritisak)
                self.humidity_data.append(vlaznost)

                # Ograniči liste podataka (npr. poslednjih 100 tačaka)
                if len(self.time_data) > 100:
                    self.time_data.pop(0)
                    self.temp_data.pop(0)
                    self.pressure_data.pop(0)
                    self.humidity_data.pop(0)

                # Ažuriraj grafikone
                self.update_plots()

            except ValueError:
                self.terminal.appendPlainText("Greška: Format podataka je neispravan.")

    def update_plots(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        self.ax1.plot(self.time_data, self.temp_data, 'r-', label="Temperatura (°C)")
        self.ax2.plot(self.time_data, self.pressure_data, 'b-', label="Pritisak (hPa)")
        self.ax3.plot(self.time_data, self.humidity_data, 'g-', label="Vlažnost (%)")

        self.ax1.set_ylabel("Temperatura (°C)")
        self.ax2.set_ylabel("Pritisak (hPa)")
        self.ax3.set_ylabel("Vlažnost (%)")
        self.ax3.set_xlabel("Vreme")

        self.ax1.legend()
        self.ax2.legend()
        self.ax3.legend()

        self.canvas.draw()
    
    def read_serial_data(self):
        if self.serial_port and self.serial_port.in_waiting:
            data = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8')
            try:
                temp, pritisak, vlaznost = data.split(',')
                temp = float(temp)
                pritisak = float(pritisak)
                vlaznost = int(vlaznost)

                self.terminal.appendPlainText(f"Temperatura je {temp} °C")
                self.terminal.appendPlainText(f"Pritisak je {pritisak} hPa")
                self.terminal.appendPlainText(f"Vlažnost je {vlaznost} %")
                
                # Ažuriraj progres barove i vrednosti etiketa
                self.temp_progress.setValue(temp)
                self.pressure_progress.setValue(pritisak)
                self.humidity_progress.setValue(vlaznost)

                self.temp_value_label.setText(f"{temp:.1f} °C")
                self.pressure_value_label.setText(f"{pritisak:.1f} hPa")
                self.humidity_value_label.setText(f"{vlaznost} %")

                # Proveri i ažuriraj boje progres barova na osnovu pragova
                if temp > 30:
                    self.temp_progress.setStyleSheet("QProgressBar::chunk { background-color: red; }")
                else:
                    self.temp_progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")

                if pritisak > 1020:
                    self.pressure_progress.setStyleSheet("QProgressBar::chunk { background-color: red; }")
                else:
                    self.pressure_progress.setStyleSheet("QProgressBar::chunk { background-color: lightgreen; }")

                if vlaznost > 70:
                    self.humidity_progress.setStyleSheet("QProgressBar::chunk { background-color: red; }")
                else:
                    self.humidity_progress.setStyleSheet("QProgressBar::chunk { background-color: lightblue; }")

                # Ažuriraj liste podataka za grafikon
                self.time_data.append(len(self.time_data))
                self.temp_data.append(temp)
                self.pressure_data.append(pritisak)
                self.humidity_data.append(vlaznost)

                # Ograniči liste podataka (npr. poslednjih 100 tačaka)
                if len(self.time_data) > 100:
                    self.time_data.pop(0)
                    self.temp_data.pop(0)
                    self.pressure_data.pop(0)
                    self.humidity_data.pop(0)

                # Ažuriraj grafikone
                self.update_plots()

            except ValueError:
                self.terminal.appendPlainText("Greška: Format podataka je neispravan.")

    def update_plots(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        self.ax1.plot(self.time_data, self.temp_data, 'r-', label="Temperatura (°C)")
        self.ax2.plot(self.time_data, self.pressure_data, 'b-', label="Pritisak (hPa)")
        self.ax3.plot(self.time_data, self.humidity_data, 'g-', label="Vlažnost (%)")

        self.ax1.set_ylabel("Temperatura (°C)")
        self.ax2.set_ylabel("Pritisak (hPa)")
        self.ax3.set_ylabel("Vlažnost (%)")
        self.ax3.set_xlabel("Vreme")

        self.ax1.legend()
        self.ax2.legend()
        self.ax3.legend()

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
