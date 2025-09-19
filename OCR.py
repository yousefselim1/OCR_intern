import argparse
import easyocr
from PIL import Image
import numpy as np
import re

# Arabic to English digits map
AR2EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

def cx(b):  
    return (b[0][0] + b[1][0] + b[2][0] + b[3][0]) / 4.0

def cy(b):  
    return (b[0][1] + b[1][1] + b[2][1] + b[3][1]) / 4.0


def main():
    ap = argparse.ArgumentParser(description="Extract ONLY numbers from image (ordered).")
    ap.add_argument("--input", required=True, help="Path to image")
    ap.add_argument("--gpu", action="store_true", help="Use GPU if available")
    ap.add_argument("--rtl", action="store_true",
                    help="Print numbers right→left within each line (default left→right)")
    args = ap.parse_args()

    reader = easyocr.Reader(['ar', 'en'], gpu=args.gpu)
    img = Image.open(args.input).convert("RGB")



    allow = "0123456789٠١٢٣٤٥٦٧٨٩"
    raw = reader.readtext(
        np.array(img), detail=1, paragraph=False, allowlist=allow,
        width_ths=0.15, ycenter_ths=0.7, height_ths=0.7,
        contrast_ths=0.3, adjust_contrast=0.7
    )

    if not raw:
        return

    # group into rows by Y 
    h = img.height
    tol = max(10, int(h * 0.02))
    rows = []
    for it in sorted(raw, key=lambda r: cy(r[0])):
        y = cy(it[0])
        if not rows or abs(y - cy(rows[-1][0][0])) > tol:
            rows.append([it])
        else:
            rows[-1].append(it)

    for row in rows:
        row_sorted = sorted(row, key=lambda r: cx(r[0]), reverse=args.rtl)
        s = "".join(re.sub(r"[^0-9]", "", (t or "").translate(AR2EN)) for _, t, _ in row_sorted)

        # just >= 12 digits
        if s and len(s) >= 12:
            print("Full number:", s)

            # second from right
            if len(s) >= 2:
                print("Second from right:", s[-2])

            # first 7 from left
            first7 = s[:7]
            if first7:
                # apply replacement rule on first digit
                if first7[0] == "3":
                    first7 = "20" + first7[1:]
                elif first7[0] == "2":
                    first7 = "19" + first7[1:]
                print("First 7 (with replacement if needed):", first7)


if __name__ == "__main__":
    main()








# import easyocr
# from PIL import Image
# import numpy as np
# import argparse

# def run_ocr(image_path, gpu=False):
#     # Arabic + English OCR
#     reader = easyocr.Reader(['ar', 'en'], gpu=gpu)
#     img = Image.open(image_path).convert("RGB")
#     results = reader.readtext(np.array(img), detail=1, paragraph=False)

#     for bbox, text, conf in results:
#         print(f"[{conf:.2f}] {text}")

# if __name__ == "__main__":
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--input", required=True, help="Path to image file")
#     ap.add_argument("--gpu", action="store_true", help="Use GPU if available")
#     args = ap.parse_args()

#     run_ocr(args.input, gpu=args.gpu)





