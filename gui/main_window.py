import cv2
from gui.styles import DARK_THEME
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox
)

from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import (
    Qt,
    QTimer,
    QObject,
    QThread,
    pyqtSignal
)

from camera.webcam import Webcam
from ai.gemini_client import GeminiClient
from evaluation.evaluator import Evaluator


class EvaluationWorker(QObject):

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, answer_key_data):
        super().__init__()

        self.answer_key_data = answer_key_data
        self.student_path = "student.jpg"

    def run(self):

        try:

            client = GeminiClient()

            # Extract ONLY student answers
            student_answers = client.extract_answers(
                self.student_path
            )

            evaluator = Evaluator()

            result = evaluator.evaluate(
                self.answer_key_data,
                student_answers
            )

            self.finished.emit(result)

        except Exception as e:

            self.error.emit(str(e))


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart AI MCQ Evaluation System")
        self.resize(1000, 700)

        # Path of uploaded answer key image
        self.answer_key = None

        # Extracted answer key JSON
        self.answer_key_data = None

        self.thread = None
        self.worker = None

        # Webcam
        self.webcam = Webcam()

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.setup_ui()
        self.setStyleSheet(DARK_THEME)

    def setup_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()

        # Upload Button
        self.upload_btn = QPushButton("Upload Answer Key")
        self.upload_btn.clicked.connect(self.upload_key)

        self.key_label = QLabel("Answer Key : Not Loaded")

        layout.addWidget(self.upload_btn)
        layout.addWidget(self.key_label)

        # Camera Preview
        self.camera_label = QLabel()

        self.camera_label.setFixedSize(800, 450)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("""
        border:2px solid #555;
        border-radius:10px;
        background-color:black;
    """)

        layout.addWidget(self.camera_label)

        # Buttons

        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start Camera")
        self.capture_btn = QPushButton("Capture")
        self.evaluate_btn = QPushButton("Evaluate")

        self.start_btn.clicked.connect(self.start_camera)
        self.capture_btn.clicked.connect(self.capture_image)
        self.evaluate_btn.clicked.connect(self.evaluate)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.capture_btn)
        button_layout.addWidget(self.evaluate_btn)

        layout.addLayout(button_layout)

        # Result

        self.score = QLabel("Score : -")
        self.correct = QLabel("Correct : -")
        self.wrong = QLabel("Wrong : -")
        self.status = QLabel("Status : Ready")

        layout.addWidget(self.score)
        layout.addWidget(self.correct)
        layout.addWidget(self.wrong)
        layout.addWidget(self.status)

        central.setLayout(layout)

    # ----------------------------
    # Upload Answer Key
    # ----------------------------

    def upload_key(self):

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Answer Key",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if not file:
            return

        self.status.setText("Status : Reading Answer Key...")

        try:

            client = GeminiClient()

            self.answer_key_data = client.extract_answers(file)

            self.answer_key = file

            self.key_label.setText("Answer Key : Loaded Successfully")

            self.status.setText("Status : Answer Key Ready")

            print(self.answer_key_data)

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

            self.status.setText("Status : Failed")

    # ----------------------------
    # Start Camera
    # ----------------------------

    def start_camera(self):

        try:

            self.webcam.start()

            self.timer.start(30)

            self.status.setText("Status : Camera Started")

        except Exception as e:

            self.status.setText(str(e))

    # ----------------------------
    # Update Camera Frame
    # ----------------------------

    def update_frame(self):

        frame = self.webcam.read()

        if frame is None:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = frame.shape

        image = QImage(
            frame.data,
            w,
            h,
            ch * w,
            QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        self.camera_label.setPixmap(
            pixmap.scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio
            )
        )

    # ----------------------------
    # Capture Image
    # ----------------------------

    def capture_image(self):

        filename = self.webcam.capture("student.jpg")

        self.status.setText(f"Captured : {filename}")

    # ----------------------------
    # Evaluate
    # ----------------------------

    def evaluate(self):

        if self.answer_key_data is None:

            QMessageBox.warning(
                self,
                "Error",
                "Please upload answer key first."
            )

            return

        self.status.setText("Status : Evaluating...")

        self.evaluate_btn.setEnabled(False)

        self.thread = QThread()

        self.worker = EvaluationWorker(
            self.answer_key_data
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.finished.connect(
            self.show_result
        )

        self.worker.error.connect(
            self.show_error
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.error.connect(
            self.thread.quit
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.start()

    # ----------------------------
    # Show Result
    # ----------------------------

    def show_result(self, result):

        self.score.setText(
            f"Score : {result['score']} / {result['total_questions']}"
        )

        self.correct.setText(
            f"Correct : {result['correct']}"
        )

        self.wrong.setText(
            f"Wrong : {result['wrong']}"
        )

        self.status.setText(
            f"Completed ({result['percentage']}%)"
        )

        self.evaluate_btn.setEnabled(True)

    # ----------------------------
    # Show Error
    # ----------------------------

    def show_error(self, message):

        QMessageBox.critical(
            self,
            "Evaluation Error",
            message
        )

        self.status.setText("Status : Failed")

        self.evaluate_btn.setEnabled(True)

    # ----------------------------
    # Close Window
    # ----------------------------

    def closeEvent(self, event):

        self.timer.stop()

        self.webcam.stop()

        event.accept()