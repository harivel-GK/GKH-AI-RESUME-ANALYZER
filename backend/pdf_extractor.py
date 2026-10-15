# backend/pdf_extractor.py
"""
PDF text extraction module.
Primary: PyMuPDF (fitz) -- fast, high accuracy.
Fallback: pdfplumber -- handles complex layouts.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extracts text from PDF files using PyMuPDF with pdfplumber fallback."""

    def extract(self, pdf_bytes: bytes, filename: str = "resume.pdf") -> str:
        """
        Extract text from PDF bytes.
        Returns clean text string or raises ValueError if extraction fails.
        """
        text = self._extract_with_fitz(pdf_bytes)

        if not text or len(text.strip()) < 50:
            logger.info(f"fitz extraction insufficient for {filename}, trying pdfplumber...")
            text = self._extract_with_pdfplumber(pdf_bytes)

        if not text or len(text.strip()) < 20:
            raise ValueError(
                f"Could not extract text from {filename}. "
                "The PDF may be scanned/image-based. Please use a text-based PDF."
            )

        return text.strip()

    def _extract_with_fitz(self, pdf_bytes: bytes) -> Optional[str]:
        """Extract text using PyMuPDF (fitz)."""
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pages_text = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                # Extract with layout preservation
                text = page.get_text("text", sort=True)
                if text.strip():
                    pages_text.append(text)

            doc.close()
            return "\n".join(pages_text)

        except ImportError:
            logger.warning("PyMuPDF (fitz) not installed. Install with: pip install PyMuPDF")
            return None
        except Exception as e:
            logger.warning(f"fitz extraction failed: {e}")
            return None

    def _extract_with_pdfplumber(self, pdf_bytes: bytes) -> Optional[str]:
        """Extract text using pdfplumber as fallback."""
        try:
            import pdfplumber
            import io

            pages_text = []
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        pages_text.append(text)

            return "\n".join(pages_text)

        except ImportError:
            logger.warning("pdfplumber not installed. Install with: pip install pdfplumber")
            return None
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
            return None
