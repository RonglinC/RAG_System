from bs4 import BeautifulSoup
from pathlib import Path


def load_html(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # remove scripts / styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    return " ".join(text.split())


def load_knowledge_base(folder: str):
    docs = {}

    for file in Path(folder).glob("*.html"):
        docs[file.name] = load_html(file)

    return docs