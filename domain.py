from dataclasses import dataclass, field
from typing import Dict, Annotated, List


@dataclass
class InputProduct:
    product_title: str
    product_description: str
    product_price: float
    product_features: Dict[str, str] = field(default_factory=dict)

    def to_json(self) -> Dict[str, str]:
        return {
            "title": self.product_title,
            "description": self.product_description,
            "price": self.product_price,
            "features": self.product_features
        }


@dataclass
class OutputResult:
    mean_price: float
    std_price: float
    context_description: str

    def to_json(self) -> Dict[str, str]:
        return {
            "mean_price": self.mean_price,
            "std_price": self.std_price,
            "context_description": self.context_description
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
