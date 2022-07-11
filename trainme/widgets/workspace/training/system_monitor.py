import time

import psutil
from PyQt5.QtCore import QObject, pyqtSignal

from trainme.common.gpu_util import get_gp_us


class SystemMonitor(QObject):
    new_system_status = pyqtSignal(str)
    finished = pyqtSignal()

    def run(self):
        self.new_system_status.emit("Initializing...")
        while True:
            time.sleep(3)
            report = ""
            cpu_percent = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            gpus = get_gp_us()
            report = f"+ <b>CPU:</b> {cpu_percent}%<br>"
            report += f"+ <b>RAM:</b> {ram.percent}%<br>"
            report += "+ <b>GPUs:</b>"
            if len(gpus) == 0:
                report += "There is no GPU in your system, or CUDA has not been setup correctly.<br>"
            elif len(gpus) == 1:
                report += "There is 1 GPU.<br>"
            else:
                report += f"There are {len(gpus)} GPUs.<br>"
            for gpu in gpus:
                report += f"{gpu.id}: <b>VRam:</b> {gpu.memory_used}/{gpu.memory_total} MB, <b>Temp:</b> {gpu.temperature}°, <b>{gpu.name}</b><br>"
            self.new_system_status.emit(report)
