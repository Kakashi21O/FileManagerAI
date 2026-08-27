from dataclasses import dataclass
from pathlib import Path
import re
from typing import List, Optional, Set

from models.file_node import FileNode
from models.folder_node import FolderNode


@dataclass
class FileContext:
    file_node: FileNode
    is_in_project: bool
    parent_folder_name: str
    sibling_extensions: Set[str]
    content_snippet: str
    detected_topic: Optional[str] = None
    confidence: float = 0.0
    suggested_target_folder: Optional[str] = None
    reason: str = ""


class ContextEngine:
    """
    Analyzes contextual cues around a file before organizing:
    - Surrounding directory meaning & sibling files
    - Project boundaries
    - Light header/content inspection (e.g. keywords, shebangs, imports, markdown headers)
    - Rejects guessing if confidence is low (< 0.75), routing to Review/ or leaving untouched.
    """

    # Lightweight regex cues for content recognition
    AI_ML_KEYWORDS = {"torch", "tensorflow", "keras", "sklearn", "transformers", "pytorch", "llm", "pipeline", "model"}
    WEB_BACKEND_KEYWORDS = {"flask", "django", "fastapi", "express", "router", "endpoint", "app = Flask", "app = FastAPI"}
    WEB_FRONTEND_KEYWORDS = {"react", "vue", "angular", "next", "tailwind", "useState", "useEffect", "jsx", "tsx"}
    DATA_KEYWORDS = {"pandas", "numpy", "dataframe", "read_csv", "plt.plot", "seaborn"}
    DISCORD_BOT_KEYWORDS = {"discord", "commands.bot", "bot.run", "on_ready", "on_message", "intents", "ctx.send", "client.event", "autocatcher", "topgg", "voter", "sofi", "karuta", "waifu", "poke", "poketwo"}


    def inspect_file_content(self, path: Path, max_bytes: int = 4096) -> str:
        """Reads a bounded header snippet of text/code files safely."""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_bytes)
        except (PermissionError, OSError):
            return ""

    def analyze_context(
        self,
        file_node: FileNode,
        parent_folder: FolderNode,
        project_folders: Set[Path],
    ) -> FileContext:
        # 1. Project Boundary Check (Absolute safety rule: never tear apart a project)
        is_in_project = False
        for proj in project_folders:
            try:
                file_node.path.relative_to(proj)
                is_in_project = True
                break
            except ValueError:
                continue

        if is_in_project:
            return FileContext(
                file_node=file_node,
                is_in_project=True,
                parent_folder_name=parent_folder.name,
                sibling_extensions={f.extension.lower() for f in parent_folder.files},
                content_snippet="",
                confidence=1.0,
                suggested_target_folder=None,
                reason="Protected project component (stay untouched)",
            )

        # 2. Extract Sibling context & parent folder semantic context
        sibling_exts = {f.extension.lower() for f in parent_folder.files if f.path != file_node.path}
        snippet = self.inspect_file_content(file_node.path)
        snippet_lower = snippet.lower()

        topic = None
        target_folder = None
        confidence = 0.0
        reason = ""

        # Content keyword analysis
        words = set(re.findall(r"\b[a-zA-Z_]+\b", snippet_lower))

        if words.intersection(self.DISCORD_BOT_KEYWORDS):
            topic = "Discord/Bot"
            target_folder = "Python/Bots"
            confidence = 0.90
            reason = f"Detected Discord/bot keywords in file content ({', '.join(list(words.intersection(self.DISCORD_BOT_KEYWORDS))[:3])})"
        elif words.intersection(self.AI_ML_KEYWORDS):
            topic = "AI/ML"
            target_folder = "Python/AI"
            confidence = 0.90
            reason = f"Detected AI/ML libraries in file content ({', '.join(words.intersection(self.AI_ML_KEYWORDS))})"
        elif words.intersection(self.WEB_BACKEND_KEYWORDS):
            topic = "Web Backend"
            target_folder = "Python/Backend"
            confidence = 0.90
            reason = f"Detected Web framework in file content ({', '.join(words.intersection(self.WEB_BACKEND_KEYWORDS))})"
        elif words.intersection(self.WEB_FRONTEND_KEYWORDS):
            topic = "Web Frontend"
            target_folder = "Web/Frontend"
            confidence = 0.90
            reason = "Detected Frontend framework keywords in file content"
        elif words.intersection(self.DATA_KEYWORDS):
            topic = "Data Analysis"
            target_folder = "Data"
            confidence = 0.85
            reason = "Detected Data processing libraries in file content"
        else:
            # Check existing folder semantics before guessing
            p_name_lower = parent_folder.name.lower()
            if p_name_lower in {"ai", "ml", "models", "nlp", "src", "source", "lib", "components"}:
                # Keep untouched inside existing structure
                confidence = 0.80
                target_folder = None
                reason = f"Existing structured folder '{parent_folder.name}' (stay untouched)"

            else:
                # Insufficient confidence to make a specific contextual move
                confidence = 0.40
                target_folder = None
                reason = "Insufficient contextual confidence; avoid guessing"

        return FileContext(
            file_node=file_node,
            is_in_project=is_in_project,
            parent_folder_name=parent_folder.name,
            sibling_extensions=sibling_exts,
            content_snippet=snippet[:200],
            detected_topic=topic,
            confidence=confidence,
            suggested_target_folder=target_folder,
            reason=reason,
        )
