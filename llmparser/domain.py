from dataclasses import dataclass
from typing import Dict, List, Annotated

@dataclass
class input_product:
    product_title: str
    product_description: str
    product_price: float
    product_features: Dict[str, str]

    @property
    def to_json(self):
        return {
            "title": self.product_title,
            "description": self.product_description,
            "price": self.product_price,
            "features": self.product_features
        }

@dataclass
class source:
    source_url: str
    source_summary: Annotated[str, "a summary of the source content"]

    @property
    def to_json(self):
        return {
            "source_url": self.source_url,
            "source_summary": self.source_summary
        }

@dataclass
class input_context:
    mean_price: float
    std_price: float
    contex_description: Annotated[str, "a description of the median, std price. In other words the llm reasoning"]
    context_sources: List[source]

    @property
    def to_json(self):
        return {
            "mean_price": self.mean_price,
            "std_price": self.std_price,
            "context_description": self.contex_description,
            "context_sources": [source.to_json for source in self.context_sources]
        }

@dataclass
class MSGS:
    user: str
    system: str

    @property
    def to_messages(self):
        return [
            {"role": "user", "content": self.user}
            , { "role": "system", "content": self.system}
        ]