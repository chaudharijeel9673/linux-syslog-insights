import random
import faker
from datetime import datetime, timedelta

# Initialize Faker
fake = faker.Faker()
output_file = "simulated_linux_syslog_advanced.log"
total_logs = 50000

# Hosts and processes
hosts = ["server1", "server2", "web01", "db01", "cache01", "gateway1"]
processes = ["sshd", "cron", "kernel", "dockerd", "systemd", "postfix", "nginx"]
severities = ["INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"]

# Log categories and templates
log_templates = {
    "auth_fail": ("Failed password attempt from {}", "WARNING"),
    "auth_success": ("Accepted password for user from {}", "INFO"),
    "security_change": ("Firewall rule updated", "CRITICAL"),
    "security_change_2": ("New SSH key added", "CRITICAL"),
    "cpu": ("High CPU usage detected", "CRITICAL"),
    "disk": ("Disk space running low", "ERROR"),
    "system_task": ("Cron job completed", "INFO"),
    "service_failure": ("Restarted service due to crash", "ERROR"),
    "session_event": ("User session closed", "INFO"),
    "warning_temp": ("Cron job failed to start", "WARNING"),
    "error_temp": ("Cron process crashed", "ERROR")
}

# Time settings
start_time = datetime(2025, 3, 5, 0, 0, 0)
end_time = datetime(2025, 6, 5, 23, 59, 59)

# Control IPs to simulate brute-force and reuse
repeated_ips = [fake.ipv4() for _ in range(5)]

# Prebuild specific sequences for use cases
special_logs = []

# 1. Brute-force: same IP with 6 failures within 5 minutes
bf_time = start_time + timedelta(days=10, hours=2)
ip = repeated_ips[0]
host = "server1"
for i in range(6):
    msg = log_templates["auth_fail"][0].format(ip)
    ts = bf_time + timedelta(seconds=i * 45)
    special_logs.append((ts, host, "sshd", "WARNING", msg))

# 2. Error spike: 12 errors in 1 hour for server2
error_time = start_time + timedelta(days=15, hours=4)
for i in range(12):
    ts = error_time + timedelta(minutes=i * 5)
    special_logs.append((ts, "server2", "kernel", "ERROR", log_templates["disk"][0]))

# 3. Correlated: auth_fail then security_change
corr_time = start_time + timedelta(days=20, hours=3)
ip = repeated_ips[1]
special_logs.append((corr_time, "db01", "sshd", "WARNING", log_templates["auth_fail"][0].format(ip)))
special_logs.append((corr_time + timedelta(minutes=8), "db01", "systemd", "CRITICAL", log_templates["security_change"][0]))

# 4. CPU usage across 4 hosts in same 5-minute window
cpu_time = start_time + timedelta(days=25, hours=5)
for h in ["server1", "server2", "web01", "gateway1"]:
    special_logs.append((cpu_time + timedelta(seconds=random.randint(0, 300)), h, "kernel", "CRITICAL", log_templates["cpu"][0]))

# 5. Session drift: session with CPU/disk inside
session_start = start_time + timedelta(days=30, hours=6)
special_logs.append((session_start, "cache01", "systemd", "INFO", log_templates["session_event"][0]))
special_logs.append((session_start + timedelta(minutes=2), "cache01", "kernel", "ERROR", log_templates["disk"][0]))
special_logs.append((session_start + timedelta(minutes=4), "cache01", "kernel", "CRITICAL", log_templates["cpu"][0]))
special_logs.append((session_start + timedelta(minutes=6), "cache01", "systemd", "INFO", log_templates["session_event"][0]))

# 6. Severity suppression: warning → error within 10 mins
supp_time = start_time + timedelta(days=35, hours=1)
special_logs.append((supp_time, "web01", "cron", "WARNING", log_templates["warning_temp"][0]))
special_logs.append((supp_time + timedelta(minutes=7), "web01", "cron", "ERROR", log_templates["error_temp"][0]))

# Generate random filler logs
all_logs = []
all_logs.extend(special_logs)

# Generate remaining logs
remaining_logs = total_logs - len(special_logs)
for _ in range(remaining_logs):
    ts = start_time + timedelta(seconds=random.randint(0, int((end_time - start_time).total_seconds())))
    host = random.choice(hosts)
    process = random.choice(processes)
    category_key = random.choice(list(log_templates.keys()))
    message_template, severity = log_templates[category_key]
    if "{}" in message_template:
        ip = random.choice(repeated_ips + [fake.ipv4()])
        message = message_template.format(ip)
    else:
        message = message_template
    all_logs.append((ts, host, process, severity, message))

# Sort logs by timestamp
all_logs.sort(key=lambda x: x[0])

# Write to file
with open(output_file, "w") as f:
    for ts, host, process, severity, message in all_logs:
        timestamp_str = ts.strftime("%Y %b %d %H:%M:%S")
        pid = random.randint(100, 9999)
        log_line = f"{timestamp_str} {host} {process}[{pid}]: [{severity}] {message}\n"
        f.write(log_line)

output_file
