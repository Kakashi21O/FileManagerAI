from datetime import datetime
from pathlib import Path
from core.temporal import TemporalOrganizer


def test_temporal_organizer_extracts_year_month(tmp_path):
    test_file = tmp_path / "photo_vacation.jpg"
    test_file.touch()

    organizer = TemporalOrganizer()
    timeline = organizer.get_timeline_folder(test_file)

    now = datetime.now()
    expected = f"{now.strftime('%Y')}/{now.strftime('%m')}"

    assert timeline == expected
