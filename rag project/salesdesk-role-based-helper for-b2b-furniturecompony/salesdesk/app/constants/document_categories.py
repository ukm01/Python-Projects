from enum import Enum


class DocumentCategory(str, Enum):
    PRODUCT = "product"
    POLICY = "policy"
    CATALOG = "catalog"
    PRICING = "pricing"
