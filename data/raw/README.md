# Dataset Setup — data/raw/README.md

## 1. Install Kaggle CLI
```bash
pip install kaggle
```

## 2. Get your Kaggle API token
- Go to kaggle.com → Account → Create New API Token
- This downloads `kaggle.json`
- Place it at:
  - Windows: `C:\Users\<you>\.kaggle\kaggle.json`
  - Mac/Linux: `~/.kaggle/kaggle.json`

## 3. Download IEEE-CIS Fraud Detection
```bash
kaggle competitions download -c ieee-fraud-detection -p data/raw/ieee-cis
```
(You may need to accept competition rules on the Kaggle website first —
it's a closed competition dataset, not open download.)

## 4. Download PaySim
```bash
kaggle datasets download -d ealaxi/paysim1 -p data/raw/paysim
```

## 5. Unzip
```bash
cd data/raw/ieee-cis && unzip *.zip && cd ../..
cd data/raw/paysim && unzip *.zip && cd ../..
```

## 6. Confirm data/raw is gitignored
Check `.gitignore` includes:
```
data/raw/
data/processed/
*.zip
```
Raw data should NEVER be committed — too large, and IEEE-CIS technically
requires competition acceptance to redistribute.

## Next: notebooks/01_eda_ieee_cis_paysim.ipynb
Start EDA here before touching graph_builder.py — know your class imbalance
(~3.5% fraud rate in IEEE-CIS) and feature distributions first.
