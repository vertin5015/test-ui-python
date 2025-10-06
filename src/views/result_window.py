from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QApplication, QSizePolicy

class ResultWindow(QWidget):
    def __init__(self, controller, back_to_level_select):
        super().__init__()
        self.controller = controller
        self.back_to_level_select = back_to_level_select
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("成绩")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)

        self.label = QLabel("")
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label)

        btn_layout = QHBoxLayout()
        retry = QPushButton("继续做题")
        retry.clicked.connect(self.on_retry)
        exit_btn = QPushButton("退出程序")
        exit_btn.clicked.connect(self.on_exit)
        btn_layout.addWidget(retry)
        btn_layout.addWidget(exit_btn)
        self.layout.addLayout(btn_layout)

        self.layout.addStretch(1)
        self.setLayout(self.layout)
        self.setMinimumSize(420, 300)

    def show_result(self, result: dict):
        s = f"共 {result['total']} 题，答对 {result['correct']}。成绩：{result['score_pct']} %"
        self.label.setText(s)

    def on_retry(self):
        self.back_to_level_select()

    def on_exit(self):
        QApplication.quit()
