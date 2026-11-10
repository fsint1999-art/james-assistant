"""Métricas do sistema (CPU, RAM, VRAM, temperatura, disco, rede)."""
import shutil, subprocess, psutil

def _gpu():
    try:
        o = subprocess.check_output(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
                                     "--format=csv,noheader,nounits"], text=True, timeout=2).split("\n")[0]
        u, mu, mt, t = [float(x) for x in o.split(",")]
        return {"load": u, "vram_used": mu / 1024, "vram_total": mt / 1024, "temp": t}
    except Exception: pass
    try:  # AMD via sysfs
        base = next(psutil.Path("/sys/class/drm").glob("card*/device/gpu_busy_percent")) if hasattr(psutil, "Path") else None
    except Exception: base = None
    from pathlib import Path
    for d in Path("/sys/class/drm").glob("card?/device"):
        try:
            return {"load": float((d / "gpu_busy_percent").read_text()),
                    "vram_used": float((d / "mem_info_vram_used").read_text()) / 2**30,
                    "vram_total": float((d / "mem_info_vram_total").read_text()) / 2**30, "temp": None}
        except Exception: continue
    return None

def snapshot():
    temps = psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else {}
    cpu_t = next((v[0].current for k, v in temps.items() if v and k in ("coretemp", "k10temp", "zenpower")), None)
    vm, du, net = psutil.virtual_memory(), shutil.disk_usage("/"), psutil.net_io_counters()
    return {"cpu": psutil.cpu_percent(), "cores": psutil.cpu_count(), "cpu_temp": cpu_t,
            "ram": vm.percent, "ram_gb": vm.total / 2**30,
            "disk": du.used / du.total * 100, "disk_free_gb": du.free / 2**30,
            "net_up": net.bytes_sent, "net_down": net.bytes_recv,
            "online": any(s.isup for n, s in psutil.net_if_stats().items() if n != "lo"),
            "gpu": _gpu()}
