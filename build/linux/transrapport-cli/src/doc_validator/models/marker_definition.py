"""MarkerDefinition model for marker specifications with validation rules."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class MarkerType(Enum):
    """Types of markers in the LD-3.4 specification."""
    
    ATO = "ATO"
    SEM = "SEM"
    CLU = "CLU"
    MEMA = "MEMA"


@dataclass
class MarkerDefinition:
    """Represents marker specifications from MARKER.md with validation rules."""
    
    marker_id: str
    marker_type: MarkerType
    definition_source: str
    validation_rules: List[str]
    examples_required: int
    schema_constraints: Dict[str, any]
    
    def __post_init__(self) -> None:
        """Initialize defaults after creation."""
        if self.validation_rules is None:
            self.validation_rules = []
        if self.schema_constraints is None:
            self.schema_constraints = {}
        
        # Set default examples requirement based on marker type
        if self.examples_required <= 0:
            self.examples_required = 5  # LD-3.4 standard requirement
    
    @classmethod
    def create_ato_marker(cls, marker_id: str, definition_source: str) -> "MarkerDefinition":
        """Create a marker definition for ATO type."""
        return cls(
            marker_id=marker_id,
            marker_type=MarkerType.ATO,
            definition_source=definition_source,
            validation_rules=[
                "must_have_pattern",
                "examples_minimum_5",
                "pattern_is_regex"
            ],
            examples_required=5,
            schema_constraints={"required_fields": ["pattern", "examples"]}
        )
    
    @classmethod
    def create_sem_marker(cls, marker_id: str, definition_source: str) -> "MarkerDefinition":
        """Create a marker definition for SEM type."""
        return cls(
            marker_id=marker_id,
            marker_type=MarkerType.SEM,
            definition_source=definition_source,
            validation_rules=[
                "must_have_composed_of",
                "composed_of_minimum_2_ato",
                "examples_minimum_5",
                "window_rule_required"
            ],
            examples_required=5,
            schema_constraints={
                "required_fields": ["composed_of", "examples"],
                "min_composed_of": 2
            }
        )
    
    @classmethod
    def create_clu_marker(cls, marker_id: str, definition_source: str) -> "MarkerDefinition":
        """Create a marker definition for CLU type."""
        return cls(
            marker_id=marker_id,
            marker_type=MarkerType.CLU,
            definition_source=definition_source,
            validation_rules=[
                "must_have_composed_of",
                "activation_rule_required",
                "examples_minimum_5"
            ],
            examples_required=5,
            schema_constraints={
                "required_fields": ["composed_of", "activation", "examples"]
            }
        )
    
    @classmethod
    def create_mema_marker(cls, marker_id: str, definition_source: str) -> "MarkerDefinition":
        """Create a marker definition for MEMA type."""
        return cls(
            marker_id=marker_id,
            marker_type=MarkerType.MEMA,
            definition_source=definition_source,
            validation_rules=[
                "must_have_composed_of_or_detect_class",
                "activation_rule_required",
                "examples_minimum_5"
            ],
            examples_required=5,
            schema_constraints={
                "required_fields": ["examples"],
                "alternative_fields": [["composed_of"], ["detect_class"]]
            }
        )
    
    def validate_marker_id_prefix(self) -> bool:
        """Validate that marker ID has correct prefix for its type."""
        expected_prefix = f"{self.marker_type.value}_"
        return self.marker_id.startswith(expected_prefix)
    
    def get_validation_summary(self) -> Dict[str, any]:
        """Get a summary of validation requirements for this marker."""
        return {
            "marker_id": self.marker_id,
            "type": self.marker_type.value,
            "examples_required": self.examples_required,
            "validation_rules": self.validation_rules,
            "schema_constraints": self.schema_constraints,
            "prefix_valid": self.validate_marker_id_prefix()
        }