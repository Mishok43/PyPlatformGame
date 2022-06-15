"""Audio test is responsible for testing AudioManager."""

import os
import unittest
import pygame

from PyPlatformGame.audiomanager import AudioManager


class AudioManagerTest(unittest.TestCase):
    """Test class for validating AudioManager."""

    def setup_audiomanager(self):
        """Setuping audiomanager before testing."""
        sounds_folder  = os.path.join('PyPlatformGame', 'assets', 'testsounds')
        AudioManager().init_sounds(sounds_folder, "")

    def test_loading(self):
        """Checking loading sounds from a test folder."""
        self.setup_audiomanager()
        audio_manager = AudioManager()
        loaded_sounds = audio_manager.get_loaded_sounds()
        self.assertEqual(len(loaded_sounds.keys()), 3)
        self.assertTrue('pop1.wav' in loaded_sounds)
        self.assertTrue('pop2.mp3' in loaded_sounds)
        self.assertTrue('pop3.wav' in loaded_sounds)

    def test_handlers(self):
        """Checking work with handles of sounds."""
        self.setup_audiomanager()
        audio_manager = AudioManager()

        self.assertEqual(audio_manager.get_sound_handle('pop1.wav'), 0)
        self.assertEqual(audio_manager.get_sound_handle('pop2.mp3'), 1)
        self.assertEqual(audio_manager.get_sound_handle('pop3.wav'), 2)

    def test_playing(self):
        """Checking sound playing."""
        self.setup_audiomanager()

        audio_manager = AudioManager()
        handle_1 = audio_manager.get_sound_handle('pop1.wav')
        handle_2 = audio_manager.get_sound_handle('pop2.mp3')
        handle_3 = audio_manager.get_sound_handle('pop3.wav')

        self.assertTrue(audio_manager.play_sound(handle_1))
        self.assertTrue(audio_manager.play_sound(handle_2))
        self.assertTrue(audio_manager.play_sound(handle_3))


if __name__ == '__main__':
    pygame.mixer.pre_init(44100, 16, 1, 512)
    pygame.init()
    unittest.main()
