import pytest

from app import model

params = [
    ("Artist - Album", ("Album", "Artist", "")),
    (
        "1972 - Good Artist - Good Album (1848 )",
        (
            "Good Album",
            "Good Artist",
            "1848",
        ),
    ),
    ("Album only - 1973", ("Album only", "", "")),
    (
        "Test Artist - Test Album (1982) [Details]",
        ("Test Album", "Test Artist", "Details"),
    ),
]


@pytest.mark.parametrize("folder_name,expected", params)
def test_get_data_from_album_folder_name(folder_name, expected):
    result = model.RawAlbum._get_data_from_album_folder_name(folder_name)
    assert result == expected
