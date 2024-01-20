import subprocess
import platform

def is_ip_active(ip):
    # Determine the appropriate ping command based on the operating system
    if platform.system().lower() == "windows":
        command = ["ping", "-n", "1", ip]
    else:
        command = ["ping", "-c", "1", ip]

    try:
        # Run the ping command
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True  # If the command runs successfully, the IP is active
    except subprocess.CalledProcessError:
        return False  # If the command fails, the IP is not active

if __name__ == "__main__":
    target_ip = "192.168.0.120"
    
    if is_ip_active(target_ip):
        print(f"The IP address {target_ip} is active.")
    else:
        print(f"The IP address {target_ip} is not active.")
