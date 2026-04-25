from enum import Enum


class AssetType(str, Enum):
    SECURITY = "security"
    NETWORK = "network"


class Answer:
    def __init__(
        self,
        justification: str = "",
        answers: dict[str, bool] | None = None,
    ):
        self._justification = justification
        self._answers = answers or {}

    def set_answer(node_id: str, answer: bool):
        return
    def set_justification(justification: str):
        return
    
    def get_answer(node_id: str) -> bool:
        return False
    
    def get_justification() -> str:
        return ""
    

class Asset:
    def __init__(
        self,
        name: str,
        type: AssetType,
        description: str,
        answers: dict[str,Answer] | None = None,
    ):
        self._name = name
        self._type = type
        self._description = description
        self._answers = answers or []
    
    def set_name(self,name:str):
        return
    
    def set_type(self,asset_type:AssetType):
        return
    def set_description(self,description:str):
        return
    
    def set_answer(self,requirement_id:str, node_id:str, answer:bool):
        return 
    
    def get_name(self) -> str:
        return ""
    
    def get_type(self) -> AssetType:
        return AssetType.SECURITY   
    
    def get_description(self) -> str:
        return ""
    
    def get_answer(self, requirement_id:str, node_id:str) -> bool:
        return False


class Device:
    def __init__(
        self,
        id: str,
        name: str,
        os: str,
        description: str,
        assets: list[Asset] | None = None,
    ):
        self._id = id
        self._name = name
        self._os = os
        self._description = description
        self._assets = assets or []

    def add_asset(self, asset: Asset) -> None:
        return

    def remove_asset(self, asset: Asset) -> None:
        return

    def update_asset_info():
        return
    
    def get_id(self) -> str:
        return ""
    
    def get_name(self) -> str:
        return ""
    def get_os(self) -> str:
        return ""   
    def get_description(self) -> str:
        return ""
    def get_assets(self) -> list[Asset]:
        return []
    
    