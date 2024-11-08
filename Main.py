from matplotlib.widgets import Slider
from pyqtgraph import canvas
import os
import warnings
import requests
import numpy as np
import pyedflib
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRect, QSize, Qt, QCoreApplication, QMetaObject
from PyQt5.QtGui import QCursor
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QColorDialog, QSlider, QComboBox
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.interpolate import interpolate
from scipy.interpolate import PchipInterpolator
from scipy.interpolate import CubicSpline
from scipy.interpolate import splrep
from scipy.signal import butter, filtfilt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

warnings.filterwarnings("ignore", category=DeprecationWarning)


class ReplaceSignalDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Disable maximize button
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowTitleHint)

        # Set background color and border
        self.setStyleSheet("""
            background-color: rgb(184, 184,184);  /* Background color */
            border: 1px solid rgb(36,36,36);  /* Border size and color */
            color:white;
        """)

        font = QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(17)

        # Label for instruction
        self.label = QLabel(self)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(10, 30, 261, 91))
        label_font = QFont()
        label_font.setFamily("Times New Roman")
        label_font.setPointSize(24)
        self.label.setFont(label_font)

        # Graph 1 button
        self.load_file_button = QPushButton(self)
        self.load_file_button.setObjectName("load_file_button")
        self.load_file_button.setGeometry(QRect(65, 150, 150, 40))
        self.load_file_button.setMaximumSize(QSize(150, 40))
        self.load_file_button.setFont(font)
        self.load_file_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.load_file_button.setStyleSheet(
            "QPushButton { border: none; padding: 10px; background-color: rgb(36,36,36); "
            "border-bottom: 2px solid transparent; } "
            "QPushButton:hover { background-color: rgb(23, 23, 23); }"
        )

        # Graph 2 button
        self.color_ok_button = QPushButton(self)
        self.color_ok_button.setObjectName("color_ok_button")
        self.color_ok_button.setGeometry(QRect(65, 200, 150, 40))
        self.color_ok_button.setMaximumSize(QSize(150, 40))
        self.color_ok_button.setFont(font)
        self.color_ok_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_ok_button.setStyleSheet(
            "QPushButton { border: none; padding: 10px; background-color: rgb(36,36,36); "
            "border-bottom: 2px solid transparent; } "
            "QPushButton:hover { background-color: rgb(23, 23, 23); }"
        )

        # Cancel button
        self.color_cancel_button = QPushButton(self)
        self.color_cancel_button.setObjectName("color_cancel_button")
        self.color_cancel_button.setGeometry(QRect(65, 250, 150, 40))
        self.color_cancel_button.setMaximumSize(QSize(150, 40))
        self.color_cancel_button.setFont(font)
        self.color_cancel_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_cancel_button.setStyleSheet(
            "QPushButton { border: none; padding: 10px; background-color: rgb(36,36,36); "
            "border-bottom: 2px solid transparent; } "
            "QPushButton:hover { background-color: rgb(23, 23, 23); }"
        )

        # Set text for label and buttons
        self.retranslateUi()

        # Connect buttons to dialog actions
        self.load_file_button.clicked.connect(self.accept_signal_1)
        self.color_ok_button.clicked.connect(self.accept_signal_2)
        self.color_cancel_button.clicked.connect(self.reject)

        self.selected_signal = None

    def retranslateUi(self):
        self.setWindowTitle("Choose Graph to Replace")
        self.load_file_button.setText("Graph 1")
        self.color_ok_button.setText("Graph 2")
        self.color_cancel_button.setText("Cancel")
        self.label.setText("Choose Graph to Replace")

    def accept_signal_1(self):
        self.selected_signal = 1
        self.accept()

    def accept_signal_2(self):
        self.selected_signal = 2
        self.accept()


class ColorPickerDialog(QDialog):
    def __init__(self, main_window=None):  # Add the main_window argument
        super().__init__()

        self.main_window = main_window  # Store the reference to the main window
        self.selected_color = None
        self.setupUi(self)

        # Connect buttons to color pickers
        self.load_file_button.clicked.connect(self.open_plot_color_picker)
        self.color_graph_button.clicked.connect(self.open_graph_color_picker)
        self.color_fig_button.clicked.connect(self.open_fig_color_picker)
        self.color_labels_button.clicked.connect(self.open_label_color_picker)

        # Connect the Ok and Cancel buttons
        self.color_ok_button.clicked.connect(self.apply_color_changes)  # Ok button
        self.color_cancel_button.clicked.connect(self.reject)  # Cancel button

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(477, 263)
        Dialog.setStyleSheet("background-color: rgb(184, 184,184);")

        font1 = QFont()
        font1.setFamily("Times New Roman")
        font1.setPointSize(17)

        # Label
        self.label = QLabel(Dialog)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(10, 10, 261, 51))
        font = QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(25)
        self.label.setFont(font)
        self.label.setStyleSheet("color:white")

        # Buttons
        self.color_ok_button = QPushButton(Dialog)
        self.color_ok_button.setGeometry(QRect(350, 200, 100, 40))
        self.color_ok_button.setMaximumSize(QSize(150, 40))
        self.color_ok_button.setFont(font1)
        self.color_ok_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_ok_button.setStyleSheet("background-color:rgb(30,30,30); color:white")

        self.load_file_button = QPushButton(Dialog)
        self.load_file_button.setGeometry(QRect(370, 100, 100, 40))
        self.load_file_button.setMaximumSize(QSize(150, 40))
        self.load_file_button.setFont(font1)
        self.load_file_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.load_file_button.setStyleSheet("color:white")

        self.color_cancel_button = QPushButton(Dialog)
        self.color_cancel_button.setGeometry(QRect(230, 200, 100, 40))
        self.color_cancel_button.setMaximumSize(QSize(150, 40))
        self.color_cancel_button.setFont(font1)
        self.color_cancel_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_cancel_button.setStyleSheet("background-color:rgb(30,30,30); color:white")

        self.color_graph_button = QPushButton(Dialog)
        self.color_graph_button.setGeometry(QRect(130, 100, 100, 40))
        self.color_graph_button.setMaximumSize(QSize(150, 40))
        self.color_graph_button.setFont(font1)
        self.color_graph_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_graph_button.setStyleSheet("color:white")

        self.color_fig_button = QPushButton(Dialog)
        self.color_fig_button.setGeometry(QRect(10, 100, 100, 40))
        self.color_fig_button.setMaximumSize(QSize(150, 40))
        self.color_fig_button.setFont(font1)
        self.color_fig_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_fig_button.setStyleSheet("color:white")

        self.color_labels_button = QPushButton(Dialog)
        self.color_labels_button.setGeometry(QRect(250, 100, 100, 40))
        self.color_labels_button.setMaximumSize(QSize(150, 40))
        self.color_labels_button.setFont(font1)
        self.color_labels_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_labels_button.setStyleSheet("color:white")

        self.retranslateUi(Dialog)
        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", "Select what to Change", None))
        self.color_ok_button.setText(QCoreApplication.translate("Dialog", "Ok", None))
        self.load_file_button.setText(QCoreApplication.translate("Dialog", "Plot", None))
        self.color_cancel_button.setText(QCoreApplication.translate("Dialog", "Cancel", None))
        self.color_graph_button.setText(QCoreApplication.translate("Dialog", "Graph", None))
        self.color_fig_button.setText(QCoreApplication.translate("Dialog", "Figure", None))
        self.color_labels_button.setText(QCoreApplication.translate("Dialog", "Labels", None))

    def open_color_dialog(self, initial_color):
        color = QColorDialog.getColor()  # Opens the color picker dialog
        if color.isValid():
            # Get the RGB values and convert them to 0-1 scale by dividing by 255
            rgb_color = color.getRgb()[:3]  # Get the RGB tuple
            return tuple(c / 255 for c in rgb_color)  # Convert each to a 0-1 range
        return initial_color

    def open_plot_color_picker(self):
        self.selected_color = 'plot'
        self.plot_color = self.open_color_dialog(self.main_window.plot_color)

    def open_graph_color_picker(self):
        self.selected_color = 'graph'
        # Accessing the instance variable with self.main_window
        self.graph_color = self.open_color_dialog(self.main_window.graph_color)  # Use self.main_window

    def open_fig_color_picker(self):
        self.selected_color = 'fig'
        # Accessing the instance variable with self
        self.fig_color = self.open_color_dialog(self.main_window.fig_color)  # Use self.main_window

    def open_label_color_picker(self):
        self.selected_color = 'label'
        # Accessing the instance variable with self
        self.label_color = self.open_color_dialog(self.main_window.label_color)  # Use self.main_window

    def apply_color_changes(self):
        """Apply the selected color based on which color picker was opened."""
        try:
            if self.selected_color == 'plot':
                self.main_window.plot_color = self.plot_color
                print(f"Plot color changed to: {self.main_window.plot_color}")
                self.update_plot_colors()  # Call to update the plot colors

            elif self.selected_color == 'graph':
                self.main_window.graph_color = self.graph_color
                print(f"Graph color changed to: {self.main_window.graph_color}")
                self.update_graph_colors()  # Call to update the graph colors

            elif self.selected_color == 'fig':
                self.main_window.fig_color = self.fig_color
                print(f"Figure color changed to: {self.main_window.fig_color}")
                self.update_canvas_colors()  # Call to update the canvas background color

            elif self.selected_color == 'label':
                self.main_window.label_color = self.label_color
                print(f"Label color changed to: {self.main_window.label_color}")
                self.update_label_colors()  # Call to update the label colors

        except Exception as e:
            print(f"Error applying color changes: {e}")

        self.accept()  # Close the dialog when Ok is pressed

    def update_canvas_colors(self):
        """Updates the figure background color."""
        self.main_window.figure.set_facecolor(self.main_window.fig_color)  # Use main_window for figure
        print(f"Figure background color updated to: {self.main_window.fig_color}")
        self.main_window.canvas.draw_idle()  # Redraw the canvas with updated colors

    def update_plot_colors(self):
        """Updates the plot color."""
        if hasattr(self.main_window, 'line_plot_1'):  # Check line_plot_1 in main_window
            self.main_window.line_plot_1.set_color(self.main_window.plot_color)
            print(f"Plot color updated to: {self.main_window.plot_color}")
        else:
            print("Line plot not found! Cannot update plot color.")
        self.main_window.canvas.draw_idle()  # Redraw the canvas with updated colors

    def update_graph_colors(self):
        """Updates the axes background and tick label colors."""
        if hasattr(self.main_window, 'ax1'):  # Check ax1 in main_window
            self.main_window.ax1.set_facecolor(self.main_window.graph_color)
            self.main_window.ax1.tick_params(colors=self.main_window.label_color)  # Update tick label color
            print(
                f"Graph background and tick labels updated for ax1: {self.main_window.graph_color}, {self.main_window.label_color}")
        else:
            print("ax1 not found! Cannot update graph background for ax1.")

        if hasattr(self.main_window, 'ax2'):  # Check ax2 in main_window
            self.main_window.ax2.set_facecolor(self.main_window.graph_color)
            self.main_window.ax2.tick_params(colors=self.main_window.label_color)  # Update tick label color
            print(
                f"Graph background and tick labels updated for ax2: {self.main_window.graph_color}, {self.main_window.label_color}")
        else:
            print("ax2 not found! Cannot update graph background for ax2.")

        self.main_window.canvas.draw_idle()  # Redraw the canvas with updated colors

    def update_label_colors(self):
        self.main_window.label_color = self.label_color
        print(f"Label color changed to: {self.main_window.label_color}")
        if hasattr(self.main_window, 'ax_polar'):
            self.main_window.ax_polar.tick_params(colors=self.label_color)
            print("Label colors updated.")
        else:
            print("Polar plot not found! Cannot update label colors.")

        self.main_window.canvas.draw_idle()  # Redraw the canvas with updated colors


class ReportDialog(QDialog):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window  # Reference to main window
        self.setupUi(self)  # Set up UI elements

        # Connect buttons to actions
        self.report_done_button.clicked.connect(self.reject)  # Done button
        self.get_stats_button.clicked.connect(self.get_stats)  # Get Stats action
        self.snapshot_button.clicked.connect(self.take_snapshot)  # Take Snapshot action

    def setupUi(self, Dialog):
        Dialog.setObjectName("ReportDialog")
        Dialog.resize(250, 275)
        Dialog.setStyleSheet("background-color: rgb(184, 184,184);")

        font1 = QFont()
        font1.setFamily("Times New Roman")
        font1.setPointSize(17)

        # Label for the dialog
        self.report_label = QLabel(Dialog)
        self.report_label.setGeometry(QRect(30, 10, 190, 51))
        self.report_label.setFont(font1)
        self.report_label.setStyleSheet("color:white")
        self.report_label.setText("Pick a Selection")

        # Get Stats button
        self.get_stats_button = QPushButton(Dialog)
        self.get_stats_button.setGeometry(QRect(50, 90, 150, 40))
        self.get_stats_button.setFont(font1)
        self.get_stats_button.setStyleSheet("color:white")
        self.get_stats_button.setText("Get Stats")

        # Take Snapshot button
        self.snapshot_button = QPushButton(Dialog)
        self.snapshot_button.setGeometry(QRect(50, 150, 150, 40))
        self.snapshot_button.setFont(font1)
        self.snapshot_button.setStyleSheet("color:white")
        self.snapshot_button.setText("Take Snapshot")

        # Done button
        self.report_done_button = QPushButton(Dialog)
        self.report_done_button.setGeometry(QRect(50, 210, 150, 40))
        self.report_done_button.setFont(font1)
        self.report_done_button.setStyleSheet("background-color:rgb(30,30,30); color:white")
        self.report_done_button.setText("Done")

        QMetaObject.connectSlotsByName(Dialog)

    def get_stats(self):
        """Generate statistics report for Signal 1 only or for Signal 1, Signal 2, and Glued Signal if second graph is active."""
        report_data = []

        # Collect stats for Signal 1 (always included)
        if hasattr(self.main_window, 'signal_data_1'):
            signal_data_1 = self.main_window.signal_data_1
            stats_1 = self.calculate_statistics(signal_data_1)
            if any(stats_1.values()):  # Check if any value is not None
                report_data.append(("Signal 1 Statistics", stats_1))

        # If second graph is active, include Signal 2 and Glued Signal stats
        if self.main_window.is_second_graph_active:
            # Collect stats for Signal 2 (if exists)
            if hasattr(self.main_window, 'signal_data_2'):
                signal_data_2 = self.main_window.signal_data_2
                stats_2 = self.calculate_statistics(signal_data_2)
                if any(stats_2.values()):
                    report_data.append(("Signal 2 Statistics", stats_2))

            # Collect stats for Glued Signal (if exists)
            if hasattr(self.main_window, 'glued_signal_data'):
                glued_signal_data = self.main_window.glued_signal_data
                stats_glued = self.calculate_statistics(glued_signal_data)
                if any(stats_glued.values()):
                    report_data.append(("Glued Signal Statistics", stats_glued))

        # Check if there is any report data to generate
        if report_data:
            # Set initial file path and name
            initial_path = "/path/to/initial/directory/"  # Set your initial directory path
            initial_name = "Signal_Statistics_Report.pdf"  # Set your desired initial file name

            # Open save file dialog with initial directory and file name
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save Report", initial_path + initial_name, "PDF Files (*.pdf)"
            )

            if filename:
                if not filename.endswith(".pdf"):
                    filename += ".pdf"  # Ensure the file has a .pdf extension

                # Create the PDF
                self.create_pdf(filename, report_data)
        else:
            QtWidgets.QMessageBox.warning(self, "No Data", "No valid signal data available to generate report.")

    def create_pdf(self, filename, report_data):
        """Create a PDF report based on collected statistics."""
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "Signal Statistics Report")
        c.setFont("Helvetica", 12)

        y_position = height - 1.5 * inch

        # Write statistics for each signal
        for title, stats in report_data:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1 * inch, y_position, title)
            y_position -= 0.3 * inch

            c.setFont("Helvetica", 12)
            for key, value in stats.items():
                c.drawString(1 * inch, y_position, f"{key}: {value}")
                y_position -= 0.2 * inch

            y_position -= 0.5 * inch

        c.save()

    def calculate_statistics(self, signal_data):
        """Calculate basic statistics for a given signal."""
        if signal_data is None or len(signal_data) == 0:
            return {
                "mean": None,
                "std": None,
                "min": None,
                "max": None,
                "duration": None,
            }

        return {
            "mean": np.mean(signal_data),
            "std": np.std(signal_data),
            "min": np.min(signal_data),
            "max": np.max(signal_data),
            "duration": len(signal_data),  # Assuming this is duration based on data points
        }

    def take_snapshot(self):
        """Take a snapshot of the current signal graph."""
        # Set initial file path and name
        initial_path = "/path/to/initial/directory/"  # Set your initial directory path
        initial_name = "Signal_Snapshot.png"  # Set your desired initial file name

        # Open save file dialog with initial directory and file name
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Snapshot", initial_path + initial_name, "Images (*.png *.jpg *.jpeg)"
        )

        if filename:
            # Ensure the file extension is correct based on the user's choice
            if not (filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg")):
                filename += ".png"  # Default to PNG if no valid extension is provided

            # Save the snapshot of the figure
            self.main_window.canvas_1.figure.savefig(filename)


class Ui_MainWindow(object):
    def __init__(self):
        self.factor = 1
        self.fig_color = (0, 0, 0)
        self.graph_color = (20 / 255, 20 / 255, 20 / 255)
        self.plot_color = (1, 1, 1)
        self.label_color = (1, 1, 1)
        self.backface_color = (0.1, 0.1, 0.1)
        self.is_animating = False
        self.is_second_graph_active = False
        self.is_glued = False
        self.is_merged = False

    def setupUi(self, MainWindow):
        # Main window setup
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 800)
        font = QtGui.QFont()
        font.setPointSize(11)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet("QWidget { background-color: black; }")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Horizontal line for header separation
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(-10, 70, 1300, 2))
        self.line.setStyleSheet("background-color:white;")
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        # Header buttons (Home, Signals, Quit)
        self.HomeButton = self.create_button(self.centralwidget, "Home", 790, 18, "rgb(252, 108, 248)")
        self.SignalsButton = self.create_button(self.centralwidget, "Signals", 950, 18, "rgb(147, 247, 167)")
        self.QuitButton = self.create_button(self.centralwidget, "Quit Application", 1120, 18, "rgb(179, 15, 66)")
        self.QuitButton.clicked.connect(QtWidgets.QApplication.quit)

        # Home Page Content Initialization
        self.home_content = QtWidgets.QWidget(self.centralwidget)
        self.home_content.setGeometry(QtCore.QRect(0, 100, 1280, 631))

        # Header icon and title
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 5, 60, 60))
        font.setFamily("Times New Roman")
        self.label.setFont(font)
        self.label.setStyleSheet("color: white;")
        self.label.setPixmap(QtGui.QPixmap("src/sound-wave.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")

        self.HeaderTitleLabel = QtWidgets.QLabel(self.centralwidget)
        self.HeaderTitleLabel.setGeometry(QtCore.QRect(70, 18, 191, 40))
        font.setPointSize(17)
        self.HeaderTitleLabel.setFont(font)
        self.HeaderTitleLabel.setStyleSheet("color: white;")
        self.HeaderTitleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.HeaderTitleLabel.setObjectName("HeaderTitleLabel")

        # Graph and labels for home page
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(0, 100, 791, 631))
        self.label_3.setPixmap(QtGui.QPixmap("src/Graph.png"))
        self.label_3.setScaledContents(True)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")

        self.HomeTitleLabel = QtWidgets.QLabel(self.centralwidget)
        self.HomeTitleLabel.setGeometry(QtCore.QRect(740, 270, 511, 91))
        font.setPointSize(36)
        font.setBold(True)
        font.setItalic(True)
        self.HomeTitleLabel.setFont(font)
        self.HomeTitleLabel.setStyleSheet("color:white;")
        self.HomeTitleLabel.setWordWrap(True)
        self.HomeTitleLabel.setObjectName("HomeTitleLabel")

        self.HomeSubTitle = QtWidgets.QLabel(self.centralwidget)
        self.HomeSubTitle.setGeometry(QtCore.QRect(740, 350, 461, 101))
        font.setPointSize(14)
        self.HomeSubTitle.setFont(font)
        self.HomeSubTitle.setStyleSheet("color:white;")
        self.HomeSubTitle.setWordWrap(True)
        self.HomeSubTitle.setObjectName("HomeSubTitle")

        self.ProceedSignalsButton = QtWidgets.QPushButton(self.centralwidget)
        self.ProceedSignalsButton.setGeometry(QtCore.QRect(740, 590, 390, 60))
        font.setPointSize(21)
        self.ProceedSignalsButton.setFont(font)
        self.ProceedSignalsButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ProceedSignalsButton.setStyleSheet("""
            QPushButton {
                border: 2px solid rgb(252, 108, 248);
                padding: 10px;
                color: white;
            }
            QPushButton:hover {
                border-color:rgb(147, 247, 167);
                background-color: rgb(30,30,30);
            }
        """)
        self.ProceedSignalsButton.setObjectName("ProceedSignalsButton")
        self.ProceedSignalsButton.clicked.connect(self.show_signals_page)

        # Signals Page Initialization
        self.signal_content = QtWidgets.QWidget(self.centralwidget)
        self.signal_content.setGeometry(QtCore.QRect(0, 100, 1280, 631))
        self.signal_content.setObjectName("signal_content")
        self.signal_content.hide()

        # Signal selection buttons and images
        self.setup_signal_title_label()
        self.setup_signal_buttons()

        # Individual signal pages (ECG, Circular, etc.)
        self.setup_signal_pages()

        # Menu and status bar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        # Connect buttons to page switching functionality
        self.connect_buttons()

        # Set initial active button (Home)
        self.set_active_button_style(self.HomeButton)

        # Add the central widget to the main window
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Multi-Port Signal Viewer"))
        self.HomeButton.setText(_translate("MainWindow", "Home"))
        self.SignalsButton.setText(_translate("MainWindow", "Signals"))
        self.QuitButton.setText(_translate("MainWindow", "Quit Application"))
        self.HeaderTitleLabel.setText(_translate("MainWindow", "Multi-Port Signal Viewer"))
        self.HomeTitleLabel.setText(_translate("MainWindow", "Hello from the Signal Innovators"))
        self.HomeSubTitle.setText(
            "Empowering data, one signal at a time. As a team of passionate problem-solvers, we transform complex signals into meaningful insights, helping you visualize and understand the world of medical data with precision and innovation. Let’s shape the future of signal analysis together, one breakthrough at a time.")
        self.ProceedSignalsButton.setText(_translate("MainWindow", "Proceed to Signal"))

    def create_button(self, parent, text, x, y, hover_color):
        # Helper function to create and style a button
        button = QtWidgets.QPushButton(parent)
        button.setGeometry(QtCore.QRect(x, y, 140, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(17)
        button.setFont(font)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setStyleSheet(f"""
            QPushButton {{
                border: none;
                padding: 10px;
                color: white;
                border-bottom: 2px solid transparent;
            }}
            QPushButton:hover {{
                border-bottom-color: {hover_color};
                color: {hover_color};
            }}
        """)
        button.setText(text)
        return button

    def create_signal_button_with_label(self, parent, image_path, button_text, x, y):
        # Create a label for the image
        image_label = QtWidgets.QLabel(parent)
        image_label.setGeometry(QtCore.QRect(x, y, 270, 260))  # Set geometry for image label
        image_label.setPixmap(QtGui.QPixmap(image_path))  # Set the image from the provided path
        image_label.setScaledContents(True)  # Scale the image to fit the label
        image_label.setAlignment(QtCore.Qt.AlignCenter)  # Center the image
        image_label.setObjectName(f"{button_text}_image_label")  # Assign object name based on the button text

        # Create the button below the label
        button = QtWidgets.QPushButton(parent)
        button.setGeometry(QtCore.QRect(x, y + 260, 270, 60))  # Place button directly below the label
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(25)
        button.setFont(font)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 10px;
                color: rgb(184, 184, 184);
                border: 2px solid rgb(184, 184, 184);
                background-color: rgb(20, 20, 20);
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
        """)
        button.setText(button_text)
        button.setObjectName(f"{button_text}_button")  # Assign object name based on the button text

        return image_label, button

    def add_back_button(self, parent_widget, icon_path="src/backArrow.png"):
        # Create and configure the back button for a given parent widget
        back_button = QtWidgets.QPushButton(parent_widget)
        back_button.setMaximumSize(QSize(150, 60))
        # Set back button icon
        icon = QtGui.QIcon()
        icon.addFile(icon_path, QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        back_button.setIcon(icon)
        back_button.setIconSize(QtCore.QSize(80, 80))
        back_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        back_button.raise_()

        return back_button

    def handle_back_button(self):
        # Show the signals page
        self.show_signals_page()

    def handle_rectangular_back_button(self):

        self.reset_rectangular_signals()
        # Show the signals page
        self.show_signals_page()

    def create_signal_page(self, parent=None):
        # Create a signal-specific content page
        signal_page = QtWidgets.QLabel(parent)
        signal_page.setGeometry(QtCore.QRect(0, 100, 1280, 631))
        signal_page.hide()
        return signal_page

    def setup_signal_pages(self):
        # Setup signal content (ECG, Circular, EEG, RTS) and their back buttons
        self.rectangular_content = self.create_signal_page(self.centralwidget)

        self.RTS_content = self.create_signal_page(self.centralwidget)

        self.circular_content = self.create_signal_page(self.centralwidget)

    def setup_signal_title_label(self):
        # Set up the title label for the signal page
        self.SignalTitleLabel = QtWidgets.QLabel(self.signal_content)
        self.SignalTitleLabel.setGeometry(QtCore.QRect(270, 80, 740, 91))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(80)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.SignalTitleLabel.setFont(font)
        self.SignalTitleLabel.setStyleSheet("color: white;")
        self.SignalTitleLabel.setAlignment(QtCore.Qt.AlignCenter)  # Center the text horizontally and vertically
        self.SignalTitleLabel.setObjectName("SignalTitleLabel")
        self.SignalTitleLabel.setText("Pick a Type of Signal!")  # Set the default text

    def setup_signal_buttons(self):
        # Set up labels and buttons for signals page
        self.rectangular_image, self.rectuangular_Button = self.create_signal_button_with_label(self.signal_content,
                                                                                                "src/rectangular-signal.png",
                                                                                                "Rectangular Signal",
                                                                                                118, 300)
        self.RTS_image, self.RTS_Button = self.create_signal_button_with_label(self.signal_content, "src/weather.png",
                                                                               "Real Time Signal", 505, 300)
        self.circular_image, self.circular_Button = self.create_signal_button_with_label(self.signal_content,
                                                                                         "src/PolarPlot.png",
                                                                                         "Circular Signal", 893, 300)
        # Create and configure overlay buttons
        self.create_overlay_button("rectangular_overlay", 118, 300, self.rectuangular_Button.click)
        self.create_overlay_button("RTS_overlay", 505, 300, self.RTS_Button.click)
        self.create_overlay_button("circular_overlay", 893, 300, self.circular_Button.click)

    def create_overlay_button(self, name, x, y, callback):
        # Create an overlay button with semi-transparent background and cursor
        overlay_button = QtWidgets.QPushButton(self.signal_content)
        overlay_button.setGeometry(QtCore.QRect(x, y, 270, 260))
        overlay_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        overlay_button.setStyleSheet("background-color:rgba(20,20,20,200);")
        overlay_button.setObjectName(name)
        overlay_button.clicked.connect(callback)
        return overlay_button

    def connect_buttons(self):
        # Connect button clicks to page-switching methods
        self.HomeButton.clicked.connect(self.show_home_page)
        self.SignalsButton.clicked.connect(self.show_signals_page)

        self.rectuangular_Button.clicked.connect(self.show_rectangular_page)
        self.circular_Button.clicked.connect(self.show_circular_page)
        self.RTS_Button.clicked.connect(self.show_RTS_page)

    def set_active_button_style(self, active_button):
        # Style the active button to show which page is selected
        self.HomeButton.setStyleSheet(
            "QPushButton { padding: 10px; color: white; border-bottom: none; }")
        self.SignalsButton.setStyleSheet(
            "QPushButton { padding: 10px; color: white; border-bottom: none; }")

        if active_button == self.HomeButton:
            active_style = "QPushButton { color: rgb(252, 108, 248); border-bottom: 2px solid rgb(252, 108, 248); }"
        elif active_button == self.SignalsButton:
            active_style = "QPushButton { color: rgb(147, 247, 167); border-bottom: 2px solid rgb(147, 247, 167); }"
        active_button.setStyleSheet(active_style)

    # Methods to show different pages
    def show_home_page(self):
        self.home_content.show()
        self.signal_content.hide()
        self.hide_all_signal_pages()
        self.set_active_button_style(self.HomeButton)

    def show_signals_page(self):
        self.home_content.hide()
        self.signal_content.show()
        self.hide_all_signal_pages()
        self.set_active_button_style(self.SignalsButton)

    def show_rectangular_page(self):
        self.signal_content.hide()
        self.hide_all_signal_pages(exclude="Rectangular")  # Ensure all other signal pages are hidden
        self.rectangular_content.show()  # Show the EEG content page
        self.setup_rectangular_page()  # Initialize the EEG page (plotting, buttons, etc.)

    def show_RTS_page(self):
        self.signal_content.hide()
        self.hide_all_signal_pages(exclude="RTS")
        self.RTS_content.show()
        self.setup_RTS_page()

    def show_circular_page(self):
        self.signal_content.hide()
        self.hide_all_signal_pages(exclude="Circular")
        self.circular_content.show()
        self.setup_circular_page()

    def hide_all_signal_pages(self, exclude=None):
        # Helper method to hide all signal pages except the one specified
        if exclude != "Rectangular":
            self.rectangular_content.hide()
        if exclude != "Circular":
            self.circular_content.hide()
        if exclude != "RTS":
            self.RTS_content.hide()

    '''---------------------------------------------------------------------------------------------------------------------------------------'''

    def initialize_rectangular_graph(self, content_widget, play_pause_button_1, play_pause_button_2, reset_button,
                                     link_button, unified_play_pause_button, replace_signal_button, add_graph_button,
                                     merge_button, glue_button, speed_button, get_rectangular_report_button,
                                     signal_1_label="Signals",
                                     signal_2_label=None):

        # Set up the canvas for plotting signals
        # Create a new figure for each axis
        self.figure_1 = Figure(facecolor=self.fig_color)  # For ax1
        self.figure_2 = Figure(facecolor=self.fig_color)  # For ax2

        # Create canvases for each figure
        self.canvas_1 = FigureCanvas(self.figure_1)
        self.canvas_2 = FigureCanvas(self.figure_2)

        content_widget.setFixedHeight(680)

        # Layout for the first graph
        layout_1 = QtWidgets.QVBoxLayout()

        # Horizontal slider for the first graph
        self.horizontal_slider_1 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.horizontal_slider_1.setRange(0, 800)
        self.horizontal_slider_1.setValue(0)

        self.horizontal_slider_1.valueChanged.connect(lambda value: self.scroll_horizontal('ax1', value))

        layout_1.addWidget(self.canvas_1)
        layout_1.addWidget(self.horizontal_slider_1)

        # Layout for the second graph
        layout_2 = QtWidgets.QVBoxLayout()
        # Horizontal slider for the second graph
        self.horizontal_slider_2 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.horizontal_slider_2.setRange(0, 800)
        self.horizontal_slider_2.setValue(0)
        self.horizontal_slider_2.valueChanged.connect(lambda value: self.scroll_horizontal('ax2', value))

        layout_2.addWidget(self.canvas_2)
        layout_2.addWidget(self.horizontal_slider_2)
        # Hide the components of layout_2 initially
        for i in range(layout_2.count()):
            layout_2.itemAt(i).widget().hide()  # Hide each widget in layout_2

        # Style the horizontal slider using a stylesheet
        self.horizontal_slider_1.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 5px;
                background: #262626;  /* Groove background color */
                margin: 0px 0px;
            }

            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #5c5c5c; /* Handle border */
                width: 40px; /* Handle width */
                margin: -40px 0; /* Handle overlap with groove */
                border-radius: 10px;
            }

            QSlider::add-page:horizontal {
                background: #262626; /* Color for the unfilled part */
                border: 1px solid #777;
                height: 0px;
                border-radius: 4px;
            }

        """)
        self.horizontal_slider_2.setStyleSheet("""
                    QSlider::groove:horizontal {
                        border: 1px solid #999999;
                        height: 5px;
                        background: #262626;  /* Groove background color */
                        border-radius: 4px;
                        margin: 0px 0px;
                    }

                    QSlider::handle:horizontal {
                        background: #ffffff;
                        width: 40px; /* Handle width */
                        margin: -40px 0; /* Handle overlap with groove */
                        border-radius: 10px;
                    }

                    QSlider::add-page:horizontal {
                        background: #262626; /* Color for the unfilled part */
                        border: 1px solid #777;
                        height: 10px;
                        border-radius: 4px;
                    }

                """)

        # Create a vertical layout for the content and add the canvas
        layout = QtWidgets.QHBoxLayout(content_widget)
        canvas_layouts = QtWidgets.QVBoxLayout()

        canvas_layouts.addLayout(layout_1)
        canvas_layouts.addLayout(layout_2)
        # Create a horizontal layout for buttons
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setSpacing(30)  # Adjust spacing between buttons

        # Set up the font
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(17)

        add_graph_button.setFixedSize(150, 40)
        add_graph_button.setFont(font)  # Set Times New Roman font
        add_graph_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        add_graph_button.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background-color: rgb(40,40,40);
            }}
            QPushButton:hover {{
                background-color: rgb(20,20,20);
            }}
        """)
        add_graph_button.clicked.connect(lambda: self.toggle_add_rectangular_graph(add_graph_button))
        button_layout.addWidget(add_graph_button, alignment=QtCore.Qt.AlignHCenter)

        # Add unified Play/Pause button for both signals
        unified_play_pause_button.setFixedSize(150, 40)
        unified_play_pause_button.setFont(font)
        unified_play_pause_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        unified_play_pause_button.setStyleSheet(f"""
                QPushButton {{
                    color: white;
                    background-color: rgb(40,40,40);
                }}
                QPushButton:hover {{
                    background-color: rgb(20,20,20);
                }}
            """)
        unified_play_pause_button.clicked.connect(lambda: self.toggle_unified_play_pause(unified_play_pause_button))
        button_layout.addWidget(unified_play_pause_button)
        unified_play_pause_button.hide()
        self.unified_play_pause_button = unified_play_pause_button

        # Add Play/Pause buttons for both signals
        play_pause_button_1.setFixedSize(150, 40)
        play_pause_button_1.setFont(font)  # Set Times New Roman font
        play_pause_button_1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        play_pause_button_1.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background-color: rgb(40,40,40);
            }}
            QPushButton:hover {{
                background-color: rgb(20,20,20);
            }}
        """)
        play_pause_button_1.clicked.connect(
            lambda: self.toggle_play_pause_rectangular_signal(self.timer_1, play_pause_button_1))
        button_layout.addWidget(play_pause_button_1)
        self.play_pause_button_1 = play_pause_button_1

        play_pause_button_2.setFixedSize(150, 40)
        play_pause_button_2.setFont(font)  # Set Times New Roman font
        play_pause_button_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        play_pause_button_2.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background-color: rgb(40,40,40);
            }}
            QPushButton:hover {{
                background-color: rgb(20,20,20);
            }}
        """)
        play_pause_button_2.clicked.connect(
            lambda: self.toggle_play_pause_rectangular_signal(self.timer_2, play_pause_button_2))
        button_layout.addWidget(play_pause_button_2)
        play_pause_button_2.hide()
        self.play_pause_button_2 = play_pause_button_2

        # Add Play/Pause buttons for both signals
        reset_button.setFixedSize(150, 40)
        reset_button.setFont(font)  # Set Times New Roman font
        reset_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        reset_button.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background-color: rgb(40,40,40);
            }}
            QPushButton:hover {{
                background-color: rgb(20,20,20);
            }}
        """)
        reset_button.clicked.connect(
            lambda: self.reset_rectangular_signals())
        button_layout.addWidget(reset_button, alignment=QtCore.Qt.AlignHCenter)

        self.reset_button = reset_button
        speed_button.setFixedSize(150, 40)
        speed_button.setFont(font)  # Set Times New Roman font
        speed_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        speed_button.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background-color: rgb(40,40,40);
            }}
            QPushButton:hover {{
                background-color: rgb(20,20,20);
            }}
        """)
        speed_button.setCheckable(True)  # Make it toggleable
        button_layout.addWidget(speed_button, alignment=QtCore.Qt.AlignHCenter)
        speed_button.clicked.connect(lambda: self.toggle_speed(speed_button))
        self.speed_button = speed_button

        # Add Link/Unlink button
        link_button.setFixedSize(150, 40)
        link_button.setFont(font)
        link_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        link_button.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background-color: rgb(40,40,40);
            }}
            QPushButton:hover {{
                background-color: rgb(20,20,20);
            }}
        """)

        # Add Replace Signal button
        replace_signal_button.setFixedSize(150, 40)
        replace_signal_button.setFont(font)  # Set Times New Roman font
        replace_signal_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        replace_signal_button.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background-color: rgb(40,40,40);
            }}
            QPushButton:hover {{
                background-color: rgb(20,20,20);
            }}
        """)
        replace_signal_button.clicked.connect(self.replace_signal)
        button_layout.addWidget(replace_signal_button, alignment=QtCore.Qt.AlignHCenter)
        self.replace_signal_button = replace_signal_button

        # Add Merge/Unmerge button with dynamic signal labels
        merge_button.setFixedSize(150, 40)
        merge_button.setFont(font)  # Set Times New Roman font
        merge_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        merge_button.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background-color: rgb(40,40,40);
            }}
            QPushButton:hover {{
                background-color: rgb(20,20,20);
            }}
        """)
        merge_button.setCheckable(True)  # Make it toggleable
        merge_button.toggled.connect(
            lambda checked: self.toggle_merge_signals(checked, signal_1_label,
                                                      signal_2_label))  # Use lambda to pass labels
        button_layout.addWidget(merge_button, alignment=QtCore.Qt.AlignHCenter)
        merge_button.hide()
        self.merge_button = merge_button

        # Add Glue/Unglue button with a dropdown for cut options
        glue_button = QtWidgets.QToolButton(content_widget)
        glue_button.setText("Glue")
        glue_button.setFixedSize(150, 40)
        glue_button.setFont(font)
        glue_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        glue_button.setStyleSheet(f"""
            QToolButton {{
                color: white;
                background-color: rgb(40,40,40);
            }}
            QToolButton:hover {{
                background-color: rgb(20,20,20);
            }}
        """)
        glue_button.setCheckable(True)  # Make it toggleable
        button_layout.addWidget(glue_button, alignment=QtCore.Qt.AlignHCenter)

        # Set the popup mode for dropdown menu behavior
        glue_button.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)

        # Create a menu for the dropdown options
        glue_menu = QtWidgets.QMenu()
        glue_menu.setStyleSheet(
            """
            QMenu { 
                background-color: rgb(40, 40, 40); 
            }
            QLabel { 
                color: white; 
            }
            """
        )

        # # Add interpolation method combo box to the glue menu
        # interp_method_widget = QtWidgets.QWidgetAction(glue_menu)
        # interp_method_container = QtWidgets.QWidget()
        # interp_method_layout = QtWidgets.QHBoxLayout()
        # interp_method_label = QtWidgets.QLabel("Interpolation:")
        # self.interpolation_method = QComboBox()
        # self.interpolation_method.addItem("Linear")
        # self.interpolation_method.addItem("Sinusoidal")
        # self.interpolation_method.addItem("Moving Average")
        # self.interpolation_method.setStyleSheet('color : black')
        # interp_method_layout.addWidget(interp_method_label)
        # interp_method_layout.addWidget(self.interpolation_method)
        # interp_method_container.setLayout(interp_method_layout)
        # interp_method_widget.setDefaultWidget(interp_method_container)
        # glue_menu.addAction(interp_method_widget)

        # Create SpinBox for Start Cut 1
        start_cut_1_widget = QtWidgets.QWidgetAction(glue_menu)
        start_cut_1_container = QtWidgets.QWidget()
        start_cut_1_layout = QtWidgets.QHBoxLayout()
        start_cut_1_label = QtWidgets.QLabel("Start Cut 1:")
        self.start_cut_1 = QtWidgets.QSpinBox()
        self.start_cut_1.setRange(0, 4500)
        start_cut_1_layout.addWidget(start_cut_1_label)
        start_cut_1_layout.addWidget(self.start_cut_1)
        start_cut_1_container.setLayout(start_cut_1_layout)
        start_cut_1_widget.setDefaultWidget(start_cut_1_container)
        glue_menu.addAction(start_cut_1_widget)

        # Create SpinBox for End Cut 1
        end_cut_1_widget = QtWidgets.QWidgetAction(glue_menu)
        end_cut_1_container = QtWidgets.QWidget()
        end_cut_1_layout = QtWidgets.QHBoxLayout()
        end_cut_1_label = QtWidgets.QLabel("End Cut 1:")
        self.end_cut_1 = QtWidgets.QSpinBox()
        self.end_cut_1.setRange(0, 4500)
        end_cut_1_layout.addWidget(end_cut_1_label)
        end_cut_1_layout.addWidget(self.end_cut_1)
        end_cut_1_container.setLayout(end_cut_1_layout)
        end_cut_1_widget.setDefaultWidget(end_cut_1_container)
        glue_menu.addAction(end_cut_1_widget)

        # Create SpinBox for Start Cut 2
        start_cut_2_widget = QtWidgets.QWidgetAction(glue_menu)
        start_cut_2_container = QtWidgets.QWidget()
        start_cut_2_layout = QtWidgets.QHBoxLayout()
        start_cut_2_label = QtWidgets.QLabel("Start Cut 2:")
        self.start_cut_2 = QtWidgets.QSpinBox()
        self.start_cut_2.setRange(0, 4500)
        start_cut_2_layout.addWidget(start_cut_2_label)
        start_cut_2_layout.addWidget(self.start_cut_2)
        start_cut_2_container.setLayout(start_cut_2_layout)
        start_cut_2_widget.setDefaultWidget(start_cut_2_container)
        glue_menu.addAction(start_cut_2_widget)

        # Create SpinBox for End Cut 2
        end_cut_2_widget = QtWidgets.QWidgetAction(glue_menu)
        end_cut_2_container = QtWidgets.QWidget()
        end_cut_2_layout = QtWidgets.QHBoxLayout()
        end_cut_2_label = QtWidgets.QLabel("End Cut 2:")
        self.end_cut_2 = QtWidgets.QSpinBox()
        self.end_cut_2.setRange(0, 4500)
        end_cut_2_layout.addWidget(end_cut_2_label)
        end_cut_2_layout.addWidget(self.end_cut_2)
        end_cut_2_container.setLayout(end_cut_2_layout)
        end_cut_2_widget.setDefaultWidget(end_cut_2_container)
        glue_menu.addAction(end_cut_2_widget)

        # Set the menu for the glue button
        glue_button.setMenu(glue_menu)

        # Hide the glue button initially (if needed)
        glue_button.hide()
        glue_button.clicked.connect(self.toggle_glue_unglue)
        self.glue_button = glue_button

        # Add report button
        get_rectangular_report_button.setFixedSize(150, 40)
        get_rectangular_report_button.setFont(font)  # Set Times New Roman font
        get_rectangular_report_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        get_rectangular_report_button.setStyleSheet(f"""
            QPushButton {{
                color: white;
                background-color: rgb(40,40,40);
            }}
            QPushButton:hover {{
                background-color: rgb(20,20,20);
            }}
        """)
        get_rectangular_report_button.setCheckable(True)  # Make it toggleable
        button_layout.addWidget(get_rectangular_report_button, alignment=QtCore.Qt.AlignHCenter)
        get_rectangular_report_button.toggled.connect(self.open_reprot_page)
        self.get_rectangular_report_button = get_rectangular_report_button

        layout.addLayout(canvas_layouts)
        # Add the button layout to the main layout
        layout.addLayout(button_layout)

        # Add back button using the add_back_button function
        back_button = self.add_back_button(content_widget)
        back_button.setFont(font)  # Set Times New Roman font
        back_button.clicked.connect(self.handle_rectangular_back_button)
        button_layout.addWidget(back_button)

    def setup_rectangular_page(self):
        if not hasattr(self, 'rectangular_initialized') or not self.rectangular_initialized:
            print("Setting up Rectangular page...")  # Debug

            # Create buttons for the Rectangular page
            play_pause_button_1 = QtWidgets.QPushButton("Play ▶", self.rectangular_content)
            play_pause_button_2 = QtWidgets.QPushButton("Play ▶", self.rectangular_content)
            unified_play_pause_button = QtWidgets.QPushButton("Play Both ▶", self.rectangular_content)
            reset_button = QtWidgets.QPushButton("Reset Signal", self.rectangular_content)
            speed_button = QtWidgets.QPushButton("1X", self.rectangular_content)
            link_button = QtWidgets.QPushButton("Link", self.rectangular_content)
            add_graph_button = QtWidgets.QPushButton("Add Graph", self.rectangular_content)
            replace_signal_button = QtWidgets.QPushButton("Replace Signal", self.rectangular_content)
            merge_button = QtWidgets.QPushButton("Merge", self.rectangular_content)
            glue_button = QtWidgets.QPushButton("Glue", self.rectangular_content)
            get_rectangular_report_button = QtWidgets.QPushButton("Get Report", self.rectangular_content)

            # Call initialize_rectangular_graph with Rectangular-specific buttons and content
            self.initialize_rectangular_graph(
                content_widget=self.rectangular_content,
                play_pause_button_1=play_pause_button_1,
                play_pause_button_2=play_pause_button_2,
                reset_button=reset_button,
                speed_button=speed_button,
                unified_play_pause_button=unified_play_pause_button,
                link_button=link_button,
                add_graph_button=add_graph_button,
                replace_signal_button=replace_signal_button,
                merge_button=merge_button,
                glue_button=glue_button,
                get_rectangular_report_button=get_rectangular_report_button,
                signal_1_label="Rectangular Signal",
                signal_2_label="Rectangular Signal 2"
            )

            # Set up the timers for playing and updating signals
            self.timer_1 = QtCore.QTimer()
            self.timer_1.timeout.connect(
                lambda: self.update_rectangular_signal('signal_data_1', 'index_1', self.window_size_1, self.line_plot_1,
                                                       self.ax1, self.timer_1))

            self.timer_2 = QtCore.QTimer()
            self.timer_2.timeout.connect(
                lambda: self.update_rectangular_signal('signal_data_2', 'index_2', self.window_size_2, self.line_plot_2,
                                                       self.ax2, self.timer_2))

            # Create the subplots for Rectangular (Signal 1) and ECG (Signal 2)
            self.ax1 = self.figure_1.add_subplot(111)  # Only one graph (Rectangular) initially
            self.ax1.set_title("Rectangular Signal", color=self.label_color)

            # Load and initialize Rectangular signal data
            filename = 'Data/Rectangular Data/EEG/Z002.txt'
            self.signal_data_1 = np.loadtxt(filename)
            self.index_1 = 0
            self.window_size_1 = 400  # Initial window size for Rectangular

            filename2 = 'Data/Rectangular Data/EEG/Z003.txt'
            self.signal_data_2 = np.loadtxt(filename2)
            self.index_2 = 0
            self.window_size_2 = 400  # Initial window size for  Rectangular Signal 2 (this was missing)

            # Plot the first graph initially (Rectangular)
            self.ax1 = self.figure_1.add_subplot(111)  # Only one graph (Rectangular) initially
            self.ax1.set_xlim(0, self.window_size_1)
            self.ax1.set_ylim(np.min(self.signal_data_1), np.max(self.signal_data_1))
            # Initially, don't plot any data
            self.line_plot_1, = self.ax1.plot([], [], color=self.plot_color)
            self.ax1.tick_params(colors=self.label_color)
            self.ax1.minorticks_on()  # Enable minor ticks
            self.ax1.grid(True, which='minor', color='lightgray', linestyle=':', linewidth=0.5, alpha=0.5)

            self.ax1.set_facecolor(self.backface_color)
            self.ax1.set_title("Rectangular Signal", color=self.label_color)
            self.ax1.set_xlabel("Time (s)", color=self.label_color)
            self.ax1.set_ylabel("Amplitude (µV)", color=self.label_color)

            # Update spinbox ranges for the signal
            self.start_cut_1.setRange(0, len(self.signal_data_1) - 1)
            self.end_cut_1.setRange(0, len(self.signal_data_1) - 1)
            self.end_cut_1.setValue(self.window_size_1)
            # Update spinbox ranges for another signal
            self.start_cut_2.setRange(0, len(self.signal_data_2) - 1)
            self.end_cut_2.setRange(0, len(self.signal_data_2) - 1)
            self.end_cut_2.setValue(self.window_size_2)

            self.setup_mouse_event()

            # Final drawing
            self.canvas_1.draw()
            self.canvas_2.draw()

            # Mark Rectangular page as initialized
            self.rectangular_initialized = True

    def toggle_speed(self, button):
        """
        Toggle between different playback speeds: 2x, 1x, 0.5x.
        Adjusts the step_size for smooth signal updating.
        """
        if button.text() == "1X":
            button.setText("2X")
            self.step_size = 4  # Faster, bigger step size means it skips more points
        elif button.text() == "2X":
            button.setText("0.5X")
            self.step_size = 1  # Slower, smaller step size means smoother/slower playback
        else:
            button.setText("1X")
            self.step_size = 2  # Normal speed, step size that balances speed and smoothness

    def update_rectangular_signal(self, signal_data_attr, index_attr, window_size, line_plot, ax, timer):
        """Smoothly update the signal data and plot based on step size (speed)."""
        signal_data = getattr(self, signal_data_attr, None)
        index = getattr(self, index_attr, 0)

        if signal_data is None or line_plot is None:
            timer.stop()
            print(f"Timer stopped for {line_plot} because it is not initialized.")
            return

        if index >= len(signal_data):
            timer.stop()
            self.play_pause_button_1.setText("Play ▶")
            return

        current_x_data = line_plot.get_xdata()
        current_y_data = line_plot.get_ydata()

        # Use the dynamically set step_size based on the current speed
        step_size = getattr(self, 'step_size', 2)  # Default to 2 if step_size is not set
        new_x_data = np.append(current_x_data, np.arange(index, index + step_size))  # Append multiple points
        new_y_data = np.append(current_y_data,
                               signal_data[index:index + step_size])  # Append the corresponding signal data

        if len(new_x_data) > window_size:
            new_x_data = new_x_data[-window_size:]
            new_y_data = new_y_data[-window_size:]
            ax.set_xlim(new_x_data[0], new_x_data[0] + window_size)

        line_plot.set_xdata(new_x_data)
        line_plot.set_ydata(new_y_data)
        ax.relim()
        ax.autoscale_view()

        # Update both canvases
        self.canvas_1.draw_idle()
        self.canvas_2.draw_idle()

        setattr(self, index_attr, index + step_size)  # Move forward by step_size

    def toggle_add_rectangular_graph(self, button):
        """Toggle between adding/removing the second signal graph."""

        if not self.is_second_graph_active:  # Add the second graph (Rectangular Signal 2)
            button.setText("Remove Graph")
            self.play_pause_button_2.show()
            self.merge_button.show()
            self.glue_button.show()
            self.unified_play_pause_button.show()
            self.is_second_graph_active = True
            self.canvas_2.show()
            self.horizontal_slider_2.show()
            # self.interpolation_method.show()
            # Clear the entire figure to remove previous plots and labels
            self.figure_1.clear()

            # Create new subplots for ax1 and ax2
            self.ax1 = self.figure_1.add_subplot(111)  # Resize ax1 to take the top half
            self.ax2 = self.figure_2.add_subplot(111)  # Create the second plot in the lower half

            # Set up the properties for ax1 and ax2
            self.ax1.set_xlim(0, self.window_size_1)
            self.ax1.set_ylim(np.min(self.signal_data_1), np.max(self.signal_data_1))
            self.line_plot_1, = self.ax1.plot([], [], color=self.plot_color)
            self.line_plot_1.set_antialiased(True)

            self.ax1.set_facecolor(self.backface_color)
            self.ax1.minorticks_on()
            self.ax1.grid(True, which='minor', color='lightgray', linestyle=':', linewidth=0.5, alpha=0.5)
            self.ax1.set_title("Rectangular Signal", color=self.label_color)
            self.ax1.set_xlabel("Time (s)", color=self.label_color)
            self.ax1.set_ylabel("Amplitude (µV)", color=self.label_color)
            self.ax1.tick_params(colors=self.label_color)

            self.ax2.set_xlim(0, self.window_size_2)
            self.ax2.set_ylim(np.min(self.signal_data_2), np.max(self.signal_data_2))
            self.line_plot_2, = self.ax2.plot([], [], color=self.plot_color)
            self.ax2.set_facecolor(self.backface_color)
            self.ax2.minorticks_on()
            self.ax2.grid(True, which='minor', color='lightgray', linestyle=':', linewidth=0.5, alpha=0.5)
            self.ax2.set_title("Rectangular Signal 2", color=self.label_color)
            self.ax2.set_xlabel("Time (s)", color=self.label_color)
            self.ax2.set_ylabel("Amplitude (µV)", color=self.label_color)
            self.ax2.tick_params(colors=self.label_color)

        else:  # Remove the second graph and make ax1 take up the full figure
            if self.is_merged:
                self.toggle_merge_signals(checked=False, signal_1_label="Rectangular Signal",
                                          signal_2_label="Rectangular Signal 2")
            if self.is_glued:
                self.toggle_glue_unglue(checked=False)

            # Update button text
            button.setText("Add Graph")
            self.play_pause_button_2.hide()
            self.merge_button.hide()
            self.glue_button.hide()
            self.unified_play_pause_button.hide()
            self.is_second_graph_active = False
            self.horizontal_slider_2.hide()

            # Clear both figures
            self.figure_1.clear()
            self.figure_2.clear()

            # Recreate the first graph in full size (ax1 takes the entire figure)
            self.ax1 = self.figure_1.add_subplot(111)  # Recreate ax1 to take the whole figure
            self.line_plot_1, = self.ax1.plot(self.signal_data_1[:self.window_size_1], color=self.label_color)
            self.ax1.set_facecolor(self.backface_color)
            self.ax1.minorticks_on()
            self.ax1.grid(True, which='minor', color='lightgray', linestyle=':', linewidth=0.5, alpha=0.5)
            self.ax1.set_title("Rectangular Signal", color=self.label_color)
            self.ax1.set_xlabel("Time (s)", color=self.label_color)
            self.ax1.set_ylabel("Amplitude (µV)", color=self.label_color)
            self.ax1.tick_params(colors=self.label_color)

            # Resize the first canvas to take up the full available space
            self.canvas_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.canvas_1.updateGeometry()

            # Hide the second canvas
            self.canvas_2.hide()

        # Redraw the canvas to reflect the changes in the figure
        self.canvas_1.draw()
        self.reset_rectangular_signals()

    def scroll_horizontal(self, axis, value):
        """Adjust the x-axis limits for horizontal scrolling for the specified axis."""
        window_size = 400
        if axis == 'ax1':
            # Adjust x-axis for ax1
            self.ax1.set_xlim(value, value + window_size)
        elif axis == 'ax2':
            # Adjust x-axis for ax2
            self.ax2.set_xlim(value, value + window_size)

        # Redraw the canvas to reflect changes
        self.canvas_1.draw()
        self.canvas_2.draw()

    def adjust_speed(self, value):
        """
        Adjust the playback speed based on the slider value.
        A lower value makes the playback faster, and a higher value makes it slower.
        """
        # Map slider value to timer interval (e.g., 1-100 slider range to 10-500 ms timer interval)
        speed_factor = 500 - (value * 4.9)  # Invert the value for timer interval adjustment
        self.timer_1.setInterval(speed_factor)
        self.timer_2.setInterval(speed_factor)
        # self.glued_timer.setInterval(speed_factor)

    '''def toggle_speed(self, button):
        if button.text() == "1X":
            button.setText = "2X"
        elif button.text() == "2X":
            button.setText = "0.5X"
        else:
            button.setText = "1X"'''

    '''def update_rectangular_signal(self, signal_data_attr, index_attr, window_size, line_plot, ax, timer):
        """Smoothly update the signal data and plot."""
        signal_data = getattr(self, signal_data_attr, None)
        index = getattr(self, index_attr, 0)

        if signal_data is None or line_plot is None:
            timer.stop()
            print(f"Timer stopped for {line_plot} because it is not initialized.")
            return

        if index >= len(signal_data):
            timer.stop()
            self.play_pause_button_1.setText("Play ▶")
            return

        current_x_data = line_plot.get_xdata()
        current_y_data = line_plot.get_ydata()

        step_size = 2  # Increase this to control how much data you "skip" forward
        new_x_data = np.append(current_x_data, np.arange(index, index + step_size))  # Append multiple points
        new_y_data = np.append(current_y_data,
                               signal_data[index:index + step_size])  # Append the corresponding signal data

        if len(new_x_data) > window_size:
            new_x_data = new_x_data[-window_size:]
            new_y_data = new_y_data[-window_size:]
            ax.set_xlim(new_x_data[0], new_x_data[0] + window_size)

        line_plot.set_xdata(new_x_data)
        line_plot.set_ydata(new_y_data)
        ax.relim()
        ax.autoscale_view()

        self.canvas_1.draw_idle()
        self.canvas_2.draw_idle()

        setattr(self, index_attr, index + step_size)  # Move forward by step_size'''

    def reset_rectangular_signals(self):
        """Reset the signal plots and restart the playback from the beginning."""

        # 1. Stop the timers to halt any ongoing playback
        self.timer_1.stop()
        self.timer_2.stop()

        # 2. Reset the indices to start from the beginning
        self.index_1 = 0
        self.index_2 = 0
        self.glued_index = 0  # Reset glued index if using it

        # 3. Clear the current data in the plots (for both signals)
        if hasattr(self, 'line_plot_1'):  # Clear Rectangular signal plot
            self.line_plot_1.set_data([], [])

        # Reset the x-axis for the first plot to start from 0
        if hasattr(self, 'ax1'):
            self.ax1.set_xlim(0, self.window_size_1)
            self.ax1.set_ylim(np.min(self.signal_data_1), np.max(self.signal_data_1))

        # Check if the second graph is active before resetting it
        if self.is_second_graph_active and hasattr(self, 'line_plot_2'):
            self.line_plot_2.set_data([], [])  # Clear Rectangular signal 2 plot
            self.ax2.set_xlim(0, self.window_size_2)
            self.ax2.set_ylim(np.min(self.signal_data_2), np.max(self.signal_data_2))
            self.ax2.relim()
            self.ax2.autoscale_view()

        # Handle the glued signal reset
        if hasattr(self, 'glued_line_plot'):
            self.glued_line_plot.set_data([], [])  # Clear glued signal plot
            if hasattr(self, 'ax1'):
                self.ax1.set_xlim(0, self.glued_window_size)
                self.ax1.set_ylim(np.min(self.glued_signal_data), np.max(self.glued_signal_data))
                self.ax1.relim()
                self.ax1.autoscale_view()

        # 4. Redraw the axes for the first plot
        if hasattr(self, 'ax1'):
            self.ax1.relim()
            self.ax1.autoscale_view()

        # Redraw the canvas after resetting
        self.canvas_1.draw_idle()

        # 5. Reset the play/pause button text to "Play"
        self.play_pause_button_1.setText("Play ▶")
        self.play_pause_button_2.setText("Play ▶")
        self.unified_play_pause_button.setText("Play Both ▶")

        print("Signal plots and axes have been reset.")

    def toggle_play_pause_rectangular_signal(self, timer, button):

        if timer.isActive():
            timer.stop()
            button.setText("Play ▶")
        else:
            timer.start(50)
            button.setText("Pause")

        # Update unified button status based on the states of both timers
        self.update_unified_play_pause_button()

    def toggle_unified_play_pause(self, button):
        """Toggle play/pause for both signals simultaneously."""
        if self.timer_1.isActive() or self.timer_2.isActive():
            # Pause both timers
            self.timer_1.stop()
            self.timer_2.stop()
            self.play_pause_button_1.setText("Play ▶")
            self.play_pause_button_2.setText("Play ▶")
            button.setText("Play Both ▶")
        else:
            # Play both timers
            self.timer_1.start(50)  # Adjust interval as necessary
            self.timer_2.start(50)
            self.play_pause_button_1.setText("Pause")
            self.play_pause_button_2.setText("Pause")
            button.setText("Pause Both")

    def update_unified_play_pause_button(self):
        """Update the text of the unified play/pause button based on the states of both timers."""
        if self.timer_1.isActive() and self.timer_2.isActive():
            # Both signals are playing
            self.unified_play_pause_button.setText("Pause Both")
        elif not self.timer_1.isActive() and not self.timer_2.isActive():
            # Both signals are paused
            self.unified_play_pause_button.setText("Play Both ▶")
        else:
            # One signal is playing, the other is paused
            self.unified_play_pause_button.setText("Pause")

    def merge_signals(self, signal_1_label, signal_2_label):
        """Combine both signals on the same axis (ax1) and take up the full figure."""
        # Clear both figures to remove previous plots and labels
        self.figure_1.clear()
        self.figure_2.clear()

        # Recreate the first graph in full size (ax1 takes the entire figure)
        self.ax1 = self.figure_1.add_subplot(111)  # Recreate ax1 to take the whole figure

        # Plot both signals on ax1
        self.line_plot_1, = self.ax1.plot(self.signal_data_1[:self.window_size_1], color='y', label=signal_1_label)
        if self.signal_data_2 is not None:
            self.line_plot_2, = self.ax1.plot(self.signal_data_2[:self.window_size_2], color=self.plot_color,
                                              label=signal_2_label)

        # Set up the axis appearance
        self.ax1.set_facecolor(self.backface_color)
        self.ax1.minorticks_on()  # Enable minor ticks
        self.ax1.grid(True, which='minor', color='lightgray', linestyle=':', linewidth=0.5, alpha=0.5)
        self.ax1.set_title(f"Combined {signal_1_label} and {signal_2_label}", color=self.label_color)
        self.ax1.set_xlabel("Time", color=self.label_color)
        self.ax1.set_ylabel("Electrical Activity", color=self.label_color)
        self.ax1.tick_params(colors=self.label_color)
        self.ax1.legend()

        # Resize the first canvas to take up the full available space
        self.canvas_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.canvas_1.updateGeometry()

        # Hide the second axis and canvas
        self.canvas_2.hide()
        self.horizontal_slider_2.hide()

        # Redraw the canvas to reflect changes
        self.canvas_1.draw()

    def unmerge_signals(self, signal_1_label, signal_2_label):
        """Restore the original unmerged state of the signals, displaying them on separate axes."""

        # Clear both figures to reset them
        self.figure_1.clear()
        self.figure_2.clear()

        # Create new subplots for ax1 and ax2
        self.ax1 = self.figure_1.add_subplot(111)  # Top subplot for signal 1
        self.ax2 = self.figure_2.add_subplot(111)  # Bottom subplot for signal 2

        # Plot the first signal on ax1
        self.line_plot_1, = self.ax1.plot(self.signal_data_1[:self.window_size_1], color=self.plot_color,
                                          label=signal_1_label)

        # Plot the second signal on ax2
        if self.signal_data_2 is not None:
            self.line_plot_2, = self.ax2.plot(self.signal_data_2[:self.window_size_2], color=self.plot_color,
                                              label=signal_2_label)

        # Configure ax1 (top subplot)
        self.ax1.set_facecolor(self.backface_color)
        self.ax1.minorticks_on()  # Enable minor ticks
        self.ax1.grid(True, which='minor', color='lightgray', linestyle=':', linewidth=0.5, alpha=0.5)
        self.ax1.set_title(signal_1_label, color=self.label_color)
        self.ax1.set_xlabel("Time (s)", color=self.label_color)
        self.ax1.set_ylabel("Electrical Activity", color=self.label_color)
        self.ax1.tick_params(colors=self.label_color)
        self.ax1.legend()

        # Configure ax2 (bottom subplot)
        self.ax2.set_facecolor(self.backface_color)
        self.ax2.minorticks_on()  # Enable minor ticks
        self.ax2.grid(True, which='minor', color='lightgray', linestyle=':', linewidth=0.5, alpha=0.5)
        self.ax2.set_title(signal_2_label, color=self.label_color)
        self.ax2.set_xlabel("Time (s)", color=self.label_color)
        self.ax2.set_ylabel("Electrical Activity", color=self.label_color)
        self.ax2.tick_params(colors=self.label_color)
        self.ax2.legend()

        # Show the second canvas and horizontal slider
        self.canvas_2.show()
        self.horizontal_slider_2.show()

        # Redraw the canvases to reflect changes
        self.canvas_1.draw()
        self.canvas_2.draw()

    def toggle_merge_signals(self, checked, signal_1_label, signal_2_label):
        """Toggle between merged and unmerged state for the signals."""

        if checked:  # Merging signals
            self.is_merged = True
            self.merge_button.setText("Unmerge Signals")
            self.merge_signals(signal_1_label, signal_2_label)
            self.signals_merged = True  # Track the merge state
            self.glue_button.hide()
        else:  # Unmerging signals
            self.is_merged = False
            self.merge_button.setText("Merge Signals")
            self.unmerge_signals(signal_1_label, signal_2_label)
            self.signals_merged = False  # Track the unmerged state
            self.glue_button.show()

        # Now reset the signals after the merge/unmerge operation
        self.reset_rectangular_signals()

    def glue_signals(self):
        """Glue the segments from both signals and interpolate using the average method."""

        # Get the start/end indices from the spinboxes for both signals
        start_1 = self.start_cut_1.value()
        end_1 = self.end_cut_1.value()
        start_2 = self.start_cut_2.value()
        end_2 = self.end_cut_2.value()

        # Extract the segments from both signals
        part_1 = self.signal_data_1[start_1:end_1]
        part_2 = self.signal_data_2[start_2:end_2]

        # Initialize interpolated values
        interp_values = []

        if end_1 >= start_2:  # Overlap case
            overlap_length = end_1 - start_2
            overlap_length = min(overlap_length, len(part_1), len(part_2))

            # Ensure overlap sections match in length
            overlap_part_1 = part_1[-overlap_length:]
            overlap_part_2 = part_2[:overlap_length]

            # Calculate the average for each overlapping point
            interp_values = (overlap_part_1 + overlap_part_2) / 2

            # Remove the overlapping parts from part_1 and part_2
            part_1 = part_1[:-overlap_length]
            part_2 = part_2[overlap_length:]

        else:  # Gap case
            gap_length = start_2 - end_1
            interp_values = np.linspace(part_1[-1], part_2[0], gap_length)

        # Concatenate the segments with the interpolated section
        glued_signal = np.concatenate((part_1, interp_values, part_2))

        # Store glued signal data for playback and visualization
        self.glued_signal_data = glued_signal
        self.glued_index = 0
        self.glued_window_size = 400  # Set window size for display

        # Clear both figures
        self.figure_1.clear()
        self.figure_2.clear()

        # Set up the axis for the glued signal in ax1, taking up the whole space
        self.ax1 = self.figure_1.add_subplot(111)
        self.ax1.set_xlim(0, self.glued_window_size)
        self.ax1.set_ylim(np.min(glued_signal), np.max(glued_signal))

        # Plot Signal 1 Part
        self.ax1.plot(np.arange(start_1, start_1 + len(part_1)), part_1, color='b', label='Signal 1 Part')

        # Plot Interpolated section
        if len(interp_values) > 0:
            interp_x = np.arange(start_1 + len(part_1), start_1 + len(part_1) + len(interp_values))
            color = 'orange' if end_1 >= start_2 else 'red'
            label = 'Overlap (Average)' if end_1 >= start_2 else 'Gap (Average)'
            self.ax1.plot(interp_x, interp_values, color=color, label=label)

        # Plot Signal 2 Part
        part_2_x = np.arange(start_1 + len(part_1) + len(interp_values),
                             start_1 + len(part_1) + len(interp_values) + len(part_2))
        self.ax1.plot(part_2_x, part_2, color='g', label='Signal 2 Part')

        # Configure plot appearance
        self.ax1.set_facecolor(self.backface_color)
        self.ax1.minorticks_on()
        self.ax1.grid(True, which='minor', color='lightgray', linestyle=':', linewidth=0.5, alpha=0.5)
        self.ax1.set_title("Glued Signal with Average Interpolation", color=self.label_color)
        self.ax1.set_xlabel("Time", color=self.label_color)
        self.ax1.set_ylabel("Amplitude (µV)", color=self.label_color)
        self.ax1.legend(facecolor='black', edgecolor=self.label_color, framealpha=1)
        self.ax1.tick_params(colors=self.label_color)

        # Hide the second canvas and redraw the first canvas with the glued signal
        self.canvas_2.hide()
        self.horizontal_slider_2.hide()
        self.canvas_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.canvas_1.updateGeometry()
        self.canvas_1.draw()

    def unglue_signals(self):
        """Restore the original segments of both signals and reset the view."""

        # Clear both figures
        self.figure_1.clear()
        self.figure_2.clear()

        # Restore the layout for ax1 and ax2
        self.ax1 = self.figure_1.add_subplot(111)  # Recreate ax1 to take the whole figure
        self.ax2 = self.figure_2.add_subplot(111)  # Create the second plot in the lower half

        # Plot the first signal on ax1
        self.ax1.set_xlim(0, self.window_size_1)
        self.ax1.set_ylim(np.min(self.signal_data_1), np.max(self.signal_data_1))
        self.line_plot_1, = self.ax1.plot(self.signal_data_1[:self.window_size_1], color=self.plot_color)
        self.ax1.set_facecolor(self.backface_color)
        self.ax1.minorticks_on()
        self.ax1.grid(True, which='minor', color='lightgray', linestyle=':', linewidth=0.5, alpha=0.5)
        self.ax1.set_title("Rectangular Signal", color=self.label_color)
        self.ax1.set_xlabel("Time (s)", color=self.label_color)
        self.ax1.set_ylabel("Amplitude (µV)", color=self.label_color)
        self.ax1.tick_params(colors=self.label_color)

        # Plot the second signal on ax2
        self.ax2.set_xlim(0, self.window_size_2)
        self.ax2.set_ylim(np.min(self.signal_data_2), np.max(self.signal_data_2))
        self.line_plot_2, = self.ax2.plot(self.signal_data_2[:self.window_size_2], color=self.plot_color)
        self.ax2.set_facecolor(self.backface_color)
        self.ax2.minorticks_on()
        self.ax2.grid(True, which='minor', color='lightgray', linestyle=':', linewidth=0.5, alpha=0.5)
        self.ax2.set_title("Rectangular Signal 2", color=self.label_color)
        self.ax2.set_xlabel("Time (s)", color=self.label_color)
        self.ax2.set_ylabel("Amplitude (µV)", color=self.label_color)
        self.ax2.tick_params(colors=self.label_color)

        # Restore visibility and layout of the second canvas and slider
        self.canvas_2.show()
        self.horizontal_slider_2.show()

        # Resize the canvases to take their original space
        self.canvas_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.canvas_1.updateGeometry()

        # Redraw the canvases
        self.canvas_1.draw()
        self.canvas_2.draw()

    def toggle_glue_unglue(self, checked):
        """Toggle between glued and unglued states for the signals."""
        if not self.is_glued and checked:
            # Reset only when transitioning from unglued to glued state
            self.reset_rectangular_signals()

        if checked:
            # If the button is checked, glue the signals
            self.is_glued = True
            self.stop_signal()  # Stop any currently playing signals
            self.glue_signals()
            self.merge_button.hide()
            self.replace_signal_button.hide()
            self.unified_play_pause_button.hide()
            self.speed_button.hide()
            self.reset_button.hide()

            # Update the button text to "Unglue"
            self.glue_button.setText("Unglue")
        else:
            # If the button is unchecked, unglue the signals
            self.is_glued = False
            self.stop_signal()  # Stop any ongoing playback
            self.unglue_signals()
            self.merge_button.show()
            self.unified_play_pause_button.show()
            self.replace_signal_button.show()
            self.speed_button.show()
            self.reset_button.show()
            # Update the button text to "Glue"
            self.glue_button.setText("Glue")

    def load_signal_data(self, file_path, signal_data_attr, index_attr):
        """Load the signal data into the appropriate variable."""
        _, file_extension = os.path.splitext(file_path)

        if file_extension == ".txt":
            setattr(self, signal_data_attr, np.loadtxt(file_path))

        elif file_extension == ".csv":
            # Load the entire CSV file, assuming the signal is in the second column
            data = np.loadtxt(file_path, delimiter=',',
                              skiprows=1)  # Assuming there's a header, adjust skiprows if necessary
            signal_data = data[:, 1]  # Select the second column (index 1)
            setattr(self, signal_data_attr, signal_data)

        elif file_extension == ".edf":
            # Use pyEDFlib to read the EDF file
            f = pyedflib.EdfReader(file_path)
            n_signals = f.signals_in_file
            signal_data = np.zeros((n_signals, f.getNSamples()[0]))

            for i in range(n_signals):
                signal_data[i, :] = f.readSignal(i)

            setattr(self, signal_data_attr, signal_data)
            f.close()

        setattr(self, index_attr, 0)  # Reset index for the signal

    def load_signal_file(self, load_signal_data_callback):
        """Open a file dialog to select a file and load the signal data."""
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Load Signal File", "",
                                                             "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)",
                                                             options=options)
        if file_path:
            load_signal_data_callback(file_path)
            if not hasattr(self, 'circular_initialized'):
                self.reset_rectangular_signals()

    def pause_signal(self, timer):
        """Stop the timer to pause the signal animation."""
        timer.stop()

    def stop_signal(self):
        # Pause both timers to stop signal animation (check if they exist)
        if hasattr(self, 'timer_1'):
            self.pause_signal(self.timer_1)
        if hasattr(self, 'timer_2'):
            self.pause_signal(self.timer_2)

        # Manually reset button texts to 'Play ▶' if buttons exist
        if hasattr(self, 'play_pause_button_1'):
            self.play_pause_button_1.setText("Play ▶")
        if hasattr(self, 'play_pause_button_2'):
            self.play_pause_button_2.setText("Play ▶")

    def open_reprot_page(self):
        report_data = ReportDialog(self)
        report_data.exec_()

    '''---------------------------------------------------------------------------------------------------------------------------------------'''

    def initialize_RTS_graph(self, content_widget, signal_1_button,
                             get_rectangular_report_button, signal_1_label="Signals"):
        # Set up the canvas for plotting signals
        self.figure = Figure(figsize=(8, 6), dpi=100,
                             facecolor=self.fig_color,  # Canvas background color
                             edgecolor='blue', frameon=True)
        self.canvas = FigureCanvas(self.figure)

        content_widget.setGeometry(0, 80, 1280, 720)
        content_widget.setFixedHeight(720)
        # Create a vertical layout for the content and add the canvas
        layout = QtWidgets.QHBoxLayout(content_widget)
        layout.addWidget(self.canvas)

        # Create a horizontal layout for buttons
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setSpacing(30)  # Adjust spacing between buttons

        # Set up the font
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(17)

        # Add Play/Pause buttons for both signals
        signal_1_button.setFixedSize(150, 40)
        signal_1_button.setFont(font)  # Set Times New Roman font
        signal_1_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        signal_1_button.setStyleSheet("background-color: rgb(36,36,36); color: white;")
        signal_1_button.clicked.connect(
            lambda: self.toggle_play_pause_RTS_signal(self.timer_1, signal_1_button))
        button_layout.addWidget(signal_1_button)

        # Store play/pause buttons for later use in other methods
        self.play_pause_button_1 = signal_1_button

        # Add Replace Signal button
        get_rectangular_report_button.setFixedSize(150, 40)
        get_rectangular_report_button.setFont(font)  # Set Times New Roman font
        get_rectangular_report_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        get_rectangular_report_button.setStyleSheet("background-color: rgb(36,36,36); color: white;")
        get_rectangular_report_button.clicked.connect(self.open_reprot_page)
        button_layout.addWidget(get_rectangular_report_button)

        # Add the button layout to the main layout
        layout.addLayout(button_layout)

        # Add back button using the add_back_button function
        back_button = self.add_back_button(content_widget)
        back_button.setFont(font)  # Set Times New Roman font
        back_button.clicked.connect(self.handle_back_button)
        button_layout.addWidget(back_button)

    def setup_RTS_page(self):
        if not hasattr(self, 'rts_initialized') or not self.rts_initialized:
            print("Setting up RTS page...")  # Debug

            # Create buttons for the RTS page
            play_pause_button_1 = QtWidgets.QPushButton("Play ▶", self.RTS_content)
            get_rectangular_report_button = QtWidgets.QPushButton("Get Report", self.RTS_content)

            # merge_button = QtWidgets.QPushButton("Merge", self.RTS_content)
            # glue_button = QtWidgets.QPushButton("Glue", self.RTS_content)

            # Call initialize_rectangular_graph with Rectangular-specific buttons and content
            self.initialize_RTS_graph(
                content_widget=self.RTS_content,
                signal_1_button=play_pause_button_1,
                get_rectangular_report_button=get_rectangular_report_button
            )

            self.timer_1 = QtCore.QTimer()

            self.timer_1.timeout.connect(
                lambda: self.update_RTS_signal('signal_data_1', 'index_1', self.window_size_1, self.line_plot_1,
                                               self.ax1,
                                               self.timer_1))

            # Create the subplots for Rectangular (Signal 1) and ECG (Signal 2)
            self.ax1 = self.figure.add_subplot(111)
            # Instantiate MplZoomHelper for the axis
            # MplZoomHelper(self.ax1)
            # Load and initialize Rectangular signal data
            filename = 'Data/RTS Data/RTS_data.txt'
            self.signal_data_1 = np.loadtxt(filename)
            self.index_1 = 0
            with open('Data/RTS Data/RTS_data.txt', 'r') as file:
                sum = 0
                for line in file:
                    sum += 1
            self.window_size_1 = sum
            self.line_plot_1, = self.ax1.plot(self.signal_data_1[:self.window_size_1], color=self.plot_color)
            self.ax1.tick_params(colors=self.label_color)

            self.ax1.minorticks_on()  # Enable minor ticks
            self.ax1.grid(True, which='minor', color='lightgray', linestyle=':', linewidth=0.5, alpha=0.5)
            self.ax1.set_facecolor(self.backface_color)
            self.ax1.set_title("Signal")
            self.ax1.set_xlabel("Time")
            self.ax1.set_ylabel("Y(t)")

            self.setup_mouse_events()

            # Draw the canvas after initial setup
            self.canvas.draw()

            # Mark RTS page as initialized
            self.rts_initialized = True
            # Install event filter for scrolling

    def update_RTS_signal(self, signal_data_attr, index_attr, window_size, line_plot, ax, timer):
        self.update_RTS_data()  # Fetch new data
        # Reload the signal data from the file to ensure we have the latest data
        signal_data = np.loadtxt('Data/RTS Data/RTS_data.txt')
        setattr(self, signal_data_attr, signal_data)  # Update the attribute with new data

        index = getattr(self, index_attr)

        signal_data = getattr(self, signal_data_attr)
        index = getattr(self, index_attr)

        if signal_data is not None:
            # Ensure we do not exceed the length of the signal data
            if index + window_size >= len(signal_data):
                timer.stop()  # Stop if we reach the end
                return

            # Prepare the x and y data
            x_data = np.arange(index, index + window_size)
            y_data = signal_data[index:index + window_size]

            # Check lengths
            if len(x_data) != len(y_data):
                print(f"Length mismatch: x_data={len(x_data)}, y_data={len(y_data)}")
                return

            # Update the plot
            line_plot.set_xdata(x_data)
            line_plot.set_ydata(y_data)

            ax.relim()
            ax.autoscale_view()

            # Redraw only the updated line
            self.canvas.draw_idle()

            # Update the index attribute
            setattr(self, index_attr, index + 1)  # Increment index

    def update_RTS_plot(self, val):
        start = int(self.start_slider.val)
        end = int(self.end_slider.val)

        # Update the plot based on slider values
        if end > start and end <= self.window_size_1:
            self.line_plot_1.set_xdata(np.arange(start, end))
            self.line_plot_1.set_ydata(self.signal_data_1[start:end])

            self.ax1.relim()
            self.ax1.autoscale_view()
            self.canvas.draw_idle()

    def get_real_time_data(self):
        """Fetch real-time data from the Weather API and return current time and temperature."""
        url = "https://api.weatherapi.com/v1/current.json?key=135b4139f4fc40a48ba202601240910&q=egypt&aqi=no"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            temp_c = data['current']['temp_c']

            return temp_c
        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)
            return None

    def update_RTS_data(self):
        """Fetch and update RTS signal data."""
        temp_c = self.get_real_time_data()

        if temp_c is not None:  # Ensure we have valid temperature data
            temp = self.fix_decimal_format(str(temp_c))
            with open('Data/RTS Data/RTS_data.txt', 'a') as file:
                file.write(str(temp) + '\n')
        else:
            print("Failed to update RTS signal.")

    def fix_decimal_format(self, number_str):
        # Split the number string by the decimal point
        parts = number_str.split('.')

        # If there are more than two parts, combine the first two parts with a single decimal point
        if len(parts) > 2:
            number_str = parts[0] + '.' + ''.join(parts[1:])

        return number_str

    def toggle_play_pause_RTS_signal(self, timer, button):
        """Toggle between playing and pausing a signal."""
        # Handle individual signals
        if button.text() == "Play ▶":
            self.play_signal(timer)
            button.setText("Pause")
        else:
            self.pause_signal(timer)
            button.setText("Play ▶")

    def play_signal(self, timer):
        """Start the timer to play the signal animation."""
        timer.start(50)  # Update every 50 ms

    def on_click(self, event, ax, canvas, signal_data):
        setattr(self, 'start', 1)
        setattr(self, 'end', self.window_size_1)

        if event.button == 1:  # Left-click (Zoom In)
            self.factor += 0.2
            self.start *= self.factor
            self.end *= self.factor

            self.start = max(0, min(int(self.start), len(signal_data) - 1))
            self.end = max(0, min(int(self.end), len(signal_data)))

            x_data = np.arange(int(self.start), int(self.end))
            y_data = signal_data[int(self.start):int(self.end)]

            if len(x_data) != len(y_data):
                print(f"Shape mismatch: x_data length = {len(x_data)}, y_data length = {len(y_data)}")
                return

            ax.lines[0].set_xdata(x_data)
            ax.lines[0].set_ydata(y_data)
            ax.relim()
            ax.autoscale_view()
            canvas.draw_idle()

        elif event.button == 3:  # Right-click (Zoom Out)
            self.factor -= 0.2
            self.start *= self.factor
            self.end *= self.factor

            x_data = np.arange(int(self.start), int(self.end))
            y_data = signal_data[int(self.start):int(self.end)]

            if len(x_data) != len(y_data):
                print(f"Shape mismatch: x_data length = {len(x_data)}, y_data length = {len(y_data)}")
                return

            ax.lines[0].set_xdata(x_data)
            ax.lines[0].set_ydata(y_data)
            ax.relim()
            ax.autoscale_view()
            canvas.draw_idle()

    def setup_mouse_events(self):
        """Setup mouse events for both canvases."""
        if hasattr(self, 'canvas_1') and hasattr(self, 'canvas_2'):
            # Setup mouse events for ax1 (canvas_1)
            self.canvas_1.mpl_connect('button_press_event',
                                      lambda event: self.on_click(event, self.ax1, self.canvas_1, self.signal_data_1))

            # Setup mouse events for ax2 (canvas_2)
            self.canvas_2.mpl_connect('button_press_event',
                                      lambda event: self.on_click(event, self.ax2, self.canvas_2, self.signal_data_2))

    def on_click02(self, event, ax, canvas, signal_data):
        """Handle mouse click events for zooming in and out for both axes."""
        if event.button == 1:  # Left-click (Zoom In)
            zoom_factor = 0.8
            xlim = ax.get_xlim()
            new_xlim = [
                max(0, (xlim[0] + (xlim[1] - xlim[0]) * (1 - zoom_factor)) / 2),
                min(len(signal_data), xlim[1] - (xlim[1] - xlim[0]) * (1 - zoom_factor) / 2)
            ]
            ax.set_xlim(new_xlim)
            ax.relim()
            ax.autoscale_view()
            canvas.draw_idle()

        elif event.button == 3:  # Right-click (Zoom Out)
            zoom_factor = 1.2
            xlim = ax.get_xlim()
            new_xlim = [
                max(0, (xlim[0] + (xlim[1] - xlim[0]) * (1 - zoom_factor)) / 2),
                min(len(signal_data), xlim[1] - (xlim[1] - xlim[0]) * (1 - zoom_factor) / 2)
            ]
            ax.set_xlim(new_xlim)
            ax.relim()
            ax.autoscale_view()
            canvas.draw_idle()

    def on_release(self, event, ax, canvas):
        """Handle mouse release events for both axes."""
        if event.button == 1:
            self.is_panning = False
            self.last_mouse_x = None

    def on_mouse_move(self, event, ax, canvas, signal_data):
        pass
        """Handle mouse movement events for panning on both axes."""
        '''if self.is_panning and self.last_mouse_x is not None:
            dx = event.xdata - self.last_mouse_x
            xlim = ax.get_xlim()
            new_xlim = [xlim[0] - dx, xlim[1] - dx]

            new_xlim[0] = max(0, new_xlim[0])
            new_xlim[1] = min(len(signal_data), new_xlim[1])

            ax.set_xlim(new_xlim)
            ax.relim()
            ax.autoscale_view()
            canvas.draw_idle()

            self.last_mouse_x = event.xdata'''

    def setup_mouse_event(self):
        """Setup mouse events for panning and zooming for both canvases."""
        if hasattr(self, 'canvas_1') and hasattr(self, 'canvas_2'):
            # Setup for ax1 (canvas_1)
            self.canvas_1.mpl_connect('button_press_event',
                                      lambda event: self.on_click02(event, self.ax1, self.canvas_1, self.signal_data_1))
            self.canvas_1.mpl_connect('button_release_event',
                                      lambda event: self.on_release(event, self.ax1, self.canvas_1))
            self.canvas_1.mpl_connect('motion_notify_event',
                                      lambda event: self.on_mouse_move(event, self.ax1, self.canvas_1,
                                                                       self.signal_data_1))

            # Setup for ax2 (canvas_2)
            self.canvas_2.mpl_connect('button_press_event',
                                      lambda event: self.on_click02(event, self.ax2, self.canvas_2, self.signal_data_2))
            self.canvas_2.mpl_connect('button_release_event',
                                      lambda event: self.on_release(event, self.ax2, self.canvas_2))
            self.canvas_2.mpl_connect('motion_notify_event',
                                      lambda event: self.on_mouse_move(event, self.ax2, self.canvas_2,
                                                                       self.signal_data_2))

    '''---------------------------------------------------------------------------------------------------------------------------------------'''

    def setup_circular_page(self):
        if not hasattr(self, 'circular_initialized') or not self.circular_initialized:
            print("Setting up Circular page...")  # Debug

            # Create buttons for the Circular page
            circular_play_button = QtWidgets.QPushButton("Play ▶", self.circular_content)
            replace_signal_button = QtWidgets.QPushButton("Replace Signal", self.circular_content)
            set_color_button = QtWidgets.QPushButton("Set Color", self.circular_content)

            self.figure = Figure(figsize=(8, 6), dpi=100, facecolor=self.fig_color, edgecolor='blue', frameon=True)
            self.canvas = FigureCanvas(self.figure)

            # Create a vertical layout for the content and add the canvas
            layout = QtWidgets.QHBoxLayout(self.circular_content)
            layout.addWidget(self.canvas)

            # Create a horizontal layout for buttons
            circular_button_layout = QtWidgets.QVBoxLayout()
            circular_button_layout.setSpacing(30)  # Adjust spacing between buttons

            # Set up the font
            font = QtGui.QFont()
            font.setFamily("Times New Roman")
            font.setPointSize(17)

            # Add Play/Pause button
            circular_play_button.setFixedSize(150, 40)
            circular_play_button.setFont(font)
            circular_play_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            circular_play_button.setStyleSheet("background-color: rgb(36,36,36); color: white;")
            circular_play_button.clicked.connect(lambda: self.toggle_play_pause_circular_signal(circular_play_button))
            circular_button_layout.addWidget(circular_play_button)
            self.circular_play_button = circular_play_button  # Store for later use

            # Add Replace Signal button
            replace_signal_button.setFixedSize(150, 40)
            replace_signal_button.setFont(font)
            replace_signal_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            replace_signal_button.setStyleSheet("background-color: rgb(36,36,36); color: white;")
            replace_signal_button.clicked.connect(self.replace_signal)
            circular_button_layout.addWidget(replace_signal_button)

            # Add Set Color Signal button
            set_color_button.setFixedSize(150, 40)
            set_color_button.setFont(font)
            set_color_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            set_color_button.setStyleSheet("background-color: rgb(36,36,36); color: white;")
            set_color_button.clicked.connect(self.open_color_picker)  # This function opens the color picker
            circular_button_layout.addWidget(set_color_button)

            # Add button layout to main layout
            layout.addLayout(circular_button_layout)

            # Add back button
            back_button = self.add_back_button(self.circular_content)
            back_button.setFont(font)
            back_button.clicked.connect(self.handle_back_button)
            circular_button_layout.addWidget(back_button)

            # Load data from text file
            self.load_circular_data()  # Use the new load_circular_data method here

            # Setup polar plot
            self.ax_polar = self.figure.add_subplot(111, projection='polar')
            self.line_polar, = self.ax_polar.plot([], [], lw=2)  # Initialize without data
            self.ax_polar.tick_params(colors=self.label_color)  # Tick label color
            self.ax_polar.set_yticklabels([])  # Remove radius labels
            self.line_polar.set_color(self.plot_color)  # Update line color
            self.ax_polar.set_facecolor(self.graph_color)  # Update background color

            # Define the init_polar function here and assign it to self.init_polar
            def init_polar():
                self.line_polar.set_data([], [])  # Initially, no data
                return self.line_polar,

            self.init_polar = init_polar  # Assign the function to self.init_polar

            # Draw the canvas after initial setup
            self.canvas.draw()

            # Mark Circular page as initialized
            self.circular_initialized = True

    def toggle_play_pause_circular_signal(self, button):
        """Toggle the play/pause state of the circular animation."""
        if button.text() == "Play ▶":
            # Create the animation only when play is pressed for the first time
            if not hasattr(self, 'ani_polar'):
                def update_polar(frame):
                    # Animate using the loaded data from the text file
                    # Ensure that the entire dataset is used, not just part of it
                    current_theta = self.theta[:frame + 1]  # Incrementally update theta
                    current_r = self.r[:frame + 1]  # Incrementally update radius

                    self.line_polar.set_data(current_theta, current_r)

                    # Set colors right before drawing
                    self.line_polar.set_color(self.plot_color)  # Update line color
                    self.ax_polar.set_facecolor(self.graph_color)  # Update background color

                    # Force redraw of the canvas
                    self.canvas.draw()

                    return self.line_polar,

                # Ensure that the animation runs over the entire length of the dataset
                self.ani_polar = FuncAnimation(self.figure, update_polar, frames=len(self.theta),
                                               init_func=self.init_polar, blit=True, interval=100)

            self.ani_polar.event_source.start()
            self.is_animating = True  # Set animation state to true
            button.setText("Pause")
        else:
            self.ani_polar.event_source.stop()
            self.is_animating = False  # Set animation state to false
            button.setText("Play ▶")

    def update_circular_plot(self):
        """Update the circular plot with new data and animate it point by point."""
        print("Update Circular Plot called")

        if hasattr(self, 'ax_polar'):
            print("Clearing the figure and recreating the plot")

            # Clear the entire figure and recreate the polar plot
            self.figure.clear()

            # Recreate the polar axis
            self.ax_polar = self.figure.add_subplot(111, projection='polar')

            # Reinitialize the line plot with empty data
            self.line_polar, = self.ax_polar.plot([], [], lw=2)

            # Restore plot settings (colors, labels, etc.)
            self.ax_polar.set_facecolor(self.graph_color)
            self.line_polar.set_color(self.plot_color)
            self.ax_polar.tick_params(colors=self.label_color)
            self.ax_polar.set_yticklabels([])  # Remove radius labels

            # Define the animation update function
            def update_polar(frame):
                """Update function for the animation, adding points incrementally."""

                # Avoid clearing the figure here to prevent flashing issues
                current_theta = self.theta[:frame]  # Get theta points up to the current frame
                current_r = self.r[:frame]  # Get radius points up to the current frame

                # Update the line plot with the new points
                self.line_polar.set_data(current_theta, current_r)

                # Make sure the canvas is redrawn after each update
                self.canvas.draw_idle()

                return self.line_polar,

            # Define the initialization function for the animation
            def init_polar():
                """Initializes the polar plot for the animation."""
                self.line_polar.set_data([], [])  # Set the line data to empty for initialization
                return self.line_polar,  # Return the line as a sequence (tuple)

            # Ensure the animation is stored and run properly
            if hasattr(self, 'ani_polar'):
                self.ani_polar.event_source.stop()  # Stop any previous animation

            # Create a new animation instance and store it
            self.ani_polar = FuncAnimation(self.figure, update_polar, frames=len(self.theta),
                                           init_func=init_polar, blit=False, interval=150)

            # Redraw the canvas initially to reflect the starting state
            self.canvas.draw_idle()

            # Start the animation immediately after replacing the signal
            self.ani_polar.event_source.start()

    def load_circular_data(self):
        """Load circular data from the default circular data file."""
        file_path = 'Data/Circular Data/antenna_radiation_pattern.txt'

        try:
            # Load the data from the file (assuming it's in two columns: theta and radius)
            data = np.loadtxt(file_path, delimiter=",")
            # Separate theta and radius (columns 0 and 1)
            self.theta = data[:, 0]  # Angles in radians
            self.r = data[:, 1]  # Radius values
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            # Fallback to some default data if the file isn't found
            self.theta = np.linspace(0, 2 * np.pi, 100)
            self.r = np.sin(self.theta)  # Example: simple sine wave
            print("Loaded default circular data")

    def replace_signal(self):
        # Check if we're on the circular page
        if hasattr(self, 'circular_initialized') and self.circular_initialized:
            # Load circular signal
            self.load_signal_file(lambda file_path: self.load_circular_data_from_file(file_path))
        else:
            # Check if we're on a rectangular signal page
            if self.is_second_graph_active:
                # Create and show the custom ReplaceSignalDialog
                dialog = ReplaceSignalDialog(self.centralwidget)
                result = dialog.exec_()

                if result == QDialog.Accepted:
                    if dialog.selected_signal == 1:
                        # Replace Signal 1 (Rectangular)
                        self.load_signal_file(
                            lambda file_path: self.load_signal_data(file_path, 'signal_data_1', 'index_1'))
                    elif dialog.selected_signal == 2:
                        # Replace Signal 2 (Rectangular)
                        self.load_signal_file(
                            lambda file_path: self.load_signal_data(file_path, 'signal_data_2', 'index_2'))
                else:
                    print("Signal replacement canceled")
            else:
                # Default behavior: replace the first rectangular signal (Rectangular)
                self.load_signal_file(
                    lambda file_path: self.load_signal_data(file_path, 'signal_data_1', 'index_1'))

    def load_circular_data_from_file(self, file_path):
        """Load circular data from the specified file path."""
        data = np.loadtxt(file_path, delimiter="," )
        self.theta = data[:, 0]
        self.r = data[:, 1]
        self.update_circular_plot()

    def open_color_picker(self):
        color_dialog = ColorPickerDialog(self)
        color_dialog.exec_()

    '''---------------------------------------------------------------------------------------------------------------------------------------'''


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.showFullScreen()
    sys.exit(app.exec_())
