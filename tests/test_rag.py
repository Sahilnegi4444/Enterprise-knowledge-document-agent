import pytest
from app.rag.chunker import MarkdownChunker
from app.rag.vector_store import get_vector_store
from app.rag.kb_manager import KBManager

def test_markdown_chunker_structure():
    markdown_content = """# Title H1
This is paragraph 1.
## Section H2
This is paragraph 2.
- Bullet 1
- Bullet 2
### Sub-Section H3
Paragraph 3.
"""
    chunks = MarkdownChunker.chunk_document(markdown_content, max_chunk_size=1000)
    assert len(chunks) == 3
    
    # Check H1 chunk
    assert chunks[0]["metadata"]["section"] == "Title H1"
    assert chunks[0]["metadata"]["headings"] == "Title H1"
    assert "This is paragraph 1." in chunks[0]["content"]
    
    # Check H2 chunk
    assert chunks[1]["metadata"]["section"] == "Section H2"
    assert chunks[1]["metadata"]["headings"] == "Title H1 > Section H2"
    assert "Bullet 1" in chunks[1]["content"]
    
    # Check H3 chunk
    assert chunks[2]["metadata"]["section"] == "Sub-Section H3"
    assert chunks[2]["metadata"]["headings"] == "Title H1 > Section H2 > Sub-Section H3"
    assert "Paragraph 3." in chunks[2]["content"]

def test_vector_store_fallback():
    # Use the test database configured in conftest
    vs = get_vector_store()
    vs.clear()
    
    docs = [
        {"content": "Standard operating procedures for deployment.", "metadata": {"document_type": "SOP", "category": "guidelines"}},
        {"content": "Project proposal templates and outlines.", "metadata": {"document_type": "Proposal", "category": "templates"}},
        {"content": "High level system architecture design document.", "metadata": {"document_type": "Architecture", "category": "templates"}}
    ]
    
    vs.add_documents(docs)
    
    # Query without filter
    res = vs.query("proposal template", top_k=1)
    assert len(res) == 1
    assert "proposal" in res[0]["content"].lower()
    
    # Query with metadata filter
    res_filtered = vs.query("design", top_k=2, metadata_filter={"document_type": "Architecture"})
    assert len(res_filtered) == 1
    assert "architecture" in res_filtered[0]["content"].lower()
    
    # Query with filter that should exclude the SOP document containing "deployment"
    res_empty = vs.query("deployment", top_k=2, metadata_filter={"document_type": "Proposal"})
    # It should only return Proposal documents (the SOP document containing 'deployment' is excluded)
    assert len(res_empty) == 1
    assert res_empty[0]["metadata"]["document_type"] == "Proposal"
    assert "proposal" in res_empty[0]["content"].lower()

def test_parse_frontmatter():
    markdown = """---
document_type: SOP
category: standard
version: 3.1
---
# Main Header
Content here.
"""
    meta, body = KBManager.parse_frontmatter(markdown)
    assert meta["document_type"] == "SOP"
    assert meta["category"] == "standard"
    assert meta["version"] == "3.1"
    assert "# Main Header" in body
