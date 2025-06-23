# -*- coding: utf-8 -*-
"""
Universal document processor extracting text and images from various formats.
"""

import os
import io
import logging
import shutil
import base64
import zipfile
# Optional dependency for .rar support
try:
    import rarfile  # needs `pip install rarfile` and unrar/bsdtar on system
except ImportError:
    rarfile = None
import subprocess
from datetime import datetime
from typing import List, Dict, Optional

import fitz  # PyMuPDF
import pandas as pd
from PIL import Image, ExifTags
from PIL import ImageOps  # ← for auto-rotating images by EXIF
from striprtf.striprtf import rtf_to_text
import strip_markdown
import openpyxl
import pytesseract
from dotenv import load_dotenv

from openai import OpenAI   # ⬅️ new-style SDK (≥ 1.0.0)  ✅

# Module-level AI instruction for image description
AI_IMAGE_DESCRIPTION_PROMPT = """You are given a single image of a document. Analyze the image and provide a detailed report with the following structure:

1. General Description
   - Briefly describe the visual appearance of the document (what it looks like)
   - If the document or form is empty or contains no information, skip further processing

2. Document Type Classification
   - Identify the type of document from the image
   - Classify as one of the standard document types if applicable, or mark as "Other document type"

3. Text Content (if applicable)
   - Extract and provide all visible text exactly as it appears
   - Maintain the original order of paragraphs and lines
   - Do not omit or paraphrase anything
   - Accurately identify and preserve all meaningful information (filled form fields and values)

4. Fields and Values
   - For each labeled field, heading, or identifier, specify:
     • Field name (as labeled in the document)
     • Purpose/meaning (brief explanation)

5. Element Summary
   - Provide a comprehensive list of all mentioned elements, fields, and sections
   - Include exact wording and brief context description"""

# ----------------------------------------------------------------------
# Configuration constants
# ----------------------------------------------------------------------
MIN_IMG_PIXELS = 200 * 200
MAX_VISION_CALLS_PER_PAGE = 50
MAX_IMAGE_DIM = 3000
MAX_IMAGE_SIZE = 10 * 1024 * 1024

SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".gif", ".tiff", ".tif", ".bmp"}

# ----------------------------------------------------------------------
# ZIP archive limits
# ----------------------------------------------------------------------
MAX_ZIP_SIZE = 100 * 1024 * 1024        # 100 MB
MAX_ZIP_FILES = 50                      # process at most 50 files per archive

# ----------------------------------------------------------------------
# RAR archive limits (same policy as ZIP)
# ----------------------------------------------------------------------
MAX_RAR_SIZE = 100 * 1024 * 1024      # 100 MB
MAX_RAR_FILES = 50                    # max members to process

# ----------------------------------------------------------------------
# Page limit configuration for multi-page documents
# ----------------------------------------------------------------------
MAX_PAGES_DEFAULT = 10                                  # default page limit
MAX_PAGES_ENV_VAR = "MAX_DOCUMENT_PAGES"               # environment variable name
DISABLE_PAGE_LIMIT_ENV_VAR = "DISABLE_PAGE_LIMIT"      # flag to disable limits

###############################################################################
# Logging configuration
###############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

LOG_DIR = "processed_documents"
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "processing.log"))
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(file_handler)


###############################################################################
# Helper utilities
###############################################################################

def _generate_unique_image_name(source_type: str, original_name: str, extension: str) -> str:
    """
    Generate unique image filename to prevent conflicts across different processing types.
    
    Args:
        source_type: Type of processing (pdf, archive, direct)
        original_name: Original filename without extension
        extension: File extension (without dot)
    
    Returns:
        Unique filename in format: {source_type}_{timestamp}_{counter}_{original_name}.{extension}
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    counter = getattr(_generate_unique_image_name, 'counter', 0) + 1
    _generate_unique_image_name.counter = counter
    # Clean original name to be filename-safe
    clean_name = "".join(c for c in original_name if c.isalnum() or c in ('_', '-')).rstrip()
    return f"{source_type}_{timestamp}_{counter:03d}_{clean_name}.{extension}"

def _ensure_dirs() -> None:
    """Ensure that standard output directories exist."""
    for d in ("images", "tables", LOG_DIR):
        os.makedirs(d, exist_ok=True)


def _save_binary(content: bytes, dest_path: str) -> None:
    """Write binary data to a destination path, creating parent dirs if needed."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(content)

# ----------------------------------------------------------------------
# Utility to save image data (bytes or fitz.Pixmap or PIL.Image)
# ----------------------------------------------------------------------
def _save_image_data(data, dest_path: str) -> None:
    """Save image data (bytes or fitz.Pixmap or PIL.Image) to disk, ensuring parent dirs exist."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    # fitz.Pixmap
    if hasattr(data, "save") and callable(data.save):
        data.save(dest_path)
    # PIL.Image.Image
    elif hasattr(data, "save") and hasattr(data, "format"):
        data.save(dest_path)
    else:
        with open(dest_path, "wb") as f:
            f.write(data)

def _find_soffice() -> str:
    """
    Locate LibreOffice 'soffice' executable.

    Order:
    1. Env variable SOFFICE_PATH
    2. In PATH (`shutil.which`)
    3. macOS default location
    """
    candidates = [
        os.getenv("SOFFICE_PATH"),
        shutil.which("soffice"),
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]
    for p in candidates:
        if p and os.path.isfile(p):
            return p
    raise FileNotFoundError(
        "LibreOffice 'soffice' executable not found. "
        "Install LibreOffice or set env var SOFFICE_PATH."
    )


def _get_page_limit() -> Optional[int]:
    """
    Get page limit configuration from environment variables.
    
    Returns:
        None if page limits are disabled
        int if page limits are enabled (custom or default)
        
    Priority:
        1. DISABLE_PAGE_LIMIT (if true, return None)
        2. MAX_DOCUMENT_PAGES (custom limit)
        3. DEFAULT (10 pages)
    """
    load_dotenv()
    
    # Check if page limits are disabled
    disable_limit = os.getenv(DISABLE_PAGE_LIMIT_ENV_VAR, "").lower()
    if disable_limit in ("true", "1", "yes", "on"):
        logger.info("Page limits disabled via %s environment variable", DISABLE_PAGE_LIMIT_ENV_VAR)
        return None
    
    # Check for custom page limit
    custom_limit = os.getenv(MAX_PAGES_ENV_VAR)
    if custom_limit:
        try:
            limit = int(custom_limit)
            if limit > 0:
                logger.info("Using custom page limit: %d pages (from %s)", limit, MAX_PAGES_ENV_VAR)
                return limit
            else:
                logger.warning("Invalid page limit %s, using default %d", custom_limit, MAX_PAGES_DEFAULT)
        except ValueError:
            logger.warning("Invalid page limit %s, using default %d", custom_limit, MAX_PAGES_DEFAULT)
    
    # Use default
    logger.info("Using default page limit: %d pages", MAX_PAGES_DEFAULT)
    return MAX_PAGES_DEFAULT


###############################################################################
# Document class
###############################################################################
class Document:
    """Universal document processor extracting text / images from many formats."""

    _IMAGE_EXTS = SUPPORTED_IMAGE_FORMATS

    def __init__(self, file_path: str, *, media_dir: str = "media_for_processing") -> None:
        self.media_dir = media_dir
        os.makedirs(self.media_dir, exist_ok=True)

        if not file_path.startswith(self.media_dir):
            self.file_path = os.path.join(self.media_dir, os.path.basename(file_path))
        else:
            self.file_path = file_path

        self.file_name = os.path.basename(self.file_path)
        self.file_ext = os.path.splitext(self.file_name)[1].lower()
        self.file_size = os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0

        self.metadata: Dict[str, str] = {}
        self.text_content: str = ""
        self.tables: List[str] = []
        self.images: List[str] = []

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def process(self) -> None:
        """Detect file type and dispatch to the correct private handler."""
        if self.file_name.startswith("~$"):
            raise ValueError(f"Temporary file detected ('{self.file_name}'). Skipping processing.")

        _ensure_dirs()

        # ─────────────────────────────────────────────────────────────────────
        # Dispatcher: extensions → methods
        # ─────────────────────────────────────────────────────────────────────
        HANDLERS = {
                        ".pdf": self._process_pdf,
                        ".txt": self._process_txt,
                        ".pages": self._process_pages,
                        ".numbers": self._process_numbers,
                        ".xlsx": self._process_spreadsheet,
                        ".xls": self._process_spreadsheet,
                        ".csv": self._process_csv,
                        ".json": self._process_generic_text,
                        ".py": self._process_generic_text,
                        ".html": self._process_generic_text,
                        ".cms": self._process_generic_text,
                        ".css": self._process_generic_text,
                        ".eml": self._process_email,
                        ".mbox": self._process_email,
                        ".rtf": self._process_rtf,
                        ".md": self._process_markdown,
                        ".markdown": self._process_markdown,
                        ".odt": self._process_odt,
                        ".epub": self._process_epub,
                        ".zip": self._process_generic_zip,
                        ".rar": self._process_generic_rar,
            }

        ext = self.file_ext

        # handler selection

        if ext in self._IMAGE_EXTS:
            handler = self._process_image
        elif ext in {".docx", ".doc", ".pptx", ".ppt"}:
            # first convert Office → PDF
            pdf_path = self._convert_to_pdf(self.file_path)
            self.file_path, self.file_name, self.file_ext = pdf_path, os.path.basename(pdf_path), ".pdf"
            handler = self._process_pdf
        else:
            handler = HANDLERS.get(ext)

        if not handler:
            raise ValueError(f"Unsupported file format: {ext}")
        # call the appropriate method
        handler()


    # ------------------------------------------------------------------
    # Format-specific processing methods
    # ------------------------------------------------------------------

    def _process_pdf(self) -> None:
        """
        Extract text and images from PDF:
        – text via page.get_text(\"dict\"), as in the "old" version;
        – saves images, but describes (Vision) only
          large ones and while not exceeding MAX_VISION_CALLS.
        """

        print(f"Processing PDF document {self.file_path}")

        doc = fitz.open(self.file_path)
        self.metadata.update(doc.metadata or {})
        parts: List[str] = []

        # Get page limit configuration
        page_limit = _get_page_limit()
        total_pages = len(doc)
        pages_to_process = min(total_pages, page_limit) if page_limit else total_pages
        
        if page_limit and total_pages > page_limit:
            logger.info("PDF has %d pages, limiting processing to %d pages", total_pages, page_limit)

        for page_number in range(pages_to_process):
            page = doc[page_number]
            vision_calls = 0
            image_counter = 1

            # a) if page has vector graphics/background, take preview pixmap
            if page.get_drawings():
                print(f"Processing page {page_number + 1} with graphics")
                try:
                    pix = page.get_pixmap()
                    img_path = os.path.join(
                        "images",
                        f"{os.path.splitext(self.file_name)[0]}_page{page_number + 1}.png",
                    )
                    _save_image_data(pix, img_path)
                    # print(f"Saving page {page_number + 1} image with graphics")
                    self.images.append(img_path)
                    desc = self._generate_image_description(img_path)
                    # print(f"Processing page {page_number + 1} image with graphics completed")
                    parts.append(f"[========[Page {page_number + 1} with graphics]======== \n {desc}]\n")
                    print(f"Description for page {page_number + 1} with graphics added")
                except Exception as e:
                    logger.error("Pixmap error p.%s: %s", page_number + 1, e)
                    print(f"Error processing page {page_number + 1} image with graphics")

            else:  # b) regular text + embedded raster images
                print(f"Processing page {page_number + 1}: regular text + embedded raster images")
                parts.append(f"========[Page {page_number + 1} regular text + embedded raster images]=======\n")
                page_dict = page.get_text("dict")
                # print("page_dict:", page_dict)
                # print("blocks:", page_dict.get("blocks", []))
                if not page_dict.get("blocks", []):
                    print(f"No text or images found on page {page_number + 1}")
                for block in page_dict.get("blocks", []):
                    # print(block.get("type"))
                    if block.get("type") == 0:  # text block
                        # print(f"Adding text block for page {page_number + 1}")
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                parts.append(span.get("text", ""))

                    elif block.get("type") == 1:  # image block
                        # print(f"Processing image {image_counter} from page {page_number + 1}")
                        parts.append(f"========[Image {image_counter}]========\n")
                        img_bytes = block.get("image")
                        w = block.get("width", 0)
                        h = block.get("height", 0)
                        if w * h < MIN_IMG_PIXELS:
                            continue  # too small — skip
                        img_ext = block.get("ext", "png")
                        # Generate unique filename for PDF embedded image
                        base_name = f"{os.path.splitext(self.file_name)[0]}_img{image_counter}"
                        unique_name = _generate_unique_image_name("pdf", base_name, img_ext)
                        img_path = os.path.join("images", unique_name)
                        try:
                            _save_image_data(img_bytes, img_path)
                            self.images.append(img_path)
                            if vision_calls < MAX_VISION_CALLS_PER_PAGE:
                                desc = self._generate_image_description(img_path)
                                vision_calls += 1
                            else:
                                desc = "(description skipped — Vision limit reached)"
                            parts.append(f"[Image {image_counter}: {desc}] (Image saved to: {img_path})")
                            # print(f"Saving description for image {image_counter} from page {page_number + 1}")
                            image_counter += 1
                        except Exception as e:
                            logger.error("Save/describe image error: %s", e)

                    elif block.get("type") != 0 and block.get("type") != 1:  # other block type
                        print(f"No text or images found on page {page_number + 1}")

            parts.append("\n---\n")

        self.text_content = "".join(parts)
        doc.close()

    def _process_txt(self) -> None:
        with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
            self.text_content = f.read()
        self._inject_basic_metadata()

    def _process_image(self) -> None:
        print(f"Starting raster file processing: {self.file_path}")
        try:
            img = Image.open(self.file_path)
        except Exception as e:
            raise ValueError(f"Cannot open image '{self.file_name}': {e}")

        # — auto-rotate image based on EXIF orientation before resizing
        try:
            exif = img.getexif()
            if exif and exif.get(274):  # 274 is the EXIF Orientation tag
                img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        if max(img.size) > MAX_IMAGE_DIM or self.file_size > MAX_IMAGE_SIZE:
            img.thumbnail((MAX_IMAGE_DIM, MAX_IMAGE_DIM))

        fmt = "JPEG" if img.format and img.format.lower() in {"tiff", "tif"} else (img.format or "PNG")
        # Generate unique filename for direct image processing
        base_name = os.path.splitext(self.file_name)[0]
        unique_name = _generate_unique_image_name("direct", base_name, fmt.lower())
        out_path = os.path.join("images", unique_name)
        _save_image_data(img, out_path)
        self.images.append(out_path)

        exif_data: Dict[str, str] = {}
        try:
            exif = img.getexif() or {}
            for tag, value in exif.items():
                exif_data[ExifTags.TAGS.get(tag, tag)] = value
            if "Orientation" in exif_data:
                # if needed, we can actually rotate the image,
                # but if just saving — reset the tag
                exif_data["Orientation"] = 1
            self.metadata.update(exif_data)
        except Exception:
            logger.debug("No EXIF metadata or failed to parse for '%s'", self.file_name)

        self.text_content = f"{self._generate_image_description(out_path)} (Image saved to: {out_path})"

    def _process_spreadsheet(self) -> None:
        previews: List[str] = []
        base = os.path.splitext(self.file_name)[0]
        try:
            xls = pd.ExcelFile(self.file_path)
        except Exception as e:
            raise ValueError(f"Failed to open Excel: {e}")

        # Get page limit configuration (treat each sheet as one "page")
        page_limit = _get_page_limit()
        total_sheets = len(xls.sheet_names)
        sheets_to_process = min(total_sheets, page_limit) if page_limit else total_sheets
        
        if page_limit and total_sheets > page_limit:
            logger.info("Excel has %d sheets, limiting processing to %d sheets", total_sheets, page_limit)

        for sheet_name in xls.sheet_names[:sheets_to_process]:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)

            # — full export to CSV
            csv_path = os.path.join("tables", f"{base}_{sheet_name}.csv")
            df.to_csv(csv_path, index=False)
            self.tables.append(csv_path)

            # — full CSV text for report
            full_csv = df.to_csv(index=False)

            # — Markdown version for readability
            md = df.to_markdown(index=False)

            previews.append(f"Sheet: {sheet_name} (CSV):\n{full_csv}\n")
            previews.append(f"Sheet: {sheet_name} (Markdown):\n{md}\n")

        self.text_content = "\n".join(previews)

    def _process_csv(self) -> None:
        df = pd.read_csv(self.file_path)
        csv_copy = os.path.join("tables", os.path.basename(self.file_path))
        df.to_csv(csv_copy, index=False)
        self.tables.append(csv_copy)

        # — full CSV text
        full_csv = df.to_csv(index=False)

        # — Markdown table for readability
        md = df.to_markdown(index=False)

        self.text_content = (
            f"CSV (full):\n{full_csv}\n"
            f"CSV (Markdown):\n{md}"
        )

    def _process_generic_text(self) -> None:
        with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
            self.text_content = f.read()
        self._inject_basic_metadata()

    def _process_rtf(self) -> None:
        with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = f.read()
        self.text_content = rtf_to_text(data)
        self._inject_basic_metadata()

    def _process_markdown(self) -> None:
        with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
            md = f.read()
        self.text_content = strip_markdown.strip_markdown(md)
        self._inject_basic_metadata()

    def _process_odt(self) -> None:
        with zipfile.ZipFile(self.file_path, "r") as z:
            if "content.xml" not in z.namelist():
                raise ValueError("ODT missing content.xml")
            raw_xml = z.read("content.xml").decode("utf-8", errors="ignore")
        import re
        text = re.sub(r"<[^>]+>", "", raw_xml.replace("</text:p>", "\n"))
        self.text_content = text.strip()
        self._inject_basic_metadata()

    def _process_epub(self) -> None:
        doc = fitz.open(self.file_path)
        pages = [p.get_text("text") for p in doc]
        self.text_content = "\n".join(pages)
        doc.close()
        self._inject_basic_metadata()

    def _process_pages(self) -> None:
        self._process_zip_bundle(expect_xml=True)

    def _process_numbers(self) -> None:
        self._process_zip_bundle(expect_xml=True)

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _inject_basic_metadata(self) -> None:
        stat = os.stat(self.file_path)
        self.metadata.update(
            {
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "size_bytes": stat.st_size,
            }
        )

    def _process_zip_bundle(self, *, expect_xml: bool = False) -> None:
        with zipfile.ZipFile(self.file_path, "r") as z:
            xml_files = [f for f in z.namelist() if f.endswith(".xml")]
            jpg_files = [f for f in z.namelist() if f.endswith((".jpg", ".png"))]
            if jpg_files:
                data = z.read(jpg_files[0])
                # Generate unique filename for archive extracted image
                original_name = os.path.splitext(os.path.basename(jpg_files[0]))[0]
                extension = os.path.splitext(jpg_files[0])[1][1:]  # Remove the dot
                unique_name = _generate_unique_image_name("archive", original_name, extension)
                img_path = os.path.join("images", unique_name)
                _save_binary(data, img_path)
                self.images.append(img_path)
                self.text_content += f"{self._generate_image_description(img_path)} (Image saved to: {img_path})\n"
            if expect_xml and xml_files:
                with z.open(xml_files[0]) as f:
                    self.text_content += f.read().decode("utf-8", errors="ignore")
            elif expect_xml and not xml_files:
                self.text_content += "(XML not found in bundle)"
        self._inject_basic_metadata()


    def _convert_to_pdf(self, path: str) -> str:
        soffice = _find_soffice()       # ← uses new search function
        output_dir = os.path.dirname(path)
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", output_dir, path],
            check=True,
        )
        pdf_path = os.path.splitext(path)[0] + ".pdf"
        logger.debug("Converted '%s' to PDF via %s", path, soffice)
        return pdf_path

    # ------------------------------------------------------------------
    # OpenAI Vision (updated for SDK ≥1.0.0)
    # ------------------------------------------------------------------

    def _generate_image_description(
        self,
        image_path: str,
        *,
        model: str = "gpt-4.1-mini",
        max_tokens: int = 5000,
        timeout: float = 120,
    ) -> str:
        """
        Generate a short description of an image using GPT-4 Vision.

        • Uses the new `OpenAI` client (SDK ≥ 1.0.0).
        • Adds `timeout` so long-running requests don't block the main thread.
        • In case of error or timeout returns placeholder string.
        """
        load_dotenv()
        api_key = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("API_KEY not set; skipping Vision description.")
            return "(description unavailable)"

        client = OpenAI(api_key=api_key)

        with open(image_path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode()

        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": AI_IMAGE_DESCRIPTION_PROMPT},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                        ],
                    }
                ],
                max_tokens=max_tokens,
                temperature=0,
                timeout=timeout,          # ← key parameter
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error("OpenAI image description failed: %s", e)
            return "(description failed)"

    # Placeholder for email processing
    def _process_email(self) -> None:
        self.text_content = "(email parsing not implemented in this snippet)"

    # ------------------------------------------------------------------
    # Generic ZIP processing
    # ------------------------------------------------------------------
    def _process_generic_zip(self) -> None:
        """
        Handle ordinary .zip archives.

        • Reject archives larger than MAX_ZIP_SIZE.
        • Iterate through at most MAX_ZIP_FILES entries.
        • If an entry is a supported image or document type, extract it
          to a temp sub-folder and recursively process with Document.
        • Unsupported entries are skipped. If nothing useful found,
          a placeholder message is stored in text_content.
        """
        logger.info("Processing ZIP archive '%s' (%d bytes)", self.file_name, self.file_size)

        if self.file_size > MAX_ZIP_SIZE:
            msg = (f"(archive skipped: size {self.file_size} B > "
                   f"{MAX_ZIP_SIZE} B limit)")
            logger.warning("%s %s", self.file_name, msg)
            self.text_content = msg
            return

        extracted_root = os.path.join(
            self.media_dir, "unzipped", os.path.splitext(self.file_name)[0]
        )
        os.makedirs(extracted_root, exist_ok=True)

        useful_files = 0
        try:
            with zipfile.ZipFile(self.file_path, "r") as z:
                names = z.namelist()
                if len(names) > MAX_ZIP_FILES:
                    logger.info("ZIP %s has %d entries; only first %d will be processed",
                                self.file_name, len(names), MAX_ZIP_FILES)

                for idx, name in enumerate(names):
                    if idx >= MAX_ZIP_FILES:
                        break
                    if name.endswith("/"):            # skip dirs
                        continue
                    _, ext = os.path.splitext(name)
                    ext = ext.lower()
                    if ext in self._IMAGE_EXTS or ext in {
                        ".pdf", ".txt", ".pages", ".numbers",
                        ".xlsx", ".xls", ".csv", ".json", ".py",
                        ".html", ".cms", ".css", ".eml", ".mbox",
                        ".rtf", ".md", ".markdown", ".odt", ".epub",
                        ".docx", ".doc", ".pptx", ".ppt"
                    }:
                        dest_path = os.path.join(extracted_root, os.path.basename(name))
                        with z.open(name) as src, open(dest_path, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        logger.info("Extracted %s from %s", name, self.file_name)

                        try:
                            child_doc = Document(dest_path, media_dir=self.media_dir)
                            child_doc.process()
                            useful_files += 1
                            # aggregate outputs
                            self.text_content += (
                                f"\n===== [Extracted: {name}] =====\n"
                                f"{child_doc.text_content}\n"
                            )
                            self.images.extend(child_doc.images)
                            if hasattr(child_doc, "tables"):
                                self.tables.extend(child_doc.tables)
                        except Exception as e:
                            logger.error("Failed processing '%s' inside '%s': %s",
                                         name, self.file_name, e)
                    else:
                        logger.debug("Skipping unsupported entry '%s' in %s", name, self.file_name)
        except Exception as e:
            logger.error("Cannot open ZIP '%s': %s", self.file_name, e)
            self.text_content = "(zip archive corrupted or unreadable)"
            return

        if useful_files == 0:
            self.text_content = "(zip contains no supported documents or images)"

        self._inject_basic_metadata()

    # ------------------------------------------------------------------
    # Generic RAR processing
    # ------------------------------------------------------------------
    def _process_generic_rar(self) -> None:
        """
        Handle ordinary .rar archives similarly to ZIP.

        • Skips if rarfile library is missing.
        • Rejects archives larger than MAX_RAR_SIZE.
        • Processes up to MAX_RAR_FILES entries.
        • Extracts supported documents/images, then recursively processes them.
        """
        if rarfile is None:
            msg = "(rarfile module not installed; .rar skipped)"
            logger.warning("%s %s", self.file_name, msg)
            self.text_content = msg
            return

        logger.info("Processing RAR archive '%s' (%d bytes)", self.file_name, self.file_size)

        if self.file_size > MAX_RAR_SIZE:
            msg = (f"(archive skipped: size {self.file_size} B > "
                   f"{MAX_RAR_SIZE} B limit)")
            logger.warning("%s %s", self.file_name, msg)
            self.text_content = msg
            return

        extracted_root = os.path.join(
            self.media_dir, "unrarred", os.path.splitext(self.file_name)[0]
        )
        os.makedirs(extracted_root, exist_ok=True)

        useful_files = 0
        try:
            with rarfile.RarFile(self.file_path) as rf:
                names = rf.namelist()
                if len(names) > MAX_RAR_FILES:
                    logger.info("RAR %s has %d entries; only first %d will be processed",
                                self.file_name, len(names), MAX_RAR_FILES)

                for idx, name in enumerate(names):
                    if idx >= MAX_RAR_FILES:
                        break
                    if name.endswith("/"):
                        continue
                    _, ext = os.path.splitext(name)
                    ext = ext.lower()
                    if ext in self._IMAGE_EXTS or ext in {
                        ".pdf", ".txt", ".pages", ".numbers",
                        ".xlsx", ".xls", ".csv", ".json", ".py",
                        ".html", ".cms", ".css", ".eml", ".mbox",
                        ".rtf", ".md", ".markdown", ".odt", ".epub",
                        ".docx", ".doc", ".pptx", ".ppt"
                    }:
                        dest_path = os.path.join(extracted_root, os.path.basename(name))
                        with rf.open(name) as src, open(dest_path, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        logger.info("Extracted %s from %s", name, self.file_name)

                        try:
                            child_doc = Document(dest_path, media_dir=self.media_dir)
                            child_doc.process()
                            useful_files += 1
                            self.text_content += (
                                f"\n===== [Extracted: {name}] =====\n"
                                f"{child_doc.text_content}\n"
                            )
                            self.images.extend(child_doc.images)
                            if hasattr(child_doc, "tables"):
                                self.tables.extend(child_doc.tables)
                        except Exception as e:
                            logger.error("Failed processing '%s' inside '%s': %s",
                                         name, self.file_name, e)
                    else:
                        logger.debug("Skipping unsupported entry '%s' in %s", name, self.file_name)
        except Exception as e:
            logger.error("Cannot open RAR '%s': %s", self.file_name, e)
            self.text_content = "(rar archive corrupted or unreadable)"
            return

        if useful_files == 0:
            self.text_content = "(rar contains no supported documents or images)"

        self._inject_basic_metadata()

###############################################################################
# Batch utility
###############################################################################

def batch_process_folder(
    input_folder: str,
    output_file: str = None,
    *,
    preview_chars: int = None,   # how many text characters to write to report
    return_docs: bool = False,   # if True, returns list of dictionaries with results instead of text report
) -> list:
    """
    Traverses *all* files in `input_folder` and nested subfolders.
    For each file:
      • creates unique copy in `media_for_processing/<relpath>`
      • runs Document
      • writes summary to report
    """
    _ensure_dirs()
    # List for returned data of each document
    docs = []  # type: List[dict]
    # Buffer for text report (if return_docs=False)
    results: List[str] = []
    if not return_docs:
        results.append("=== Batch processing report ===\n")

    for root, _, files in os.walk(input_folder):
        for name in sorted(files):
            if name.startswith("."):            # skip .DS_Store etc.
                continue
            abs_path = os.path.join(root, name)
            rel_path = os.path.relpath(abs_path, input_folder)

            # ── ensure unique name in media_for_processing ──
            dest_path = os.path.join("media_for_processing", rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            if not os.path.exists(dest_path):
                shutil.copy2(abs_path, dest_path)

            if not return_docs:
                results.append("======================================")
                results.append(f"File: {rel_path}")

            try:
                doc = Document(dest_path)
                doc.process()
                # Collect document data
                doc_info = {
                    'rel_path': rel_path,
                    'file_ext': doc.file_ext,
                    'file_size': doc.file_size,
                    'metadata': doc.metadata,
                    'text_content': doc.text_content,
                    'absolute_path': dest_path,
                    # List of generated CSV files from tables (if any)
                    'tables': getattr(doc, 'tables', []),
                }
                docs.append(doc_info)
                if not return_docs:
                    # Add to text report
                    results.append(f"Type: {doc.file_ext}")
                    results.append(f"Size: {doc.file_size} bytes")
                    results.append("----------- Metadata -----------")
                    results.extend(f"{k}: {v}" for k, v in doc.metadata.items())
                    results.append("----------- Content -----------")
                    if preview_chars is None:
                        results.append(doc.text_content)
                    else:
                        txt = doc.text_content
                        results.append(txt[:preview_chars] + ("..." if len(txt) > preview_chars else ""))

            except Exception as e:
                results.append(f"ERROR: {e}")

            if not return_docs:
                results.append("======================================\n")

    if return_docs:
        return docs
    # Otherwise — save text report to file
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(results))
        print(f"Batch processing completed. Report at {output_file}")
    return docs


if __name__ == "__main__":
    batch_process_folder(
        "downloaded_files",
        os.path.join("processed_documents_21_04", "final_output_21_04_94.txt"),
    )

# ----------------------------------------------------------------------
# Manual test instructions:
# 1. Create a folder 'test_input' with sample files: PDF, images, .xlsx, .txt.
# 2. Run `batch_process_folder("test_input", "test_report.txt")`.
# 3. Verify outputs:
#    - 'processed_documents' contains .txt reports
#    - 'images' contains saved images for pages and embedded graphics
#    - 'tables' contains CSV exports from spreadsheets
# 4. Inspect logs at processed_documents/processing.log for any errors.
# ----------------------------------------------------------------------