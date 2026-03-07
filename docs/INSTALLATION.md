Smart Agriculture AI System Installation Guide

Requirements:

Python 3.9 or newer

Installation Steps:

1) Clone repository

git clone <repository-url>

cd CropProject


2) Create virtual environment

python -m venv crop_env


3) Activate environment

Windows:

crop_env\Scripts\activate

Linux/Mac:

source crop_env/bin/activate


4) Install dependencies

pip install -r requirements.txt


5) Run Dashboard

streamlit run dashboard/app.py
