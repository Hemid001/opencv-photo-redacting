import os
import sys
import json
import cv2
import numpy as np
import matplotlib.pyplot as plt
import io

# Поддержка вывода русских символов в консоли Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def process_image(image_path, output_dir):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Не удалось загрузить изображение: {image_path}")
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
    corner_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    if corners is not None:
        for corner in corners:
            x, y = corner.ravel()
            cv2.circle(corner_img, (int(x), int(y)), 3, (0, 0, 255), -1)
    height, width = gray.shape
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    hist_norm = hist / hist.sum()
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    gray_path = os.path.join(output_dir, f"{base_name}_gray.png")
    edges_path = os.path.join(output_dir, f"{base_name}_edges.png")
    corners_path = os.path.join(output_dir, f"{base_name}_corners.png")
    hist_path = os.path.join(output_dir, f"{base_name}_hist.png")
    cv2.imwrite(gray_path, gray)
    cv2.imwrite(edges_path, edges)
    cv2.imwrite(corners_path, corner_img)
    plt.figure()
    plt.title("Histogram")
    plt.xlabel("Pixel intensity")
    plt.ylabel("Frequency")
    plt.plot(hist_norm)
    plt.savefig(hist_path)
    plt.close()
    return {
        "width": width,
        "height": height,
        "histogram": hist_norm.tolist(),
        "gray_path": gray_path,
        "edges_path": edges_path,
        "corners_path": corners_path,
        "hist_path": hist_path
    }

def write_sql(output_dir, records):
    sql_path = os.path.join(output_dir, "images_data.sql")
    with open(sql_path, 'w', encoding='utf-8') as f:
        f.write("""
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT,
    width INTEGER,
    height INTEGER,
    histogram TEXT,
    gray_path TEXT,
    edges_path TEXT,
    corners_path TEXT,
    hist_path TEXT
);
""")
        for i, rec in enumerate(records, 1):
            hist_json = json.dumps(rec["histogram"], ensure_ascii=False).replace("'", "''")
            original_path = rec['original_path'].replace("'", "''")
            gray_path = rec['gray_path'].replace("'", "''")
            edges_path = rec['edges_path'].replace("'", "''")
            corners_path = rec['corners_path'].replace("'", "''")
            hist_path = rec['hist_path'].replace("'", "''")
            f.write(f"INSERT INTO images (id, image_path, width, height, histogram, gray_path, edges_path, corners_path, hist_path) VALUES ("
                    f"{i}, '{original_path}', {rec['width']}, {rec['height']}, '{hist_json}', "
                    f"'{gray_path}', '{edges_path}', '{corners_path}', '{hist_path}');\n")
    return sql_path

def main(folder_path):
    output_dir = os.path.join(folder_path, "output")
    os.makedirs(output_dir, exist_ok=True)
    exts = ['.jpg', '.jpeg', '.png']
    records = []
    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in exts):
            full_path = os.path.join(folder_path, file)
            processed = process_image(full_path, output_dir)
            if processed is not None:
                processed["original_path"] = full_path
                records.append(processed)
    if not records:
        print("В указанной папке не найдено корректных изображений для обработки.")
        return
    sql_file = write_sql(output_dir, records)
    print(f"Обработка завершена. SQL файл создан: {sql_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python script.py /путь/к/папке")
        sys.exit(1)
    main(sys.argv[1])