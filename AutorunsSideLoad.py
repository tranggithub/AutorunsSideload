import os
import csv
import hashlib
import subprocess
from colorama import init, Fore, Style

init(autoreset=True)  # Tự reset về màu thường sau mỗi dòng
SIGCHECK_PATH = "..\SysSuite\sigcheck.exe"  # Đường dẫn đến sigcheck.exe

def get_md5(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return "Error reading"

def get_sigcheck_info(file_path):
    try:
        result = subprocess.run([SIGCHECK_PATH, file_path], capture_output=True, text=True)
        output = result.stdout.strip()
        lines = output.splitlines()

        verified = "Unknown"
        publisher = "Unknown"

        for line in lines:
            if "Verified:" in line:
                verified = line.split(":", 1)[1].strip()
            elif "Publisher:" in line:
                publisher = line.split(":", 1)[1].strip()

        return f"{verified} {publisher}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_all_files_in_folder(folder_path):
    try:
        return [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f))]
    except:
        return []

def extract_dir(image_path):
    return os.path.dirname(image_path.strip('"'))

def is_pe_file(file_path):
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.dll', '.exe']:
            return False
        with open(file_path, 'rb') as f:
            magic = f.read(2)
            return magic == b'MZ'
    except:
        return False
def main(autoruns_input_csv, output_csv):
    results = []
    folders = []
    with open(autoruns_input_csv, newline='', encoding='utf-8-sig',errors='replace') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            image_path = row.get("Image Path")
            if not image_path or not os.path.isfile(image_path):
                continue
            base_name = os.path.basename(image_path)
            folder = extract_dir(image_path)
            if (folder in folders):
                continue
            folders.append(folder)
            if (folder == 'c:\windows\system32' or folder == 'c:\windows\syswow64'):
                continue
            print(Fore.YELLOW + f"{folder}")
            files = get_all_files_in_folder(folder)

            for f in files:
                if not is_pe_file(f):
                    continue
                sig_info = get_sigcheck_info(f)
                md5 = get_md5(f)
                results.append({
                    "Original Image Name": base_name,
                    "Collected File Path": f,
                    "Digital Signature": sig_info,
                    "MD5": md5
                })
                
#                if sig_info not in whitelists:
#                    print(f"{base_name}, {f}, {sig_info}, {md5}")
                if "unsigned " in sig_info.lower():
                    print(f"{base_name}, {f}, {sig_info}, {md5}")

    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_out:
        writer = csv.DictWriter(csv_out, fieldnames=["Original Image Name", "Collected File Path", "Digital Signature", "MD5"])
        writer.writeheader()
        writer.writerows(results)

    print(f"✔️ Xuất ra file: {output_csv}")

if __name__ == "__main__":
    autoruns_input_csv = "D:\Viettel\Lab1\windows\samples_DESKTOP-92OTEJ5___20250705_200731.573\log_autoruns.csv"  # Đầu vào từ Autoruns
    output_csv = "collected_file_info.csv"
    whitelists = ["Signed Microsoft Corporation","Signed Microsoft Windows Publisher"]
    main(autoruns_input_csv, output_csv)
