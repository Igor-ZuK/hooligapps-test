"""Type aliases for convenient typing annotation. For details see PEP-613."""
from typing import Any

# Dictionary representation of json data
JsonDct = dict[str, Any]

# List representation of json data
JsonLst = list[JsonDct]
