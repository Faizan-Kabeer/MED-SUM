# MedSum Hybrid Model for Efficient Medical Text Summarization

## 📌 Overview

The **MedSum Hybrid Model** is a medical text summarization framework that integrates **extractive** and **abstractive** approaches to generate high-quality, concise, and grammatically correct summaries of medical documents. It leverages the **LexRank algorithm** for extractive summarization and the **T5-small transformer model** for abstractive summarization. The final output undergoes post-processing to ensure readability and accuracy.

---

## ⚙️ System Architecture

The summarization process is divided into four main phases:

1. **Data Preparation Phase**

   * Collect raw medical datasets
   * Apply initial preprocessing
   * Remove empty rows
   * Clean dataset
   * Format dataset for **PyTorch**
   * Generate **training-ready data**

2. **Extractive Phase**

   * Input: Preprocessed medical dataset
   * Apply **LexRank algorithm** for extractive summarization
   * Generate reduced text

3. **Abstractive Phase**

   * Input: Reduced text
   * Apply **T5-small model** for abstractive summarization
   * Generate raw summary in natural language

4. **Enhancement Phase**

   * Post-process raw summary
   * Perform text cleaning
   * Apply grammar correction
   * Apply structural formatting
   * Generate **final summary**

---

## 🛠️ Technologies Used

* **Python**
* **PyTorch** (Deep Learning Framework)
* **LexRank** (Extractive Summarization Algorithm)
* **T5-small** (Transformer-based Model)
* **NLP Libraries** (e.g., NLTK, SpaCy, Hugging Face Transformers)

---

## 🚀 Features

* Combines **extractive** and **abstractive** summarization techniques
* Produces **concise, coherent, and grammatically correct** summaries
* Optimized for **medical text datasets**
* Flexible pipeline that can integrate other transformer models


