from dataclasses import dataclass
 
 
@dataclass(frozen=True)
class InsertJustificationCommand:
    session_id: str
    asset_id: str
    requirement_id: str
    node_id: str
    justification: str
 