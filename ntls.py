import os
import json
import logging
import platform
import threading
import subprocess
from pyfiglet import Figlet
from datetime import datetime

BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"
LIGHT_RED = "\033[1;31m"
LIGHT_GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN = "\033[1;36m"
LIGHT_WHITE = "\033[1;37m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
CROSSED = "\033[9m"
RESET = "\033[0m"

system = platform.system()

def clear():
    if system == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def intro():
    clear()
    f = Figlet(font='slant')
    print(BLUE)
    print(f.renderText('NTLS'))
    print(RESET)
    print(f"{CYAN}Network Test and Log System - v1.0.0 | by NAX Entertainment\n(iNotAtch Emergency test and log Termux proyect){RESET}")

LOG_DIR = "ntls_logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logger():
    log_filename = f"{LOG_DIR}/network_logs_{datetime.now().strftime('%Y-%m-%d')}.txt"
    logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(message)s")

def log_session_start():
    intro()
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    message = f"{CYAN}--- STARTING MONITOR ---\n- Time: {start_time}{RESET}"
    print(message)
    logging.info(message)

def ping_dns(dns_server, timeout=2):
    try:
        result = subprocess.run(["ping", "-c", "1", "-W", str(timeout), dns_server], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "time=" in line:
                    latency = float(line.split("time=")[1].split()[0])
                    return latency
        return None
    except Exception:
        return None

def check_packet_loss(dns_server, count=5, timeout=2):
    try:
        result = subprocess.run(["ping", "-c", str(count), "-W", str(timeout), dns_server], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "packet loss" in line:
                    packet_loss = int(line.split(", ")[2].split("%")[0])
                    return packet_loss
        return 100
    except Exception:
        return 100

def test_web_connectivity(url="http://www.google.com", timeout=5):
    try:
        result = subprocess.run(["curl", "-I", "--max-time", str(timeout), url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0
    except Exception:
        return False

def test_download_speed(url="http://ipv4.download.thinkbroadband.com/100KB.zip", timeout=5):
    try:
        start_time = datetime.now()
        result = subprocess.run(
            ["curl", "-o", "/dev/null", "--max-time", str(timeout), url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        end_time = datetime.now()
        if result.returncode == 0:
            file_size_bytes = 100 * 1024
            download_time_seconds = (end_time - start_time).total_seconds()
            speed_MBps = file_size_bytes / (download_time_seconds * 1024 * 1024)
            speed_Mbps = speed_MBps * 8
            return speed_MBps, speed_Mbps
        return None, None
    except Exception:
        return None, None

def get_best_dns():
    dns_servers = [
        {"name": "Google DNS", "ip": "8.8.8.8"},
        {"name": "Quad9", "ip": "9.9.9.9"},
        {"name": "Cloudflare DNS", "ip": "1.1.1.1"},
        {"name": "OpenDNS", "ip": "208.67.222.222"}
    ]
    emergency_dns = [
        {"name": "Emergency DNS 1", "ip": "198.142.0.51"},
        {"name": "Emergency DNS 2", "ip": "198.142.0.52"}
    ]

    results = {}
    for server in dns_servers + emergency_dns:
        latency = ping_dns(server["ip"], timeout=2)
        if latency is not None:
            results[server["ip"]] = (server, latency)

    if results:
        best_dns = min(results.values(), key=lambda x: x[1])[0]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        message = f"{LIGHT_GREEN}[{timestamp}] Best DNS: {best_dns['name']} ({best_dns['ip']}){RESET}"
        print(message)
        logging.info(message)
        return best_dns["ip"]
    else:
        error_message = f"{RED}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] No functional DNS found.{RESET}"
        print(error_message)
        logging.error(error_message)
        return None

def monitor_dns_latency():
    max_failures, failure_count, current_dns = 5, 0, None
    latencies = []
    interval = 5
    last_summary_time = datetime.now()

    while True:
        if not current_dns:
            current_dns = get_best_dns()
            if not current_dns:
                print(f"{YELLOW}Waiting for coverage...{RESET}")
                continue

        latency = ping_dns(current_dns)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        if latency is not None:
            failure_count = 0
            latencies.append(latency)
            logging.info(f"[{timestamp}] Ping to {current_dns}: {latency} ms")
        else:
            failure_count += 1
            logging.info(f"[{timestamp}] Ping to {current_dns}: Failed")

        if (datetime.now() - last_summary_time).total_seconds() >= interval:
            avg_latency = sum(latencies) / len(latencies) if latencies else None
            status_color = LIGHT_GREEN if avg_latency and avg_latency < 50 else RED
            status = "Good" if avg_latency and avg_latency < 50 else "Bad"
            summary_message = f"{status_color}[{timestamp}] Ping summary: Average: {avg_latency:.1f} ms ({status}){RESET}" if avg_latency else f"{RED}[{timestamp}] Ping failed.{RESET}"
            print(summary_message)
            logging.info(summary_message)

            packet_loss = check_packet_loss(current_dns)
            if packet_loss > 50:
                print(f"{RED}[ALERT] [{timestamp}] High packet loss ({packet_loss}%){RESET}")
                logging.warning(f"[{timestamp}] High packet loss ({packet_loss}%)")

            if not test_web_connectivity():
                print(f"{RED}[ALERT] [{timestamp}] Web connectivity failed.{RESET}")
                logging.warning(f"[{timestamp}] Web connectivity failed.")

            latencies.clear()
            last_summary_time = datetime.now()

        if failure_count >= max_failures:
            print(f"{RED}Too many failures. Reevaluating DNS...{RESET}")
            current_dns, failure_count = get_best_dns(), 0

        threading.Event().wait(1)

def get_mobile_network_info():
    previous_state = None
    while True:
        try:
            mobile_info_raw = subprocess.check_output(["termux-telephony-deviceinfo"], timeout=2).decode("utf-8")
            mobile_info = json.loads(mobile_info_raw)
            operator = mobile_info.get("network_operator_name", "Unknown")
            network_type = mobile_info.get("network_type", "Unknown").upper()
            data_enabled = mobile_info.get("data_enabled", "Unknown")
            sim_state = mobile_info.get("sim_state", "Unknown")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            current_state = {
                "operator": operator,
                "network_type": network_type,
                "data_enabled": data_enabled,
                "sim_state": sim_state
            }

            if current_state != previous_state:
                summary = (
                    f"{CYAN}[{timestamp}] Operator: {operator}, Network: {network_type}, "
                    f"Data: {data_enabled}, SIM: {sim_state}{RESET}"
                )
                print(summary)
                logging.info(summary)
                previous_state = current_state

        except subprocess.TimeoutExpired:
            error_message = f"{RED}[{timestamp}] Timeout: termux-telephony-deviceinfo exceeded time limit.{RESET}"
            print(error_message)
            logging.error(error_message)

        except Exception as e:
            error_message = f"{RED}[{timestamp}] Error retrieving mobile info: {e}{RESET}"
            print(error_message)
            logging.error(error_message)

        threading.Event().wait(60)

def evaluate_network_quality():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    dns_server = "8.8.8.8"
    avg_latency = ping_dns(dns_server)
    packet_loss = check_packet_loss(dns_server)

    if avg_latency is not None:
        latency_status = "Good" if avg_latency < 50 else "Bad"
        latency_message = f"{LIGHT_GREEN}[{timestamp}] Latency: {avg_latency:.1f} ms ({latency_status}){RESET}"
    else:
        latency_message = f"{RED}[{timestamp}] Latency test failed.{RESET}"
    print(latency_message)
    logging.info(latency_message)

    if packet_loss is not None:
        packet_loss_status = "Good" if packet_loss < 10 else "Bad"
        packet_loss_message = f"{LIGHT_GREEN if packet_loss < 10 else RED}[{timestamp}] Packet loss: {packet_loss}% ({packet_loss_status}){RESET}"
    else:
        packet_loss_message = f"{RED}[{timestamp}] Packet loss test failed.{RESET}"
    print(packet_loss_message)
    logging.info(packet_loss_message)

    download_test_url = "http://ipv4.download.thinkbroadband.com/100KB.zip"
    speed_MBps, speed_Mbps = test_download_speed(download_test_url, timeout=5)
    if speed_MBps is not None and speed_Mbps is not None:
        download_message = f"{LIGHT_GREEN}[{timestamp}] Download speed: {speed_MBps:.2f} MB/s ({speed_Mbps:.2f} Mbps){RESET}"
    else:
        download_message = f"{RED}[{timestamp}] Download test failed.{RESET}"
    print(download_message)
    logging.info(download_message)

def monitor_network():
    setup_logger()
    log_session_start()
    mobile_thread = threading.Thread(target=get_mobile_network_info, daemon=True)
    dns_thread = threading.Thread(target=monitor_dns_latency, daemon=True)
    quality_thread = threading.Thread(target=evaluate_network_quality, daemon=True)
    mobile_thread.start()
    dns_thread.start()
    quality_thread.start()
    while True:
        pass

try:
    if __name__ == "__main__":
        print(f"{CYAN}Starting Emergency Network Test System...{RESET}")
        monitor_network()

except KeyboardInterrupt:
    print(f"\n{RED}Monitoring stopped by user.{RESET}")