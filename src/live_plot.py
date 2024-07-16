import sys
import serial
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import pyqtgraph as pg

class SerialReaderThread(QThread):
    data_received = pyqtSignal(int, float)
    def __init__(self, port, baud_rate):
        super().__init__()
        self.serial_port = serial.Serial(port, baud_rate, timeout=1)
    def run(self):
        while True:
            if self.serial_port.inWaiting() > 0:
                data_line = self.serial_port.readline().decode('utf-8').strip()
                data_parts = data_line.split(' ')
                if len(data_parts) == 2:
                    try:
                        int_part = int(data_parts[0])
                        float_part = float(data_parts[1])
                        self.data_received.emit(int_part, float_part)
                    except ValueError:
                        pass

class DataWindow(QMainWindow):
    def __init__(self, title, color):
        super().__init__()
        self.setWindowTitle(title)
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(1024))
        self.y = [0 for _ in range(1024)]
        
        self.graphWidget.setBackground('w')
        self.pen = pg.mkPen(color=color)
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=self.pen)
    
    def update_plot(self, data):
        self.y = self.y[1:]
        self.y.append(data)
        self.data_line.setData(self.x, self.y)
    
    def add_constant_line(self, y_value, color):
        pen = pg.mkPen(color=color, style=Qt.DotLine, width = 3)  # 수정된 부분
        self.graphWidget.addItem(pg.InfiniteLine(angle=0, pos=y_value, pen=pen))

class MainWindow:
    def __init__(self, port, baud_rate):
        self.int_window = DataWindow("Integer Data", (255, 0, 0))
        self.float_window = DataWindow("Float Data", (0, 0, 255))
        
        self.step = 10  # step을 인스턴스 변수로 선언
        self.ten_ = 10
        self.count = 1
        self.four_count = 0
        self.in_range_count = 0
        self.data_buffer = []

        self.filter_size = 32  # Moving Average 필터 크기 설정
        self.float_data_buffer = []  # float 데이터 전용 버퍼

        # 상수값 선 초기화에 self.step 사용
        self.float_window.add_constant_line(self.step - 6, 'm')
        self.float_window.add_constant_line(self.step + 6, 'm')

        self.serial_thread = SerialReaderThread(port, baud_rate)
        self.serial_thread.data_received.connect(self.update_plots)
        self.serial_thread.start()

    def show(self):
        self.int_window.show()
        self.float_window.show()

    def update_plots(self, int_data, float_data):
        
        self.data_buffer.append((int_data, float_data))
        # 버퍼 사이즈 유지
        if len(self.data_buffer) > 3600:
            self.data_buffer.pop(0)

        # DC 제거를 위한 평균 계산
        int_avg = sum(d[0] for d in self.data_buffer) / len(self.data_buffer)
        # DC 제거 및 위상 뒤집기
        int_data_corrected = -(int_data - int_avg)
        
        # Plot 업데이트 조건 추가
        if self.four_count % 4 == 0:  # 4개의 데이터마다 한 번씩 plot
            self.int_window.update_plot(int_data_corrected)
            
            if len(self.float_data_buffer) >= self.filter_size:
                float_data_filtered = sum(self.float_data_buffer[-self.filter_size:]) / self.filter_size
            else:
                float_data_filtered = float_data  # 필터 크기보다 데이터가 적을 때는 원본 데이터 사용
            
            self.float_window.update_plot(float_data_filtered)
            
            # y축 범위 동적으로 조정
            self.float_window.graphWidget.setYRange(self.step - 15, self.step + 15)

        # 상수 선 위치 및 그래프 범위 업데이트는 여전히 계속
            if self.step - 6 <= float_data_filtered <= self.step + 6:
                self.in_range_count += 1
                if self.in_range_count >= 896:
                    self.save_data_to_file()
                    if self.count < 20:
                        self.step += self.ten_
                    else:
                        self.step -= self.ten_
                    self.in_range_count = 0
                    self.count += 1
                    
                    # 상수 선 위치 및 그래프 범위 업데이트
                    self.float_window.graphWidget.clear()
                    self.float_window.add_constant_line(self.step - 6, 'm')
                    self.float_window.add_constant_line(self.step + 6, 'm')
                    self.float_window.data_line = self.float_window.graphWidget.plot(self.float_window.x, self.float_window.y, pen=self.float_window.pen)
            else:
                self.in_range_count = 0

            if self.count == 40:
                sys.exit()
        if self.four_count == 3:
            self.four_count = 0
        else:
            self.four_count+=1
    def save_data_to_file(self):
        # 최근 3584개 데이터 추출 및 파일 저장
        formatted_data = ["{},{}".format(data[0], data[1]) for data in self.data_buffer[-3584:]]
        data_str = "\n".join(formatted_data)
        data_str= data_str +"\n"
        
        # 파일 저장
        with open('data.txt', 'a') as f:
            f.write(data_str)
            f.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow('COM7', 115200)
    main.show()
    sys.exit(app.exec_())
