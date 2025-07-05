import os
import csv
import hashlib
import subprocess

SIGCHECK_PATH = "..\SysSuite\sigcheck.exe"  # Đường dẫn đến sigcheck.exe

def get_md5(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return "Error reading"

def get_sigcheck_info(file_path):
    try:
        result = subprocess.run([SIGCHECK_PATH, "-n", "-q", file_path], capture_output=True, text=True)
        output = result.stdout.strip()
        if output:
            return output.splitlines()[0]  # Lấy dòng đầu (signature info)
        return "Unknown"
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

def main(autoruns_input_csv, output_csv):
    results = []

    with open(autoruns_input_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            image_path = row.get("Image Path")
            if not image_path or not os.path.isfile(image_path):
                continue

            base_name = os.path.basename(image_path)
            folder = extract_dir(image_path)
            files = get_all_files_in_folder(folder)

            for f in files:
                print(f)
                sig_info = get_sigcheck_info(f)
                md5 = get_md5(f)
                results.append({
                    "Original Image Name": base_name,
                    "Collected File Path": f,
                    "Digital Signature": sig_info,
                    "MD5": md5
                })

    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_out:
        writer = csv.DictWriter(csv_out, fieldnames=["Original Image Name", "Collected File Path", "Digital Signature", "MD5"])
        writer.writeheader()
        writer.writerows(results)

    print(f"✔️ Xuất ra file: {output_csv}")

if __name__ == "__main__":
    autoruns_input_csv = "D:\Viettel\Lab1\windows\samples_DESKTOP-92OTEJ5___20250705_200731.573\log_autoruns.csv"  # Đầu vào từ Autoruns
    output_csv = "collected_file_info.csv"
    main(autoruns_input_csv, output_csv)
