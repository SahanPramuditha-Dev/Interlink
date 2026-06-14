import time
import sys
import ping3

TARGET = "8.8.8.8"  # Google Public DNS
PING_INTERVAL = 1   # Time to wait between pings (seconds)

# ANSI Color Codes for terminal formatting
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

print(f"{BOLD}📡 Starting Continuous Monitor for {TARGET}... (Press Ctrl+C to stop){RESET}\n")

total_pings = 0
successful_pings = 0
latencies = []

try:
    while True:
        total_pings += 1
        raw_time = ping3.ping(TARGET)
        
        if raw_time is None:
            print(f"{RED}❌ Request Timed Out to {TARGET}{RESET}")
        elif raw_time is False:
            print(f"{RED}❌ Network Error: Unable to resolve host {TARGET}{RESET}")
            sys.exit(1)
        else:
            successful_pings += 1
            ms = raw_time * 1000
            latencies.append(ms)
            print(f"{GREEN}✅ Reply from {TARGET}: time={ms:.2f}ms{RESET}")
            
        time.sleep(PING_INTERVAL)

except KeyboardInterrupt:
    # Captures Ctrl+C cleanly to show summary statistics
    print(f"\n\n{BOLD}--- {TARGET} Ping Statistics Summary ---{RESET}")
    packet_loss = ((total_pings - successful_pings) / total_pings) * 100
    print(f"Packets: Sent = {total_pings}, Received = {successful_pings}, Lost = {total_pings - successful_pings} ({packet_loss:.1f}% loss)")
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        print(f"Approximate round trip times in milli-seconds:")
        print(f"    Minimum = {min(latencies):.2f}ms, Maximum = {max(latencies):.2f}ms, Average = {avg_latency:.2f}ms")
    print(f"{BOLD}Monitor closed successfully.{RESET}")