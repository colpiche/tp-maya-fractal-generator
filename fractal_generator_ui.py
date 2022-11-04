from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QSlider,
    QCheckBox,
    QPushButton,
    QMessageBox
)

import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2.QtWidgets import QWidget

import sys

import fractal_generator_project.fractal_generator_api as api
import imp
imp.reload(api)

# A modifier pour éviter les erreurs lors de l'import du module api
PROJECT_PATH = r"D:\DOCUMENTS\Cours ENJMIN\2022-09_Scripting Python pour animation"
SIZE_SLIDER_DEFAULT_VALUE = 10
GENERATIONS_SLIDER_DEFAULT_VALUE = 2


if PROJECT_PATH not in sys.path:
    sys.path.append(PROJECT_PATH)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)


class FractalUI(QDialog):
    def __init__(self):
        super(FractalUI, self).__init__(parent=maya_main_window())

        # Layouts
        self.main_layout = None
        self.size_slider_layout = None
        self.generations_slider_layout = None

        # Widgets
        self.fractal_list = None
        self.size_label = None
        self.size_slider = None
        self.size_value_label = None
        self.generations_label = None
        self.generations_slider = None
        self.generations_value_label = None
        self.colorize_generations_checkbox = None
        self.generate_button = None
        self.clear_button = None
        self.too_many_generations_warning_box = None
        self.we_told_you_box = None

    def init_ui(self):
        self.setWindowTitle("Fractal generator")
        self.init_layouts()
        self.init_widgets()
        self.set_layouts()
        self.set_connections()
        self.set_default()

    def init_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.size_slider_layout = QHBoxLayout(self)
        self.generations_slider_layout = QHBoxLayout(self)

    def init_widgets(self):
        self.fractal_list = QComboBox()
        self.size_label = QLabel("Size")
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_value_label = QLabel(str(SIZE_SLIDER_DEFAULT_VALUE))
        self.generations_label = QLabel("Generations")
        self.generations_slider = QSlider(Qt.Horizontal)
        self.generations_value_label = QLabel(str(GENERATIONS_SLIDER_DEFAULT_VALUE))
        self.colorize_generations_checkbox = QCheckBox("Randomly colorize generations")
        self.generate_button = QPushButton("Generate !")
        self.clear_button = QPushButton("Clear viewport")
        self.too_many_generations_warning_box = QMessageBox()
        self.we_told_you_box = QMessageBox()

    def set_layouts(self):
        self.main_layout.addWidget(self.fractal_list)
        self.main_layout.addLayout(self.size_slider_layout)
        self.main_layout.addLayout(self.generations_slider_layout)
        self.main_layout.addWidget(self.colorize_generations_checkbox)
        self.main_layout.addWidget(self.generate_button)
        self.main_layout.addWidget(self.clear_button)
        self.size_slider_layout.addWidget(self.size_label)
        self.size_slider_layout.addWidget(self.size_slider)
        self.size_slider_layout.addWidget(self.size_value_label)
        self.generations_slider_layout.addWidget(self.generations_label)
        self.generations_slider_layout.addWidget(self.generations_slider)
        self.generations_slider_layout.addWidget(self.generations_value_label)

    def set_connections(self):
        self.fractal_list.activated.connect(self.fractal_list_activated)
        self.size_slider.valueChanged.connect(self.update_size_value_label)
        self.generations_slider.valueChanged.connect(self.update_generations_value_label)
        self.generate_button.clicked.connect(self.generate_button_clicked)
        self.clear_button.clicked.connect(self.clear_viewport)
        self.too_many_generations_warning_box.buttonClicked.connect(
            self.too_many_generations_warning_box_button_clicked
        )
        self.we_told_you_box.buttonClicked.connect(self.we_told_you_box_button_clicked)

    def set_default(self):
        self.main_layout.setAlignment(Qt.AlignTop)
        self.size_slider.setMinimum(5)
        self.size_slider.setMaximum(20)
        self.size_slider.setValue(SIZE_SLIDER_DEFAULT_VALUE)
        self.generations_slider.setMinimum(1)
        self.generations_slider.setMaximum(10)
        self.generations_slider.setValue(GENERATIONS_SLIDER_DEFAULT_VALUE)
        self.fractal_list.addItems(api.FRACTAL_TYPES)
        self.too_many_generations_warning_box.setWindowTitle("Alert")
        self.too_many_generations_warning_box.setIcon(QMessageBox.Warning)
        self.too_many_generations_warning_box.setText(
            "Generating fractals with a large number a generations needs a\
            lot of memory and can lead to computer destruction.\
            Are you sure you want to continue ?"
        )
        self.too_many_generations_warning_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        self.too_many_generations_warning_box.setDefaultButton(QMessageBox.Cancel)
        self.we_told_you_box.setWindowTitle("Hey !")
        self.we_told_you_box.setIcon(QMessageBox.Critical)
        self.we_told_you_box.setText("Alright, we told you so.")
        self.we_told_you_box.setStandardButtons(QMessageBox.Ignore)

    def show(self):
        self.init_ui()
        return super(FractalUI, self).show()

    def fractal_list_activated(self):
        if self.fractal_list.currentIndex() == 0:
            self.colorize_generations_checkbox.show()
        else:
            self.colorize_generations_checkbox.hide()

    def update_size_value_label(self):
        self.size_value_label.setText(str(self.size_slider.value()))

    def update_generations_value_label(self):
        self.generations_value_label.setText(str(self.generations_slider.value()))

    def generate_button_clicked(self):
        if (
            (self.fractal_list.currentIndex() == 0 and self.generations_slider.value() > 5) or
            (self.fractal_list.currentIndex() == 1 and self.generations_slider.value() > 3) or
            (self.fractal_list.currentIndex() == 2 and self.generations_slider.value() > 6)
        ):
            self.too_many_generations_warning_box.exec_()
            return
        else:
            self.generate_fractal()

    def generate_fractal(self):
        if self.colorize_generations_checkbox.isChecked() == 1:
            color_list = api.generate_random_colors_list(self.generations_slider.value())
            api.generate_fractal(
                self.fractal_list.currentText(),
                self.size_slider.value(),
                self.generations_slider.value(),
                True,
                color_list
            )
        else:
            api.generate_fractal(
                self.fractal_list.currentText(),
                self.size_slider.value(),
                self.generations_slider.value()
            )

    def clear_viewport(self):
        api.clear_viewport()

    def too_many_generations_warning_box_button_clicked(self, button):
        if button.text() == "&Yes":
            self.too_many_generations_warning_box.hide()
            self.we_told_you_box.exec_()
        else:
            return

    def we_told_you_box_button_clicked(self):
        self.generate_fractal()


if __name__ == '__main__':
    if "fractal_ui" in globals():
        globals()["fractal_ui"].deleteLater()
    fractal_ui = FractalUI()
    fractal_ui.show()
