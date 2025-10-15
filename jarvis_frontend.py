import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from jarvis2 import jarvis_backend, listen_for_command

class VoiceThread(QThread):
    response_signal = pyqtSignal(str)

    def run(self):
        # Call the backend voice listener
        response = listen_for_command()
        self.response_signal.emit(response)

class JarvisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis AI Assistant")
        self.setGeometry(200, 200, 500, 600)

        layout = QVBoxLayout()

        # Status label
        self.label = QLabel("Jarvis is ready!")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Response display
        self.response_box = QTextEdit()
        self.response_box.setReadOnly(True)
        layout.addWidget(self.response_box)

        # Start listening button
        self.listen_button = QPushButton("🎤 Start Listening")
        self.listen_button.clicked.connect(self.start_listening)
        layout.addWidget(self.listen_button)

        # Exit button
        self.stop_button = QPushButton("❌ Exit")
        self.stop_button.clicked.connect(self.close_app)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)
        self.voice_thread = None

    def start_listening(self):
        """Start voice recognition in a separate thread."""
        self.label.setText("Listening...")
        self.voice_thread = VoiceThread()
        self.voice_thread.response_signal.connect(self.show_response)
        self.voice_thread.start()

    def show_response(self, response):
        """Show Jarvis's response in the UI."""
        self.label.setText("Jarvis is ready!")
        self.response_box.append(f"Jarvis: {response}")

    def close_app(self):
        """Close the app safely."""
        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.terminate()  # Stop the voice thread if running
        self.close()

def run_gui():
    app = QApplication(sys.argv)
    jarvis = JarvisApp()
    jarvis.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_gui()
