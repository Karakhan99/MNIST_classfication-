# -*- coding: utf-8 -*-
"""Mnist_akhmadjon.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1w0EXbhYOLDPLLlfK0lRS9F81ElPmrx9H
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report

print("Downloading / loading MNIST …")
mnist = fetch_openml("mnist_784", version=1, as_frame=False)  # 70 000 × 784
X, y = mnist["data"], mnist["target"].astype(int)

# Optional down‑sampling to keep runtime reasonable on CPUs
# Uncomment if you hit memory / time limits
# sample = np.random.RandomState(42).choice(np.arange(X.shape[0]), size=20000, replace=False)
# X, y = X[sample], y[sample]

# Train / test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=10_000, random_state=42, stratify=y
)

def make_pipeline(clf, use_pca=False, pca_var=0.95):
    steps = [("scaler", StandardScaler())]
    if use_pca:
        steps.append(("pca", PCA(n_components=pca_var, svd_solver="full")))
    steps.append(("clf", clf))
    return Pipeline(steps)

# 3. Define the models to benchmark
# -----------------------------------------------------------
models = {
    "LogReg": LogisticRegression(max_iter=1000, n_jobs=-1, solver="lbfgs", multi_class="multinomial"),
    "SVM‑RBF": SVC(kernel="rbf", gamma="scale"),
    "kNN‑3": KNeighborsClassifier(n_neighbors=3),
    "RandForest": RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42),
    "MLP‑100": MLPClassifier(hidden_layer_sizes=(100,), max_iter=20, random_state=42, verbose=False),
}

# 4. Run experiments
# -----------------------------------------------------------
results = []

for name, model in models.items():
    for pca_flag in (False, True):
        label = f"{name}{' + PCA' if pca_flag else ''}"
        pipe = make_pipeline(model, use_pca=pca_flag)
        print(f"Training {label} …")
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        acc = accuracy_score(y_test, preds)
        results.append({"Model": name, "PCA": pca_flag, "Accuracy": acc})

# 5. Present results
# -----------------------------------------------------------
df = pd.DataFrame(results).sort_values(["Model", "PCA"])
print("\n=== Test set accuracies ===")
print(df.pivot(index="Model", columns="PCA", values="Accuracy").rename(columns={False: "No PCA", True: "With PCA"}))
print("\nClassification report for Logistic Regression + PCA (quick glance):")
print(classification_report(y_test, make_pipeline(models["LogReg"], True).fit(X_train, y_train).predict(X_test)))

import pandas as pd
import matplotlib.pyplot as plt

'''
results = [{'Model': 'LogReg', 'PCA': False, 'Accuracy': 0.9198},
 {'Model': 'LogReg', 'PCA': True, 'Accuracy': 0.923},
 {'Model': 'SVM‑RBF', 'PCA': False, 'Accuracy': 0.9673},
 {'Model': 'SVM‑RBF', 'PCA': True, 'Accuracy': 0.9684},
 {'Model': 'kNN‑3', 'PCA': False, 'Accuracy': 0.9474},
 {'Model': 'kNN‑3', 'PCA': True, 'Accuracy': 0.9512},
 {'Model': 'RandForest', 'PCA': False, 'Accuracy': 0.9682},
 {'Model': 'RandForest', 'PCA': True, 'Accuracy': 0.9393},
 {'Model': 'MLP‑100', 'PCA': False, 'Accuracy': 0.9747},
 {'Model': 'MLP‑100', 'PCA': True, 'Accuracy': 0.9712}]
'''

# Convert and pivot the results
df = pd.DataFrame(results).sort_values(["Model", "PCA"])
pivot_df = df.pivot(index="Model", columns="PCA", values="Accuracy")
pivot_df.columns = ["No PCA", "With PCA"]
pivot_df = pivot_df[["No PCA", "With PCA"]]  # Ensure column order

# Plotting
pivot_df.plot(kind="bar", figsize=(8, 5), color=["#ff9999", "#66b3ff"])
plt.title("Model Accuracy With and Without PCA")
plt.ylabel("Accuracy")
plt.xlabel("Model")
plt.ylim(0.8, 1.0)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(rotation=0)
plt.legend(title="PCA")
plt.tight_layout()
plt.show()

# 6. (Optional) 2‑D PCA scatterplot of a 5 000‑sample subset
# -----------------------------------------------------------
PLOT = True
if PLOT:
    subset = np.random.RandomState(0).choice(np.arange(X_test.shape[0]), size=5000, replace=False)
    pca2 = PCA(n_components=2)
    X_2d = pca2.fit_transform(StandardScaler().fit_transform(X_test[subset]))
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(X_2d[:, 0], X_2d[:, 1], c=y_test[subset], s=10, cmap="tab10", alpha=0.7)
    plt.title("MNIST in two dimensions (PCA)")
    plt.xlabel("PC 1"); plt.ylabel("PC 2")
    plt.tight_layout(); plt.show()

"""
MNIST Classification with PCA + Logistic Regression 


---
"""

#@title 📦 Install / Import Dependencies
# (sklearn, numpy & matplotlib are pre‑installed in Colab; the following import
# block suffices, but keep this cell separate for clarity.)
from __future__ import annotations

import pathlib, random, shutil
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.datasets import fetch_openml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score,
                             classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score)
from sklearn.model_selection import train_test_split

#@title ⚙️ Global Settings
# Feel free to tweak these widgets in the Colab UI.
TEST_SIZE = 0.2  #@param {type:"slider", min:0.1, max:0.3, step:0.05}
VARIANCE_THRESHOLD = 0.95  #@param {type:"slider", min:0.8, max:0.99, step:0.01}
SAVE_FIGURES = False  #@param {type:"boolean"}
FOLDER = pathlib.Path("figures")
if SAVE_FIGURES:
    FOLDER.mkdir(exist_ok=True)
else:
    # Fresh run ‑ remove any prior artefacts to avoid confusion
    shutil.rmtree(FOLDER, ignore_errors=True)

# Utility to optionally save Matplotlib figures

def maybe_save(fig, name: str):
    if SAVE_FIGURES:
        path = FOLDER / f"{name}.png"
        fig.savefig(path, dpi=300, bbox_inches="tight")
        print(f"📁 Saved → {path}")

#@title 🔍 Helper Functions (plotting, mis‑classification gallery)
import itertools


def plot_sample_images(X: np.ndarray, y: np.ndarray, rows: int = 2, cols: int = 5):
    fig, axes = plt.subplots(rows, cols, figsize=(1.7 * cols, 1.7 * rows))
    for ax in axes.flat:
        idx = random.randrange(X.shape[0])
        ax.imshow(X[idx].reshape(28, 28), cmap="gray_r")
        ax.set_title(f"Label: {y[idx]}")
        ax.axis("off")
    fig.suptitle("Random MNIST Samples", fontsize=14)
    fig.tight_layout()
    maybe_save(fig, "sample_images")
    plt.show()


def plot_class_balance(y: np.ndarray):
    counts = pd.Series(y).value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 3))
    counts.plot(kind="bar", ax=ax)
    ax.set_xlabel("Digit"); ax.set_ylabel("Frequency")
    ax.set_title("Class Distribution in MNIST")
    fig.tight_layout()
    maybe_save(fig, "class_balance")
    plt.show()


def plot_explained_variance(pca):
    cum_var = np.cumsum(pca.explained_variance_ratio_)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(cum_var, marker="o")
    ax.axhline(0.95, ls="--", label="95% threshold")
    ax.set(xlabel="# Components", ylabel="Cumulative Explained Variance",
           title="PCA – Variance vs Components")
    ax.legend(); fig.tight_layout()
    maybe_save(fig, "pca_explained_variance")
    plt.show()


def plot_pca_scatter(X_pca, y):
    fig, ax = plt.subplots(figsize=(6, 5))
    scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=y.astype(int), s=8,
                         cmap="tab10", alpha=0.7)
    legend = ax.legend(*scatter.legend_elements(), title="Digit",
                       bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.add_artist(legend)
    ax.set(xlabel="PC 1", ylabel="PC 2", title="First Two Principal Components")
    fig.tight_layout(); maybe_save(fig, "pca_scatter"); plt.show()


def display_misclassified(X_test, y_true, y_pred, max_examples: int = 10):
    mis_idx = np.where(y_true != y_pred)[0]
    if len(mis_idx) == 0:
        print("No misclassifications – perfect classifier (unlikely) ✨")
        return
    examples = np.random.choice(mis_idx, size=min(max_examples, len(mis_idx)), replace=False)
    rows = int(np.ceil(len(examples) / 5))
    fig, axes = plt.subplots(rows, 5, figsize=(10, 2 * rows)); axes = axes.flat
    for i, ax in enumerate(axes):
        if i < len(examples):
            idx = examples[i]
            ax.imshow(X_test[idx].reshape(28, 28), cmap="gray_r")
            ax.set_title(f"T: {y_true[idx]} | P: {y_pred[idx]}")
        ax.axis("off")
    fig.suptitle("Random Misclassifications")
    fig.tight_layout(); maybe_save(fig, "misclassifications"); plt.show()

#@title 🗄️ Load & Prepare MNIST
print("Downloading MNIST (first run may take a minute)…")
mnist = fetch_openml("mnist_784", parser="auto", as_frame=False)
X = mnist.data.astype(np.float32) / 255.0  # Normalise to 0‑1
y = mnist.target.astype(str)
print(f"Dataset shape: {X.shape}; Labels: {np.unique(y)}")

# Quick summary statistics
print("\n*** Pixel Statistics – normalised ***")
print(f"Mean pixel value: {X.mean():.4f}")
print(f"Std pixel value : {X.std():.4f}")

# Plots for Chapter 3
plot_sample_images(X, y)
plot_class_balance(y)

#@title 🔀 Train / Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE,
                                                    stratify=y, random_state=42)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")

#@title 📉 Principal Component Analysis
pca = PCA(n_components=VARIANCE_THRESHOLD, svd_solver="full", random_state=42)
pca.fit(X_train)
print(f"PCA retained {pca.n_components_} components to explain {VARIANCE_THRESHOLD*100:.0f}% variance.")

X_train_pca = pca.transform(X_train)
X_test_pca = pca.transform(X_test)
plot_explained_variance(pca)
plot_pca_scatter(X_train_pca, y_train)

#@title 🤖 Train Logistic Regression Classifier
log_reg = LogisticRegression(max_iter=1000, multi_class="multinomial",
                              solver="lbfgs", n_jobs=-1)
log_reg.fit(X_train_pca, y_train)
print("Model trained ✅")

#@title 📊 Evaluation & Confusion Matrix
from sklearn.metrics import confusion_matrix

y_pred = log_reg.predict(X_test_pca)
print("\n*** Classification Report ***\n")
print(classification_report(y_test, y_pred))
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision (macro):", precision_score(y_test, y_pred, average="macro"))
print("Recall (macro):", recall_score(y_test, y_pred, average="macro"))
print("F1‑score (macro):", f1_score(y_test, y_pred, average="macro"))

cm = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(7, 6))
ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=np.unique(y_test)).plot(ax=ax, cmap="Blues", colorbar=False)
plt.title("Confusion Matrix – Logistic Regression on PCA Features")
plt.tight_layout(); maybe_save(fig, "confusion_matrix"); plt.show()

display_misclassified(X_test, y_test, y_pred)

print("\n TEST_SIZE, VARIANCE_THRESHOLD or SAVE_FIGURES flags above and re‑run the relevant cells to iterate.")
