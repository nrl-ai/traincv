import time

import psutil
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from traincv.common.gpu_util import get_gp_us


class SystemMonitor(QObject):
    new_system_status = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, system_monitor_edit, seconds_between_refresh=2):
        super().__init__()
        self.system_monitor_edit = system_monitor_edit
        self.seconds_between_refresh = seconds_between_refresh
        self.system_monitor_thread = QThread()
        self.moveToThread(self.system_monitor_thread)
        self.system_monitor_thread.started.connect(self.run)
        self.finished.connect(self.system_monitor_thread.quit)
        self.new_system_status.connect(self.system_monitor_edit.setText)
        self.system_monitor_thread.start()

    def run(self):
        self.new_system_status.emit("Initializing...")
        while True:
            time.sleep(self.seconds_between_refresh)
            cpu_percent = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            gpus = get_gp_us()
            report = f"• <b>CPU:</b> {cpu_percent}%<br>"
            report += f"• <b>RAM:</b> {ram.percent}%<br>"
            report += "• <b>GPUs:</b> "
            if len(gpus) == 0:
                report += (
                    "There is no GPU in your system, or CUDA has not been"
                    " setup correctly.<br>"
                )
            elif len(gpus) == 1:
                report += "There is 1 GPU<br>"
            else:
                report += f"There are {len(gpus)} GPUs<br>"
            for gpu in gpus:
                report += (
                    f"<b>⋗ ID {gpu.id} - {gpu.name}</b><br><b>VRam:</b>"
                    f" {gpu.memory_used}/{gpu.memory_total} MB, <b>Temp:</b>"
                    f" {gpu.temperature}°<br>"
                )
            self.new_system_status.emit(report)
