import re
from typing import List, Dict, Any

class MarkdownChunker:
    @staticmethod
    def chunk_document(content: str, max_chunk_size: int = 1000) -> List[Dict[str, Any]]:
        """
        Splits Markdown text semantically along header boundaries (# H1, ## H2, etc.).
        Returns list of chunks containing text and structural metadata.
        """
        chunks = []
        lines = content.split("\n")
        
        # Keep track of the current headings at each level
        current_headers = {1: "", 2: "", 3: "", 4: "", 5: "", 6: ""}
        current_chunk_text = []
        current_size = 0
        
        heading_pattern = re.compile(r"^(#{1,6})\s+(.*)$")
        
        for line in lines:
            match = heading_pattern.match(line)
            if match:
                # Save previous chunk if it has content
                if current_chunk_text:
                    chunk_str = "\n".join(current_chunk_text).strip()
                    if chunk_str:
                        active_headings = [v for k, v in current_headers.items() if v]
                        section_name = active_headings[-1] if active_headings else "General"
                        chunks.append({
                            "content": chunk_str,
                            "metadata": {
                                "section": section_name,
                                "headings": " > ".join(active_headings)
                            }
                        })
                    current_chunk_text = []
                    current_size = 0
                
                # Update current header hierarchy
                level = len(match.group(1))
                title = match.group(2).strip()
                current_headers[level] = title
                # Clear nested sub-headers
                for l in range(level + 1, 7):
                    current_headers[l] = ""
                
                current_chunk_text.append(line)
                current_size += len(line)
            else:
                current_chunk_text.append(line)
                current_size += len(line)
                
                # Split if chunk limit exceeded
                if current_size >= max_chunk_size:
                    chunk_str = "\n".join(current_chunk_text).strip()
                    if chunk_str:
                        active_headings = [v for k, v in current_headers.items() if v]
                        section_name = active_headings[-1] if active_headings else "General"
                        chunks.append({
                            "content": chunk_str,
                            "metadata": {
                                "section": section_name,
                                "headings": " > ".join(active_headings)
                            }
                        })
                    # Carry forward heading context and last 3 lines for context continuity
                    overlap_lines = current_chunk_text[-3:] if len(current_chunk_text) > 3 else []
                    current_chunk_text = overlap_lines
                    current_size = sum(len(l) for l in current_chunk_text)
                    
        # Flush the final chunk
        if current_chunk_text:
            chunk_str = "\n".join(current_chunk_text).strip()
            if chunk_str:
                active_headings = [v for k, v in current_headers.items() if v]
                section_name = active_headings[-1] if active_headings else "General"
                chunks.append({
                    "content": chunk_str,
                    "metadata": {
                        "section": section_name,
                        "headings": " > ".join(active_headings)
                    }
                })
                
        return chunks
