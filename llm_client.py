import os 
from openai import OpenAI

class LLMClient:
    def __init__(self,model: str | None = None,api_key: str | None = None, base_url: str | None = None,temperature: float = 0.2, max_tokens: int = 300):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = OpenAI(**client_kwargs)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role":"system",
                    "content":(
                        "You are a helpful assistant that answers questions based on provided context. "
                        "Use the retrieved document chunks to answer the question. "
                        "Cite the source of your information by including the document name in square brackets, e.g., [doc1.txt]. "
                        "If you don't know the answer, say 'I don't know.' and cite [no_source]."

                    ),
                },
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        content=response.choices[0].message.content
        return content.strip() if content else ""
    