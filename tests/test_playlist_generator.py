import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from playlist_generator import PlaylistGenerator


class StubMetadataProcessor:
    def __init__(self, meta_map):
        self.meta_map = meta_map

    class Meta:
        def __init__(self, title, artist):
            self.title = title
            self.artist = artist

    def extract_metadata(self, filepath):
        info = self.meta_map.get(filepath)
        if info:
            title, artist = info
            return self.Meta(title, artist)
        return None


def read_playlist(path):
    lines = [line.strip() for line in open(path, encoding="utf-8") if line.strip() and not line.startswith("#")]
    return lines


def test_generate_playlist_metadata_vs_filename(tmp_path):
    music_dir = tmp_path / "music"
    music_dir.mkdir()
    file1 = music_dir / "SongA - ArtistA.mp3"
    file2 = music_dir / "SongB - ArtistB.mp3"
    file1.write_text("dummy")
    file2.write_text("dummy")

    meta_map = {str(file1): ("MetaSongA", "MetaArtistA")}
    generator = PlaylistGenerator(metadata_processor=StubMetadataProcessor(meta_map))

    out_meta = tmp_path / "playlist_meta.txt"
    assert generator.generate_playlist_from_folder(str(music_dir), str(out_meta), use_metadata=True)
    entries_meta = read_playlist(out_meta)
    assert entries_meta == ["MetaSongA - MetaArtistA", "SongB - ArtistB"]

    out_name = tmp_path / "playlist_name.txt"
    assert generator.generate_playlist_from_folder(str(music_dir), str(out_name), use_metadata=False)
    entries_name = read_playlist(out_name)
    assert entries_name == ["SongA - ArtistA", "SongB - ArtistB"]


def test_generate_playlist_include_subdirs(tmp_path):
    music_dir = tmp_path / "music"
    sub_dir = music_dir / "sub"
    sub_dir.mkdir(parents=True)
    (music_dir / "RootSong - RootArtist.mp3").write_text("dummy")
    (sub_dir / "SubSong - SubArtist.mp3").write_text("dummy")

    generator = PlaylistGenerator()

    out_include = tmp_path / "playlist_include.txt"
    assert generator.generate_playlist_from_folder(
        str(music_dir), str(out_include), include_subdirs=True)
    entries_include = read_playlist(out_include)
    assert entries_include == ["RootSong - RootArtist", "SubSong - SubArtist"]

    out_exclude = tmp_path / "playlist_exclude.txt"
    assert generator.generate_playlist_from_folder(
        str(music_dir), str(out_exclude), include_subdirs=False)
    entries_exclude = read_playlist(out_exclude)
    assert entries_exclude == ["RootSong - RootArtist"]

