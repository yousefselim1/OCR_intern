# #!/usr/bin/env python3
# # OCR with bottom-strip crop + white background mask (keeps your OCR logic)

# import argparse
# import re
# import numpy as np
# import cv2
# import easyocr
# from PIL import Image

# # Arabic to English digits map
# AR2EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# def cx(b):  # bbox center x
#     return (b[0][0] + b[1][0] + b[2][0] + b[3][0]) / 4.0

# def cy(b):  # bbox center y
#     return (b[0][1] + b[1][1] + b[2][1] + b[3][1]) / 4.0

# # --- NEW: simple crop+mask (no change to your OCR processing) -----------------
# def crop_bottom_strip_whiten(pil_img, bottom_frac=0.34, tight=True, debug_save=None):
#     """
#     1) Crop the bottom `bottom_frac` of the image.
#     2) Make background white using adaptive threshold (digits stay dark).
#     3) If tight=True, further crop to tight bbox of the digit mask.
#     Returns an RGB numpy array ready for EasyOCR.
#     """
#     rgb = np.array(pil_img)  # RGB
#     if rgb.ndim == 2:
#         gray = rgb
#         rgb3 = cv2.cvtColor(rgb, cv2.COLOR_GRAY2RGB)
#     else:
#         gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
#         rgb3 = rgb.copy()

#     H, W = gray.shape
#     y1 = max(0, int(H * (1 - float(bottom_frac))))
#     roi_gray = gray[y1:H, :]
#     roi_rgb = rgb3[y1:H, :]

#     # Adaptive threshold (invert so digits are white on black mask)
#     thr = cv2.adaptiveThreshold(
#         roi_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 10
#     )

#     # White background: wherever mask==0, set to white
#     out = roi_rgb.copy()
#     out[thr == 0] = [255, 255, 255]

#     # Optional: tighten crop around mask bbox
#     if tight:
#         ys, xs = np.where(thr > 0)
#         if len(xs) > 0:
#             pad = max(6, int(0.01 * H))
#             x1, x2 = max(0, xs.min() - pad), min(W, xs.max() + pad)
#             yb = max(0, ys.min() - pad)
#             yt = min(out.shape[0], ys.max() + pad)
#             out = out[yb:yt, x1:x2]

#     if debug_save:
#         # save BGR for cv2.imwrite compatibility
#         cv2.imwrite(debug_save, out[:, :, ::-1])

#     return out
# # -----------------------------------------------------------------------------


# def main():
#     ap = argparse.ArgumentParser(description="Extract ONLY numbers from image (ordered).")
#     ap.add_argument("--input", required=True, help="Path to image")
#     ap.add_argument("--gpu", action="store_true", help="Use GPU if available")
#     ap.add_argument("--rtl", action="store_true",
#                     help="Print numbers right→left within each line (default left→right)")
#     # preprocessing controls (optional)
#     ap.add_argument("--bottom-frac", type=float, default=0.34,
#                     help="Fraction of image height to crop from bottom (default 0.34)")
#     ap.add_argument("--no-tight", action="store_true",
#                     help="Do not tight-crop to the digit mask; keep full bottom band")
#     ap.add_argument("--debug-save", default=None,
#                     help="Path to save the preprocessed bottom strip (PNG)")
#     args = ap.parse_args()

#     # Init OCR
#     reader = easyocr.Reader(['ar', 'en'], gpu=args.gpu)

#     # Load image
#     pil_img = Image.open(args.input).convert("RGB")

#     # --- NEW: crop + whiten background (only preprocessing step) ---
#     proc = crop_bottom_strip_whiten(
#         pil_img,
#         bottom_frac=args.bottom_frac,
#         tight=(not args.no_tight),
#         debug_save=args.debug_save
#     )

#     # Your original OCR call — unchanged (we just pass `proc` instead of the full image)
#     allow = "0123456789٠١٢٣٤٥٦٧٨٩"
#     raw = reader.readtext(
#         proc, detail=1, paragraph=False, allowlist=allow,
#         width_ths=0.15, ycenter_ths=0.7, height_ths=0.7,
#         contrast_ths=0.3, adjust_contrast=0.7
#     )

#     if not raw:
#         return

#     # group into rows by Y  (same logic, use height from `proc`)
#     h = proc.shape[0]
#     tol = max(10, int(h * 0.02))
#     rows = []
#     for it in sorted(raw, key=lambda r: cy(r[0])):
#         y = cy(it[0])
#         if not rows or abs(y - cy(rows[-1][0][0])) > tol:
#             rows.append([it])
#         else:
#             rows[-1].append(it)

#     # print per your rules (unchanged)
#     for row in rows:
#         row_sorted = sorted(row, key=lambda r: cx(r[0]), reverse=args.rtl)
#         s = "".join(re.sub(r"[^0-9]", "", (t or "").translate(AR2EN)) for _, t, _ in row_sorted)

#         # just >= 12 digits
#         if s and len(s) >= 12:
#             print("Full number:", s)

#             # second from right
#             if len(s) >= 2:
#                 print("Second from right:", s[-2])

#             # first 7 from left with your replacement rule
#             first7 = s[:7]
#             if first7:
#                 if first7[0] == "3":
#                     first7 = "20" + first7[1:]
#                 elif first7[0] == "2":
#                     first7 = "19" + first7[1:]
#                 print("First 7 (with replacement if needed):", first7)


# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
# Enhance image (optionally) then run your EXACT OCR pipeline.




import argparse, re, sys
import numpy as np
import cv2
from PIL import Image
import easyocr

# -----------------------
# Your original OCR setup
# -----------------------
AR2EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

def cx(b):  # bbox center x
    return (b[0][0] + b[1][0] + b[2][0] + b[3][0]) / 4.0

def cy(b):  # bbox center y
    return (b[0][1] + b[1][1] + b[2][1] + b[3][1]) / 4.0

def run_your_ocr(pil_img, use_gpu=False, rtl=False):
    reader = easyocr.Reader(['ar', 'en'], gpu=use_gpu)
    allow = "0123456789٠١٢٣٤٥٦٧٨٩"
    raw = reader.readtext(
        np.array(pil_img), detail=1, paragraph=False, allowlist=allow,
        width_ths=0.15, ycenter_ths=0.7, height_ths=0.7,
        contrast_ths=0.3, adjust_contrast=0.7
    )
    if not raw:
        return

    h = pil_img.height
    tol = max(10, int(h * 0.02))
    rows = []
    for it in sorted(raw, key=lambda r: cy(r[0])):
        y = cy(it[0])
        if not rows or abs(y - cy(rows[-1][0][0])) > tol:
            rows.append([it])
        else:
            rows[-1].append(it)

    for row in rows:
        row_sorted = sorted(row, key=lambda r: cx(r[0]), reverse=rtl)
        s = "".join(re.sub(r"[^0-9]", "", (t or "").translate(AR2EN)) for _, t, _ in row_sorted)
        if s and len(s) >= 12:
            print("Full number:", s)
            if len(s) >= 2:
                print("Second from right:", s[-2])
            first7 = s[:7]
            if first7:
                if first7[0] == "3":
                    first7 = "20" + first7[1:]
                elif first7[0] == "2":
                    first7 = "19" + first7[1:]
                print("First 7 (with replacement if needed):", first7)

# ---------------------------------
# Simple enhancement implementations
# ---------------------------------
def enhance_classic(bgr, scale=2):
    """No-model pipeline: upscale -> denoise -> CLAHE -> unsharp mask."""
    # 1) upscale
    bgr = cv2.resize(bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    # 2) light denoise (keeps edges)
    bgr = cv2.bilateralFilter(bgr, d=7, sigmaColor=75, sigmaSpace=75)
    # 3) local contrast (CLAHE) in LAB
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l2 = clahe.apply(l)
    lab2 = cv2.merge([l2, a, b])
    bgr = cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)
    # 4) unsharp mask
    blur = cv2.GaussianBlur(bgr, (0, 0), 1.2)
    sharp = cv2.addWeighted(bgr, 1.7, blur, -0.7, 0)
    return sharp

def enhance_realesrgan(bgr, scale=2):
    """Try Real-ESRGAN (if installed). Falls back to classic if import fails."""
    try:
        import torch
        from realesrgan import RealESRGAN
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = RealESRGAN(device, scale=scale)
        # By default, the pip package downloads weights on first call to load_weights if missing.
        model.load_weights(f'weights/RealESRGAN_x{scale}.pth', download=True)
        # PIL in -> PIL out
        pil = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        out = model.predict(pil)  # PIL
        return cv2.cvtColor(np.array(out), cv2.COLOR_RGB2BGR), "realesrgan"
    except Exception as e:
        # fallback
        enhanced = enhance_classic(bgr, scale=scale)
        return enhanced, f"classic_fallback ({e.__class__.__name__})"

# --------------
# CLI Entrypoint
# --------------


def main():
    ap = argparse.ArgumentParser(description="Enhance (optionally) then OCR for long numbers.")
    ap.add_argument("--input", required=True, help="Path to image")
    ap.add_argument("--gpu", action="store_true", help="Use GPU for EasyOCR if available")
    ap.add_argument("--rtl", action="store_true", help="Right→Left sort within a line")
    ap.add_argument("--enhance", choices=["none", "classic", "realesrgan"], default="classic",
                    help="Pre-OCR enhancement method")
    ap.add_argument("--scale", type=int, default=2, help="Upscale factor for enhancer (2 is safe)")
    ap.add_argument("--save-enhanced", help="Optional path to save the enhanced image")
    args = ap.parse_args()

    # Read original image (BGR)
    bgr = cv2.imread(args.input, cv2.IMREAD_COLOR)
    if bgr is None:
        print(f"ERROR: cannot read image: {args.input}")
        sys.exit(1)

    # Enhance
    used = "none"
    if args.enhance == "classic":
        bgr = enhance_classic(bgr, scale=args.scale)
        used = "classic"
    elif args.enhance == "realesrgan":
        bgr, used = enhance_realesrgan(bgr, scale=args.scale)

    if args.save_enhanced:
        cv2.imwrite(args.save_enhanced, bgr)

    print(f"[Enhancement used] {used}")
    # Convert to PIL for your OCR code
    pil_img = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))

    # Run your original OCR
    run_your_ocr(pil_img, use_gpu=args.gpu, rtl=args.rtl)

if __name__ == "__main__":
    main()

#python OCRRRR.py --input "C:\Users\DELL\Desktop\OCR\img4.png" --enhance classic --scale 2 --save-enhanced "_enh.png"

#OCR.py --input "C:\Users\DELL\Desktop\OCR\img2.png"                                                                                                                                                 
