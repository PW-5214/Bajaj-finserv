import PyPDF2
import docx
import requests
import re
from typing import List, Dict, Any
import logging
from urllib.parse import urlparse
import io

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document processing for various file formats"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
        self.segment_size = 1000  # characters per segment
        self.segment_overlap = 200  # overlap between segments
    
    async def process_document(self, document_url: str) -> str:
        """
        Process document from URL and extract text content
        """
        try:
            # Determine document type from URL
            parsed_url = urlparse(document_url)
            file_extension = self._get_file_extension(parsed_url.path)
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Download document content
            content = await self._download_document(document_url)
            
            # Extract text based on format
            if file_extension == '.pdf':
                text_content = self._extract_pdf_text(content)
            elif file_extension == '.docx':
                text_content = self._extract_docx_text(content)
            else:
                text_content = content.decode('utf-8')
            
            # Clean and normalize text
            cleaned_text = self._clean_text(text_content)
            
            logger.info(f"Successfully processed document: {document_url}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error processing document {document_url}: {str(e)}")
            raise
    
    def segment_document(self, document_content: str) -> List[Dict[str, Any]]:
        """
        Segment document into smaller chunks for better processing
        """
        segments = []
        content_length = len(document_content)
        
        for i in range(0, content_length, self.segment_size - self.segment_overlap):
            end_pos = min(i + self.segment_size, content_length)
            segment_text = document_content[i:end_pos]
            
            # Skip empty segments
            if not segment_text.strip():
                continue
            
            # Extract potential clause information
            clause_info = self._extract_clause_info(segment_text, i)
            
            segment = {
                "text": segment_text,
                "start_position": i,
                "end_position": end_pos,
                "clause_info": clause_info,
                "segment_id": len(segments)
            }
            
            segments.append(segment)
        
        logger.info(f"Document segmented into {len(segments)} segments")
        return segments
    
    def _get_file_extension(self, path: str) -> str:
        """Extract file extension from path"""
        return path.lower().split('.')[-1] if '.' in path else '.txt'
    
    async def _download_document(self, url: str) -> bytes:
        """Download document content from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading document: {str(e)}")
            raise
    
    def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text_content += f"\n--- Page {page_num + 1} ---\n"
                text_content += page_text
                text_content += "\n"
            
            return text_content
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise
    
    def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX content"""
        try:
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            
            text_content = ""
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            
            return text_content
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\-\_\'\"]', '', text)
        
        # Normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def _extract_clause_info(self, segment_text: str, position: int) -> Dict[str, Any]:
        """Extract potential clause information from text segment"""
        clause_info = {
            "page_number": None,
            "clause_number": None,
            "section_number": None,
            "clause_type": None
        }
        
        # Try to extract page number
        page_match = re.search(r'Page (\d+)', segment_text)
        if page_match:
            clause_info["page_number"] = int(page_match.group(1))
        
        # Try to extract clause number (e.g., "Clause 2.4", "Section 3.1")
        clause_match = re.search(r'(?:Clause|Section)\s+(\d+\.?\d*)', segment_text, re.IGNORECASE)
        if clause_match:
            clause_info["clause_number"] = clause_match.group(1)
            clause_info["section_number"] = clause_match.group(1)
        
        # Try to identify clause type
        clause_types = [
            "termination", "payment", "liability", "confidentiality", 
            "non-compete", "intellectual property", "governing law",
            "dispute resolution", "force majeure", "amendment"
        ]
        
        for clause_type in clause_types:
            if clause_type.lower() in segment_text.lower():
                clause_info["clause_type"] = clause_type
                break
        
        return clause_info 