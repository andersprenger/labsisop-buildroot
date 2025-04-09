#!/usr/bin/env python3

import json
import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import socket

# --- Alunos devem implementar as funções abaixo --- #

def get_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Data e hora atual

def get_uptime():
    # Lê o tempo desde o boot (primeiro valor) do arquivo /proc/uptime
    with open("/proc/uptime", "r") as f:
        uptime_seconds = float(f.readline().split()[0])
    return int(uptime_seconds)

def get_cpu_info():
    cpu_model = ""
    cpu_speed = 0
    usage_percent = 0.0

    # Lê informações do modelo e velocidade do CPU
    with open("/proc/cpuinfo", "r") as f:
        for line in f:
            if line.startswith("model name"):
                cpu_model = line.strip().split(":")[1].strip()
            elif line.startswith("cpu MHz"):
                cpu_speed = float(line.strip().split(":")[1].strip())

    # Lê tempos da CPU em /proc/stat para calcular uso
    with open("/proc/stat", "r") as f:
        line = f.readline()
        fields = list(map(int, line.strip().split()[1:]))
        idle_time = fields[3] + fields[4]
        total_time = sum(fields)

    # Espera um pouco e mede novamente
    time.sleep(0.1)
    with open("/proc/stat", "r") as f:
        line2 = f.readline()
        fields2 = list(map(int, line2.strip().split()[1:]))
        idle2 = fields2[3] + fields2[4]
        total2 = sum(fields2)

    delta_idle = idle2 - idle_time
    delta_total = total2 - total_time
    usage_percent = 100.0 * (1 - delta_idle / delta_total) if delta_total > 0 else 0.0

    return {
        "model": cpu_model,
        "speed_mhz": round(cpu_speed, 2),
        "usage_percent": round(usage_percent, 2)
    }

def get_memory_info():
    mem_total = 0
    mem_available = 0

    with open("/proc/meminfo", "r") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                mem_total = int(line.split()[1]) // 1024  # em MB
            elif line.startswith("MemAvailable:"):
                mem_available = int(line.split()[1]) // 1024

    used = mem_total - mem_available
    return {
        "total_mb": mem_total,
        "used_mb": used
    }

def get_os_version():
    # Lê o conteúdo do arquivo /etc/os-release
    with open("/etc/os-release", "r") as f:
        for line in f:
            if line.startswith("PRETTY_NAME="):
                return line.strip().split("=")[1].strip('"')
    return "Desconhecido"

def get_process_list():
    processes = []
    for pid in os.listdir("/proc"):
        if pid.isdigit():
            try:
                with open(f"/proc/{pid}/comm", "r") as f:
                    name = f.readline().strip()
                    processes.append({"pid": int(pid), "name": name})
            except FileNotFoundError:
                continue  # processo finalizado durante leitura
    return processes

def get_disks():
    disks = []
    # Percorre os dispositivos em /sys/block
    for device in os.listdir("/sys/block"):
        try:
            with open(f"/sys/block/{device}/size", "r") as f:
                # Cada setor tem 512 bytes
                size_sectors = int(f.read().strip())
                size_mb = size_sectors * 512 // (1024 * 1024)
                disks.append({"device": device, "size_mb": size_mb})
        except Exception:
            continue
    return disks

def get_usb_devices():
    usb_devices = []
    base_path = "/sys/bus/usb/devices/"
    for device in os.listdir(base_path):
        dev_path = os.path.join(base_path, device)
        try:
            with open(os.path.join(dev_path, "product"), "r") as f:
                description = f.read().strip()
                usb_devices.append({"port": device, "description": description})
        except FileNotFoundError:
            continue
    return usb_devices

def get_network_adapters():
    adapters = []
    for iface in os.listdir("/sys/class/net/"):
        if iface == "lo":
            continue  # ignora loopback
        try:
            # Obtém IP via socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "Desconhecido"

        adapters.append({"interface": iface, "ip_address": ip})
    return adapters

# --- Servidor HTTP --- #

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            response = {
                "datetime": get_datetime(),
                "uptime_seconds": get_uptime(),
                "cpu": get_cpu_info(),
                "memory": get_memory_info(),
                "os_version": get_os_version(),
                "processes": get_process_list(),
                "disks": get_disks(),
                "usb_devices": get_usb_devices(),
                "network_adapters": get_network_adapters()
            }

            json_data = json.dumps(response, indent=2)
            html = f"""
            <!DOCTYPE html>
            <html>
              <head>
                <title>Status do Sistema</title>
              </head>
              <body>
                <h1>Status do Sistema</h1>
                <p>//////////////////////////////////////////////////////////////////////////////</p>
                <pre>{json_data}</pre>
              </body>
            </html>
            """

            data = html.encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")



# --- Função que inicia o servidor --- #

def run_server(port=8080):
    print(f"Servidor disponível em http://0.0.0.0:{port}/status")
    server = HTTPServer(("0.0.0.0", port), StatusHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
