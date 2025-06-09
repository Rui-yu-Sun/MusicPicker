import os
import unittest
import tempfile

from playlist_generator import PlaylistGenerator

class TestPlaylistGeneratorScanning(unittest.TestCase):
    def setUp(self):
        # create temporary directory structure
        self.tmp_dir = tempfile.TemporaryDirectory()
        root_path = self.tmp_dir.name
        self.root_file = os.path.join(root_path, "RootSong-Artist.mp3")
        with open(self.root_file, "w") as f:
            f.write("dummy")
        self.sub_dir = os.path.join(root_path, "sub")
        os.makedirs(self.sub_dir, exist_ok=True)
        self.sub_file = os.path.join(self.sub_dir, "SubSong-Artist.mp3")
        with open(self.sub_file, "w") as f:
            f.write("dummy")
        self.gen = PlaylistGenerator()
        self.output_file = os.path.join(root_path, "playlist.txt")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_scan_without_subdirs(self):
        files = self.gen.scan_music_folder(self.tmp_dir.name, include_subdirs=False)
        self.assertIn(self.root_file, files)
        self.assertNotIn(self.sub_file, files)

    def test_scan_with_subdirs(self):
        files = self.gen.scan_music_folder(self.tmp_dir.name, include_subdirs=True)
        self.assertIn(self.root_file, files)
        self.assertIn(self.sub_file, files)

    def test_generate_playlist_without_subdirs(self):
        self.gen.generate_playlist(self.tmp_dir.name, self.output_file,
                                   include_subdirs=False)
        with open(self.output_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if not line.startswith("#") and line.strip()]
        self.assertEqual(lines, ["RootSong - Artist"])

    def test_generate_playlist_with_subdirs(self):
        self.gen.generate_playlist(self.tmp_dir.name, self.output_file,
                                   include_subdirs=True)
        with open(self.output_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if not line.startswith("#") and line.strip()]
        self.assertEqual(set(lines), {"RootSong - Artist", "SubSong - Artist"})

if __name__ == "__main__":
    unittest.main()
