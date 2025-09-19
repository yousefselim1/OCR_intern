# OCR_intern

End-to-end OCR pipeline built during my internship at **Bedo Company**.  
The project digitizes text from hardcopy sources (Egyptian IDs dataset) using a combination of **computer vision preprocessing**, **deep learning models**, and structured **result exports**.

---

## 🚀 Features
- **Preprocessing with OpenCV**: grayscale conversion, thresholding, denoising.
- **OCR Models**: CNN-based recognition for structured text fields.
- **TFRecords Pipeline**: dataset preparation for TensorFlow training.
- **Evaluation Outputs**: CSV files (`ocr_results.csv`, `final_detected_faces.csv`) with recognized text.
- **Visualization**: sample images showing intermediate processing and final detection results.
- **Analysis Module**: accuracy metrics and error breakdown.

---

## 📂 Project Structure
OCR/
│── Analysis.py # metrics & evaluation
│── OCR.py # main OCR pipeline
│── OCRRRR.py # alternative OCR run
│── Tf_DataSet.py # TFRecord dataset builder
│── requirements.txt # dependencies
│── outputs/ # predictions & logs (LFS)
│── tfrecords/ # serialized data (LFS)
│── final_detected_faces.csv # evaluation results
│── ocr_results.csv # recognized text output
│── Updated Data.xlsx # labeled dataset
│── images/ # test samples




---

## ⚙️ Installation
```bash
# clone repo
git clone https://github.com/yousefselim1/OCR_intern.git
cd OCR_intern

# setup virtual environment
python -m venv .venv
.venv\Scripts\activate   # (Windows)
# source .venv/bin/activate   # (Linux/Mac)

# install dependencies
pip install -r requirements.txt


🖼️ Sample Results

Preprocessed input → _debug_proc.png

Enhanced image → _enh.png

Final recognized text saved in CSV outputs


📌 Requirements

Python 3.9+
TensorFlow / PyTorch
OpenCV
NumPy / Pandas

