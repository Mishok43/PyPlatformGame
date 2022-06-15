"""Module is rensposible for loading, playing sounds and music."""

import os
from pygame import mixer
from .singleton import Singleton

class AudioManager(metaclass=Singleton):
    """
    AudioManager class for loading, managing and playing sounds and musics.

    :param sounds_folder_dir: path to folder which contains all sounds
    :param music_folder_dir: path to folder which contains all musics
    :param sound: array with mixer.Sounds
    :param sounds_handles: dictionary with mapping between sounds handles and mixer.Sounds
    :param sound_volume: volume factor which applyies to every sound effect
    :param sounds_volumes: array with sound volume for every sound effect
    """

    SOUNDS_EXTENSIONS = ['.wav', '.mp3']


    def init_sounds(self, sounds_folder_dir: str, music_folder_dir: str):
        """Initialize AudioManager with passing paths to a folder with sounds and music effects.

        It runs loads_sounds automatically.

        :param sounds_folder_dir: path to folder which contains all sounds
        :param music_folder_dir: path to folder which contains all musics
        """
        self.sounds_folder_dir = sounds_folder_dir
        self.music_folder_dir = music_folder_dir
        mixer.init()
        self.load_sounds()

    def __init__(self):
        """Initialize AudioManager with default variables."""
        self.sounds = []
        self.sounds_handles = {}
        self.sound_volume = 0.5
        self.sounds_volumes = {}
        self.sounds_folder_dir = ""
        self.music_folder_dir = ""


    def load_sounds(self):
        """Load every sound file from sounds_folder_dir which was defined in constructor.

        It support .wav and .mp4 file formats.
        For every sound algorithm allocate a unique handle,
        which can be requested by get_sound_handle.
        """
        for _, _, files in os.walk(self.sounds_folder_dir):
            for file in files:
                filename, ext = os.path.splitext(file)
                if ext in self.SOUNDS_EXTENSIONS:
                    sound = mixer.Sound(os.path.join(self.sounds_folder_dir,filename+ext))
                    handle_sound = len(self.sounds)
                    self.sounds.append(sound)
                    self.sounds_handles[filename+ext] = handle_sound

    def get_sound_handle(self, filename: str) -> int:
        """
        Return a sound handle based on a filename, based on preloaded sounds.

        :param filename: sound filename

        :return: In a case when there's no any sound with requested filename, the methods Return -1.
        """
        if filename in self.sounds_handles:
            return self.sounds_handles[filename]

        return -1


    def get_loaded_sounds(self) -> dict:
        """
        Return dictionary  of loaded sounds.

        :return: dict <sound_filename, handle> of loaded sounds
        """
        return self.sounds_handles

    def play_sound(self, handle: int, volume: float=1.0) -> int:
        """
        Play a sound based on its handle.

        :param handle: sound handle
        :param volume: sound volume

        :return: If handle is correct, Return 1. Else in Return 0
        """
        if handle < 0 or handle >= len(self.sounds):
            return 0

        self.sounds_volumes[handle] = volume
        self.sounds[handle].play()
        self.sounds[handle].set_volume(self.sounds_volumes[handle]*self.sound_volume)
        return 1

    def play_sound_by_name(self, filename: str, volume: float=1.0) -> int:
        """
        Play a sound based on its filename.

        :param filename: sound filename
        :param volume: sound volume

        :return: If filename is correct, Return 1. Else in Return 0
        """
        return self.play_sound(self.get_sound_handle(filename), volume)

    def play_background_music(self, filename: str , loop: int=-1, volume: float=0.5):
        """
        Will load a music file object and prepare it for playback.

        If a music stream is already playing it will be stopped.
        This does not start the music playing.

        :param filename: music filename
        :param loop: number of iterations for playing. -1 = endlessly
        :param volume: background volume
        """
        mixer.music.load(os.path.join(self.music_folder_dir,filename))
        mixer.music.play(loop)
        mixer.music.set_volume(volume)


    def stop_background_music(self):
        """Will stop music playing."""
        mixer.music.stop()

    def set_background_volume(self, volume: float):
        """
        Will change volume of playing the background music.

        Volume from 0 to 1.

        :param volume: music volume
        """
        mixer.music.set_volume(volume)

    def get_background_volume(self) -> float:
        """
        Get background music volume.

        :return: background music volume
        """
        return mixer.music.get_volume()

    def set_sounds_volume(self, volume: float):
        """
        Will change volume of all sounds.

        :param volume: music volume
        """
        volume = min(max(volume, 0.0), 1.0)
        self.sound_volume = volume

        for i_s, _ in enumerate(self.sounds):
            mul =  self.sounds_volumes[i_s] if (i_s in self.sounds_volumes) else 1.0
            self.sounds[i_s].set_volume(mul*self.sound_volume)

    def get_sounds_volume(self) -> float:
        """
        Get sounds volume.

        :return: sounds volume
        """
        return self.sound_volume

    def set_sound_volume(self, handle: int, volume: float) -> int:
        """
        Will change volume of a particular sound based on its handle.

        :param handle: sound handle
        :param volume: sound volume

        :return: If handle is correct, Return 1. Else in Return 0
        """
        if handle < 0 or handle >= len(self.sounds):
            return 0

        volume = min(max(volume, 0.0), 1.0)

        self.sounds_volumes[handle] = volume
        self.sounds[handle].set_volume(volume*self.sound_volume)
        return 1


    def stop_sound(self, handle: int) -> int:
        """
        Will stop a particular sound.

        :param handle: sound handle

        :return: If handle is correct, Return 1. Else in Return 0
        """
        if handle < 0 or handle >= len(self.sounds):
            return 0

        self.sounds[handle].stop()
        return 1

    def stop_all_sounds(self):
        """Stop every sound."""
        for sound in self.sounds:
            sound.stop()
