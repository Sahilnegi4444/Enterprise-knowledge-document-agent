import pytest
import os
import shutil

# Force test configuration before importing components
os.environ["GROQ_API_KEY"] = "mock_groq_api_key"
os.environ["TAVILY_API_KEY"] = "mock_tavily_api_key"
os.environ["VECTOR_DB_DIR"] = "./data/chroma_test"

from app.rag.vector_store import vector_store

@pytest.fixture(scope="session", autouse=True)
def clean_test_vector_db():
    """Ensures test database directory is cleared before and after the test run."""
    # Setup
    vector_store.clear()
    yield
    # Teardown
    vector_store.clear()
    test_db_dir = "./data/chroma_test"
    if os.path.exists(test_db_dir):
        try:
            shutil.rmtree(test_db_dir)
        except Exception:
            pass
