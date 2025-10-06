from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QRadioButton, QPushButton, QMessageBox, QHBoxLayout, QScrollArea, QSizePolicy, QButtonGroup

class QuizWindow(QWidget):
    def __init__(self, controller, show_result_callback):
        super().__init__()
        self.controller = controller
        self.show_result_callback = show_result_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("答题")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)

        self.stem_label = QLabel("")
        self.stem_label.setWordWrap(True)
        self.layout.addWidget(self.stem_label)

        self.options_scroll = QScrollArea()
        self.options_scroll.setWidgetResizable(True)
        options_container = QWidget()
        self.options_layout = QVBoxLayout(options_container)
        self.option_group = QButtonGroup()
        self.option_buttons = []

        for i in range(4):
            rb = QRadioButton()
            self.option_group.addButton(rb, i)
            self.options_layout.addWidget(rb)
            self.option_buttons.append(rb)
        self.options_layout.addStretch(1)
        self.options_scroll.setWidget(options_container)
        self.layout.addWidget(self.options_scroll)

        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("上一题")
        self.prev_btn.clicked.connect(self.on_prev)
        self.next_btn = QPushButton("下一题")
        self.next_btn.clicked.connect(self.on_next)
        self.submit_btn = QPushButton("交卷")
        self.submit_btn.clicked.connect(self.on_submit)
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.next_btn)
        btn_layout.addWidget(self.submit_btn)
        self.layout.addLayout(btn_layout)
        self.layout.addStretch(1)
        self.setLayout(self.layout)
        self.setMinimumSize(500, 380)

    def load_question(self, index):
        q = self.controller.current_paper[index]
        self.stem_label.setText(f"第 {index + 1} 题: {q['stem']}")
        # 填充选项文本并确保清空旧选择（临时关闭 exclusive）
        was_exclusive = self.option_group.exclusive()
        self.option_group.setExclusive(False)
        for i, opt in enumerate(q['options']):
            self.option_buttons[i].setText(opt)
            self.option_buttons[i].setChecked(False)
        self.option_group.setExclusive(was_exclusive)

        sel = self.controller.current_answers[index]
        if sel is not None and sel >= 0:
            b = self.option_group.button(sel)
            if b:
                b.setChecked(True)

        # 更新导航按钮可用状态
        total = len(self.controller.current_paper)
        if hasattr(self, 'prev_btn'):
            self.prev_btn.setEnabled(index > 0)
        if hasattr(self, 'next_btn'):
            self.next_btn.setEnabled(index < total - 1)

    def on_next(self):
        idx = self.controller.current_index
        sel = self.option_group.checkedId()
        if sel is not None and sel != -1:
            self.controller.submit_answer(idx, sel)

        if self.controller.next_question():
            self.load_question(self.controller.current_index)
        else:
            QMessageBox.information(self, "提示", "已经是最后一题")

    def on_prev(self):
        idx = self.controller.current_index
        sel = self.option_group.checkedId()
        if sel is not None and sel != -1:
            self.controller.submit_answer(idx, sel)

        if self.controller.prev_question():
            self.load_question(self.controller.current_index)
        else:
            QMessageBox.information(self, "提示", "已经是第一题")

    def on_submit(self):
        idx = self.controller.current_index
        sel = self.option_group.checkedId()
        if sel is not None and sel != -1:
            self.controller.submit_answer(idx, sel)
        result = self.controller.finish_quiz_and_score()
        self.show_result_callback(result)
