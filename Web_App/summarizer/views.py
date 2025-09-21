from django.shortcuts import render,redirect
import pandas as pd
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import nltk
import pandas as pd
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer as SumyTokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from tqdm import tqdm
nltk.download("punkt_tab")
import re
import language_tool_python
from django.shortcuts import render, redirect
import fitz  # PyMuPDF for PDF text extraction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings

def home(request):

    tool = language_tool_python.LanguageTool('en-US')

    def extract_text_from_pdf(pdf_path):

        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text.strip()

    def clean_text(text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text, flags=re.IGNORECASE)
        sentences = text.split('. ')
        unique_sentences = list(dict.fromkeys(sentences))
        cleaned_text = '. '.join(unique_sentences)
        return cleaned_text.strip()

    def grammar_check(text):
        matches = tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)
        return corrected_text

    import re

    def structure_summary_regex(text):
        # Define patterns for different sections
        section_patterns = [
            r"(?:background and objectives|background|objectives)\s*[:\-]?\s*(.*?)(?=\b(?:materials and methods|methods|results|conclusion)\b|$)",
            r"objectives\s*[:\-]?\s*(.*?)(?=\b(?:materials and methods|methods|results|conclusion)\b|$)",
            r"(?:materials and methods|methods)\s*[:\-]?\s*(.*?)(?=\b(?:results|conclusion)\b|$)",
            r"results\s*[:\-]?\s*(.*?)(?=\b(?:conclusion)\b|$)",
            r"conclusion\s*[:\-]?\s*(.*)",
        ]

        section_names = ["Background", "Objectives", "Methods", "Results", "Conclusion"]
        
        sections = {}

        for section_name, pattern in zip(section_names, section_patterns):
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_name] = match.group(1).strip()

        return sections


    def post_process_summary(raw_summary):
        print("🔧 Running Improved Post-Processing Pipeline...")

        # Step 1: Clean raw text
        cleaned_text = clean_text(raw_summary)
        print("✅ Cleaned text")

        # Step 2: Grammar and style correction
        corrected_text = grammar_check(cleaned_text)
        print("✅ Grammar checked")

        # Step 3: Structured summary using regex
        sections = structure_summary_regex(corrected_text)
        if not sections:
            print("⚠ Could not structure sections, returning corrected text")
            return corrected_text

        structured_summary = ""
        for section, content in sections.items():
            structured_summary += f"{section}:\n{content}\n\n"

        print("✅ Structuring complete")

        return structured_summary[:-2]+"."



    # Initialize LexRank summarizer once
    summarizer = LexRankSummarizer()

    def lexrank_summarize(article_text, base_sentences=5):
        try:
            word_count = len(article_text.split())

            # Dynamically set number of sentences based on article length
            if word_count > 5000:
                num_sentences = base_sentences + 5  # e.g., 10 sentences
            elif word_count > 2000:
                num_sentences = base_sentences + 2  # e.g., 7 sentences
            else:
                num_sentences = base_sentences      # e.g., 5 sentences

            # Parse the text and summarize
            parser = PlaintextParser.from_string(article_text, SumyTokenizer("english"))
            summary_sentences = summarizer(parser.document, num_sentences)

            # Join sentences into a single summary text
            summary_text = " ".join(str(sentence) for sentence in summary_sentences)

            # Fallback to original article if summary is empty
            return summary_text if summary_text.strip() != "" else article_text

        except Exception as e:
            print(f"Error summarizing article: {e}")
            return article_text

    # Path to your checkpoint
    checkpoint_dir = "epoch3-t5"

    # Load model from checkpoint (ensure 'from_pretrained' points to the checkpoint path)
    model = T5ForConditionalGeneration.from_pretrained(checkpoint_dir)

    # Load tokenizer (use base model tokenizer if checkpoint lacks tokenizer files)
    tokenizer = T5Tokenizer.from_pretrained("t5-base")

    def generate_summary(text, model, tokenizer, max_input_length=512):
        # Tokenize input text
        inputs = tokenizer(text, return_tensors="pt", max_length=max_input_length, truncation=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        # Generate summary (adjust parameters for better control)
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_length=208,
                min_length=50,
                length_penalty=2.0,  
                num_beams=1,
                no_repeat_ngram_size=5,
                early_stopping=True
            )

        # Decode and return the summary
        summary = tokenizer.decode(output[0], skip_special_tokens=True)
        return summary
    
    final_summary=None

    if request.method == "POST":
        
        if request.POST['article']!="":  # Text input
            article = request.POST.get("article")
            if article:
                extractive_summary = lexrank_summarize(article)
                summary = generate_summary(extractive_summary, model, tokenizer)
                final_summary = post_process_summary(summary)

        elif "pdf_file" in request.FILES:  # PDF upload
            uploaded_file = request.FILES["pdf_file"]
            
            # Ensure the uploads directory exists
            upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
            os.makedirs(upload_dir, exist_ok=True)

            # Save file to MEDIA_ROOT/uploads/
            file_path = os.path.join(upload_dir, uploaded_file.name)

            with open(file_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            
            # Extract text from PDF
            pdf_text = extract_text_from_pdf(file_path)

            if pdf_text:
                extractive_summary = lexrank_summarize(pdf_text)
                summary = generate_summary(extractive_summary, model, tokenizer)
                final_summary = post_process_summary(summary)

    return render(request, "index.html", {"summary": final_summary})
