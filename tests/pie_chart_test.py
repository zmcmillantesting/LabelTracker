import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt


class PieChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Status Pie Chart")
        self.setGeometry(100, 100, 800, 600)
        
        # Create the pie chart
        self.create_pie_chart()
        
    def create_pie_chart(self):
        # Create pie series
        series = QPieSeries()
        
        # Add data (you can modify these values)
        pass_count = 45
        fail_count = 15
        pending_count = 20
        
        # Add slices
        slice_pass = series.append("Pass", pass_count)
        slice_fail = series.append("Fail", fail_count)
        slice_pending = series.append("Pending", pending_count)
        
        # Customize slice colors
        slice_pass.setColor(QColor(76, 175, 80))  # Green
        slice_fail.setColor(QColor(244, 67, 54))  # Red
        slice_pending.setColor(QColor(255, 193, 7))  # Yellow/Orange
        
        # Enable labels and make them more visible
        slice_pass.setLabel(f"Pass: {pass_count} ({slice_pass.percentage()*100:.1f}%)")
        slice_fail.setLabel(f"Fail: {fail_count} ({slice_fail.percentage()*100:.1f}%)")
        slice_pending.setLabel(f"Pending: {pending_count} ({slice_pending.percentage()*100:.1f}%)")
        
        slice_pass.setLabelVisible(True)
        slice_fail.setLabelVisible(True)
        slice_pending.setLabelVisible(True)
        
        # Optional: Explode a slice to highlight it
        slice_fail.setExploded(True)
        slice_fail.setExplodeDistanceFactor(0.1)
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Test Results Status")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        # Create chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        # Set up the main widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(chart_view)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


def main():
    app = QApplication(sys.argv)
    window = PieChartWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()