from openai import OpenAI
from ..settings import settings
from ..schemas.receipt_schema import ReceiptAnalysis


class OpenAIService:
    def __init__(self):
        self.api_key = settings.AZURE_OPENAI_API_KEY
        self.endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.model = settings.AZURE_OPENAI_DEPLOYMENT

    def _get_client(self):
        return OpenAI(
            base_url=self.endpoint,
            api_key=self.api_key,
        )

    def analyze_receipt(self, sas_url: str) -> ReceiptAnalysis:

        response = self._get_client().beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a receipt data extraction system. Extract structured information from receipt images."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the receipt information."},
                        {"type": "image_url", "image_url": {"url": sas_url}},
                    ],
                },
            ],
            response_format=ReceiptAnalysis,
        )

        if not response.choices:
            raise ValueError("OpenAI returned no choices.")

        parsed_receipt = response.choices[0].message.parsed

        if parsed_receipt is None:
            raise ValueError("OpenAI could not parse the receipt.")

        return parsed_receipt


openai_service = OpenAIService()
