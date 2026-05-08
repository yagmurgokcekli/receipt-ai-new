import time
from typing import Callable, TypeVar

from openai import (
    OpenAI,
    APITimeoutError,
    APIConnectionError,
    RateLimitError,
    InternalServerError,
    APIStatusError,
)

from ..settings import settings
from ..schemas.receipt_schema import ReceiptAnalysis, Source

T = TypeVar("T")


class OpenAIService:
    def __init__(self):
        self.api_key = settings.AZURE_OPENAI_API_KEY
        self.endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.model = settings.AZURE_OPENAI_DEPLOYMENT
        self.client = None

    def _get_client(self) -> OpenAI:
        if self.client is None:
            self.client = OpenAI(
                base_url=self.endpoint,
                api_key=self.api_key,
            )
        return self.client

    def _retry(
        self,
        operation: Callable[..., T],
        *args,
        max_attempts: int = 3,
        **kwargs,
    ) -> T:
        for attempt in range(1, max_attempts + 1):
            try:
                return operation(*args, **kwargs)

            except (
                APITimeoutError,
                APIConnectionError,
                RateLimitError,
                InternalServerError,
            ) as error:
                if attempt == max_attempts:
                    raise RuntimeError("OpenAI temporary service error") from error

                time.sleep(attempt)

            except APIStatusError as error:
                if error.status_code in [408, 429, 500, 502, 503, 504]:
                    if attempt == max_attempts:
                        raise RuntimeError("OpenAI temporary service error") from error

                    time.sleep(attempt)
                    continue

                raise RuntimeError("OpenAI request failed") from error

        raise RuntimeError("Retry failed")

    def analyze_receipt(self, sas_url: str) -> ReceiptAnalysis:
        try:
            client = self._get_client()

            response = self._retry(
                client.beta.chat.completions.parse,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a receipt data extraction system. Extract structured information from receipt images.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract the receipt information.",
                            },
                            {"type": "image_url", "image_url": {"url": sas_url}},
                        ],
                    },
                ],
                response_format=ReceiptAnalysis,
            )

            if response is None or not response.choices:
                raise RuntimeError("OpenAI returned no choices")

            parsed_receipt = response.choices[0].message.parsed

            if parsed_receipt is None:
                raise RuntimeError("OpenAI could not parse the receipt")

            parsed_receipt.source = Source.openai

            return parsed_receipt

        except RuntimeError:
            raise

        except Exception as error:
            raise RuntimeError("OpenAI receipt analysis failed") from error


openai_service = OpenAIService()
