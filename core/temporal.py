from datetime import datetime
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class TemporalOrganizer:
    """
    Extracts chronological metadata (creation/modified year and month)
    to organize media and documents into structured timeline folders (YYYY/MM).
    """

    def get_timeline_folder(self, path: Path) -> Optional[str]:
        """
        Determines the 'YYYY/MM' subfolder based on file modification timestamp.
        Returns string like '2024/08' or None if timestamp cannot be read.
        """
        try:
            stat_info = path.stat()
            # Use last modified time (mtime) as reliable cross-platform timestamp
            dt = datetime.fromtimestamp(stat_info.st_mtime)
            year_str = dt.strftime("%Y")
            month_str = dt.strftime("%m")
            return f"{year_str}/{month_str}"
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not read temporal metadata for {path}: {e}")
            return None
