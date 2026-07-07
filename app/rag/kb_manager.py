import os
import re
from typing import List, Dict, Any, Tuple
from app.rag.vector_store import vector_store
from app.rag.chunker import MarkdownChunker
from app.core.logging import logger

class KBManager:
    """Manages parsing, metadata extraction, and ingestion of local markdown knowledge files."""
    
    @staticmethod
    def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
        """
        Parses YAML-like frontmatter enclosed in --- at the start of a markdown file.
        Returns a dictionary of parsed metadata and the main body string.
        """
        metadata = {}
        body = content
        
        # Match frontmatter enclosed in triple dashes
        frontmatter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
        match = frontmatter_pattern.match(content)
        if match:
            frontmatter_text = match.group(1)
            body = content[match.end():]
            
            # Extract basic key-value pairs without using full pyyaml
            for line in frontmatter_text.split("\n"):
                line = line.strip()
                if line and ":" in line and not line.startswith("#"):
                    key, val = line.split(":", 1)
                    metadata[key.strip()] = val.strip().strip('"').strip("'")
        
        return metadata, body

    @classmethod
    def ingest_kb_directory(cls, kb_dir: str) -> int:
        """
        Recursively scans kb_dir for markdown files, chunks them, and adds to Vector Store.
        Returns total chunks ingested.
        """
        if not os.path.exists(kb_dir):
            logger.warning(f"Knowledge Base directory '{kb_dir}' does not exist. Creating empty directory.")
            os.makedirs(kb_dir, exist_ok=True)
            return 0

        logger.info(f"Starting Knowledge Base Ingestion from: {kb_dir}")
        total_chunks = 0
        
        for root, _, files in os.walk(kb_dir):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            raw_content = f.read()
                        
                        metadata, body = cls.parse_frontmatter(raw_content)
                        
                        # Infer metadata from file path and naming
                        rel_path = os.path.relpath(file_path, kb_dir)
                        parts = rel_path.split(os.sep)
                        
                        document_type = metadata.get("document_type")
                        if not document_type:
                            document_type = os.path.splitext(file)[0].replace("_", " ").title()
                            
                        category = metadata.get("category")
                        if not category:
                            category = parts[0] if len(parts) > 1 else "general"
                            
                        version = metadata.get("version", "1.0")
                        
                        # Chunk the document semantically
                        chunks = MarkdownChunker.chunk_document(body)
                        
                        # Convert to ingestion format
                        documents_to_add = []
                        for chunk in chunks:
                            chunk_metadata = {
                                "document_type": document_type,
                                "category": category,
                                "version": version,
                                "source_file": file,
                                **chunk["metadata"]
                            }
                            documents_to_add.append({
                                "content": chunk["content"],
                                "metadata": chunk_metadata
                            })
                            
                        if documents_to_add:
                            vector_store.add_documents(documents_to_add)
                            total_chunks += len(documents_to_add)
                            logger.info(f"Ingested {len(documents_to_add)} chunks from: {rel_path}")
                    except Exception as e:
                        logger.error(f"Failed to ingest knowledge file '{file_path}': {e}")
                        
        logger.info(f"Knowledge Base Ingestion completed. Total chunks loaded: {total_chunks}")
        return total_chunks
