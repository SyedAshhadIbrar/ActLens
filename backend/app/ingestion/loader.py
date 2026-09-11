from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoadedDocument:
    source_file: str
    text: str
    pages: list[str] | None = None


def load_pdf(path: Path) -> LoadedDocument:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(pages)
    return LoadedDocument(source_file=path.name, text=text, pages=pages)


def load_html(path: Path) -> LoadedDocument:
    from bs4 import BeautifulSoup

    html = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    return LoadedDocument(source_file=path.name, text=text)


def load_text(path: Path) -> LoadedDocument:
    text = path.read_text(encoding="utf-8", errors="replace")
    return LoadedDocument(source_file=path.name, text=text)


def load_document(path: Path) -> LoadedDocument:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix in (".html", ".htm"):
        return load_html(path)
    if suffix in (".txt", ".md"):
        return load_text(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def load_documents(directory: str) -> list[LoadedDocument]:
    data_dir = Path(directory)
    if not data_dir.exists():
        return []

    supported = {".pdf", ".html", ".htm", ".txt", ".md"}
    documents: list[LoadedDocument] = []
    for path in sorted(data_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in supported:
            documents.append(load_document(path))
    return documents
