import pytest

from app import import_service

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
    ("Album only - 1973", ("Album only", "", ""))
]


@pytest.mark.parametrize("folder_name,expected", params)
def test_get_data_from_album_folder_name(folder_name, expected):
    result = import_service.get_data_from_album_folder_name(folder_name)
    assert result == expected