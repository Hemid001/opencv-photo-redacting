# Image Processing & SQL Export Script

This script scans a folder for images, processes each one (grayscale, edges, corners, histogram), saves the results, and generates an SQL file to insert metadata into a database table `images`.

## What the script does

For every image with extension:

- `.jpg`
- `.jpeg`
- `.png`

in the provided folder, the script:

1. **Loads the image**.
2. **Converts it to grayscale**.
3. **Extracts edges** using the Canny edge detector.
4. **Detects corners** using `cv2.goodFeaturesToTrack` (Shi-Tomasi).
5. **Computes image dimensions** (width and height).
6. **Computes a grayscale intensity histogram**:
   - 256 bins, range [0, 255].
   - Normalized so that the sum of values equals 1.
7. **Saves the following output images** into an `output/` subfolder:
   - `*_gray.png` – grayscale image  
   - `*_edges.png` – edge map  
   - `*_corners.png` – grayscale image with detected corners marked in red  
   - `*_hist.png` – plotted histogram (using matplotlib)
8. **Generates an SQL script** `images_data.sql` in the same `output/` folder:
   - Creates table `images`
   - Inserts one row per processed image

All outputs are saved inside `folder_path/output`.

---

## Requirements

- Python 3.x
- Installed packages:
  - `opencv-python`
  - `numpy`
  - `matplotlib`

### Install dependencies

```bash
pip install opencv-python numpy matplotlib
