import os
from typing import Dict, Any, List
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv():
        pass


load_dotenv()


@dataclass
class GibsonConfig:
    """Configuration for GibsonAI integration"""

    # Note: project_uuid is managed dynamically by the agent
    # No API key needed since we use MCP server directly
    pass


@dataclass
class AgentConfig:
    """Configuration for the AI agents"""

    openai_api_key: str
    model: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 2000


@dataclass
class CSVConfig:
    """Configuration for CSV processing"""

    max_size_mb: int = 50
    supported_encodings: List[str] = None
    chunk_size: int = 1000

    def __post_init__(self):
        if self.supported_encodings is None:
            self.supported_encodings = ["utf-8", "latin-1", "cp1252"]


class Config:
    """Main configuration class"""

    def __init__(self):
        self.gibson = GibsonConfig()

        self.agent = AgentConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
        )

        self.csv = CSVConfig(
            max_size_mb=int(os.getenv("MAX_CSV_SIZE_MB", "50")),
            supported_encodings=os.getenv(
                "SUPPORTED_CSV_ENCODINGS", "utf-8,latin-1,cp1252"
            ).split(","),
            chunk_size=int(os.getenv("CSV_CHUNK_SIZE", "1000")),
        )

    def validate(self) -> Dict[str, List[str]]:
        """Validate configuration and return any errors"""
        errors = {}

        if not self.agent.openai_api_key:
            errors.setdefault("agent", []).append("OpenAI API key is required")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "gibson": {
                "mcp_server": "Direct MCP connection via gibson-cli",
                "project_management": "Dynamic project creation/selection",
            },
            "agent": {
                "model": self.agent.model,
                "temperature": self.agent.temperature,
                "max_tokens": self.agent.max_tokens,
                "openai_key_set": bool(self.agent.openai_api_key),
            },
            "csv": {
                "max_size_mb": self.csv.max_size_mb,
                "supported_encodings": self.csv.supported_encodings,
                "chunk_size": self.csv.chunk_size,
            },
        }


# Global configuration instance
config = Config()
