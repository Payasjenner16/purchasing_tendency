#  Purchasing Tendency — AI-Powered E-Commerce Intelligence System

A full-stack Flask web application that leverages deep learning models (**TendGraphNet** and **SeqBehNet**) to analyse purchasing behaviour, generate product recommendations, detect community trends, and provide real-time demand insights for buyers, sellers, and admins.

---

## 📌 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [User Roles & Access](#user-roles--access)
- [Deep Learning Models](#deep-learning-models)
- [Dataset Files](#dataset-files)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

| Role | Features |
|------|----------|
| **Buyer** | Register / Login, Browse products, Add to Cart, Place Orders, Pay, AI Recommendations, Sequential Recommendations, Demand Insights |
| **Seller** | Register / Login, Add / View Products, View Orders, Seller Analytics, Demand Alerts via Email |
| **Admin** | Login (hardcoded), Dashboard, Analytics, Remove Sellers |

**AI Capabilities:**
- 🔵 **TendGraphNet** — Graph Neural Network (GCN) that captures user–product interactions
- 🟣 **SeqBehNet** — SASRec Transformer-based sequential behaviour predictor
- 📊 Demand heatmaps by location and product
- 🧭 Community discovery and multi-seller map recommendations

---

## 📁 Project Structure

```
purchasing_tendency/
├── app.py                      # Flask entry point
├── purchasing_tendency.db      # SQLite database
├── requirements.txt            # Python dependencies
├── .gitignore
│
├── modules/                    # Flask Blueprints
│   ├── admin.py                # Admin routes
│   ├── buyer.py                # Buyer routes + AI pipeline
│   ├── seller.py               # Seller routes
│   └── utils.py                # DB helper, mail, alert generators
│
├── dl_models/                  # Deep Learning models
│   ├── tendgraphnet.py         # GNN model definition + training
│   ├── tendgraphnet.pth        # Pretrained GNN weights
│   ├── seqbehnet.py            # Sequential Transformer model + training
│   ├── seqbehnet.pth           # Pretrained SeqBehNet weights
│   └── data_loader.py          # Dataset loader for DL models
│
├── static/
│   ├── css/                    # Stylesheets
│   ├── images/                 # Static images
│   ├── uploads/products/       # Seller-uploaded product images
│   └── data/                   # CSV datasets
│       ├── dataset.csv
│       ├── ecommerce_behavior_dataset.csv
│       └── ecommerce_dataset_fixed.csv
│
└── templates/                  # Jinja2 HTML templates
    ├── index.html
    ├── base.html
    ├── admin_*.html
    ├── buyer_*.html
    ├── seller_*.html
    └── ...
```

---

## ✅ Prerequisites

Make sure the following are installed on your machine before proceeding:

| Requirement | Minimum Version | Download |
|-------------|----------------|---------|
| Python | 3.9+ | https://www.python.org/downloads/ |
| pip | Latest | Bundled with Python |
| Git (optional) | Any | https://git-scm.com/ |

> **Windows users:** During Python installation, make sure to tick **"Add Python to PATH"**.

---

## 🔧 Installation & Setup

### 1. Clone or Download the Project

```bash
# Option A — Clone via Git
git clone <your-repository-url>
cd purchasing_tendency

# Option B — Navigate to the folder directly (if already downloaded)
cd path\to\purchasing_tendency
```

### 2. Create a Virtual Environment

It is strongly recommended to use a virtual environment to isolate project dependencies.

```bash
# Create the virtual environment
python -m venv .venv
```

### 3. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

> Once activated, your terminal prompt will show `(.venv)` as a prefix.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ **Note on `torch-geometric`:** On Windows, installing `torch-geometric` may require extra steps depending on your PyTorch version and CUDA availability. If the standard install fails, follow the official guide:  
> 👉 https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html

**For CPU-only (no GPU) environments, you can install PyTorch first:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install torch-geometric
pip install -r requirements.txt
```

### 5. Verify the Database Exists

The SQLite database `purchasing_tendency.db` should already be present in the project root. If it is missing, the app will fail to start.

```bash
# Confirm the file exists
dir purchasing_tendency.db        # Windows
ls purchasing_tendency.db         # macOS/Linux
```

### 6. Verify Dataset Files

The following CSV files must exist inside `static/data/`:

- `dataset.csv`
- `ecommerce_behavior_dataset.csv`
- `ecommerce_dataset_fixed.csv`

If any are missing, the application will raise a `FileNotFoundError` on startup.

---

## 🚀 Running the Application

With the virtual environment **activated** and all dependencies installed:

```bash
python app.py
```

Expected output:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Open your browser and navigate to:

```
http://127.0.0.1:5000
```

---

## 👤 User Roles & Access

### 🔑 Admin Login
| Field | Value |
|-------|-------|
| URL | `http://127.0.0.1:5000/admin` |
| Username | `admin` |
| Password | `admin` |

### 🛍️ Buyer
| Action | URL |
|--------|-----|
| Register | `http://127.0.0.1:5000/buyer_register` |
| Login | `http://127.0.0.1:5000/buyer_login` |

### 🏪 Seller
| Action | URL |
|--------|-----|
| Register | `http://127.0.0.1:5000/seller_register` |
| Login | `http://127.0.0.1:5000/seller_login` |

---

## 🧠 Deep Learning Models

The application uses two pre-trained deep learning models stored in `dl_models/`:

### TendGraphNet (Graph Neural Network)
- Builds a bipartite user–product interaction graph
- Uses two-layer Graph Convolutional Network (GCN) via `torch_geometric`
- Pre-trained weights: `dl_models/tendgraphnet.pth`

### SeqBehNet (Sequential Behaviour Network)
- SASRec-style Transformer Encoder for sequential purchase prediction
- Predicts the next likely product based on a buyer's history
- Pre-trained weights: `dl_models/seqbehnet.pth`

> The `.pth` weight files are already included — **you do not need to retrain the models** to run the application.

---

## 📊 Dataset Files

| File | Purpose |
|------|---------|
| `dataset.csv` | District-level product purchase counts used for demand insights |
| `ecommerce_behavior_dataset.csv` | User behavior events (views, cart adds, purchases) |
| `ecommerce_dataset_fixed.csv` | Cleaned full dataset used for demand alert generation |

---

## 🐛 Troubleshooting

### `ModuleNotFoundError: No module named 'torch_geometric'`
Install `torch-geometric` following the [official instructions](https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html) for your OS and PyTorch version.

### `FileNotFoundError: static/data/dataset.csv`
Ensure all three CSV files are present inside `static/data/`. Do not rename or move them.

### `sqlite3.OperationalError`
Confirm that `purchasing_tendency.db` exists in the project root directory and has not been corrupted.

### Virtual environment not activating on PowerShell
Run the following command once to allow script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port already in use
If port `5000` is occupied, run Flask on a different port:
```bash
flask run --port 5001
```

---

## 📧 Email Configuration

The app uses Gmail SMTP to send seller demand alert emails. The SMTP credentials are pre-configured in `app.py`. If you wish to use your own Gmail account, update the following in `app.py`:

```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'
```

> Use a [Gmail App Password](https://support.google.com/accounts/answer/185833) — not your regular Gmail password.

---

## 📝 License

This project was developed as an academic final project. All rights reserved.
