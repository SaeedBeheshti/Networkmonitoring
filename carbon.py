import sys
import psutil
import time
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class NetworkCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6,4))
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Network Usage (Bytes/s)")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Bytes/s")
        self.ax.grid(True)
        self.time_data = []
        self.download_data = []
        self.upload_data = []

    def update_plot(self, download, upload):
        self.time_data.append(time.strftime("%H:%M:%S"))
        self.download_data.append(download)
        self.upload_data.append(upload)
        # فقط آخر 20 نقطه رو نگه دار
        self.time_data = self.time_data[-20:]
        self.download_data = self.download_data[-20:]
        self.upload_data = self.upload_data[-20:]

        self.ax.clear()
        self.ax.plot(self.time_data, self.download_data, label="Download", color="blue")
        self.ax.plot(self.time_data, self.upload_data, label="Upload", color="red")
        self.ax.set_title("Network Usage (Bytes/s)")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Bytes/s")
        self.ax.legend()
        self.ax.grid(True)
        self.draw()

class NetworkMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Monitor")
        self.resize(700, 500)

        self.canvas = NetworkCanvas(self)
        self.label = QLabel("Monitoring...", self)
        self.start_btn = QPushButton("Start Monitoring")
        self.start_btn.clicked.connect(self.start_monitoring)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.label)
        layout.addWidget(self.start_btn)
        self.setLayout(layout)

        self.monitoring = False

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.start_btn.setText("Monitoring...")
            thread = threading.Thread(target=self.monitor_network, daemon=True)
            thread.start()

    def monitor_network(self):
        old = psutil.net_io_counters()
        while self.monitoring:
            time.sleep(1)
            new = psutil.net_io_counters()
            download_speed = new.bytes_recv - old.bytes_recv
            upload_speed = new.bytes_sent - old.bytes_sent
            old = new
            self.canvas.update_plot(download_speed, upload_speed)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NetworkMonitor()
    window.show()
    sys.exit(app.exec_())
