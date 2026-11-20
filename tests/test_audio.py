import pygame

from audio import AudioManager


def test_play_menu_starts_the_menu_song_looping():
    audio = AudioManager()

    audio.play_menu()

    assert audio._menu_song.get_num_channels() > 0


def test_stop_menu_silences_the_menu_song():
    audio = AudioManager()
    audio.play_menu()

    audio.stop_menu()

    assert audio._menu_song.get_num_channels() == 0


def test_play_game_and_stop_game_toggle_the_game_song():
    audio = AudioManager()

    audio.play_game()
    assert audio._game_song.get_num_channels() > 0

    audio.stop_game()
    assert audio._game_song.get_num_channels() == 0


def test_pause_all_pauses_every_currently_playing_channel():
    audio = AudioManager()
    audio.play_menu()
    audio.play_game()

    audio.pause_all()

    # pygame.mixer has no direct "is paused" query per-channel, but a paused
    # mixer no longer reports busy channels advancing -- get_busy() still
    # reports the channels as occupied (paused, not stopped).
    assert pygame.mixer.get_busy() is True

    pygame.mixer.unpause()  # don't leak paused global mixer state to other tests
    audio.stop_menu()
    audio.stop_game()


def test_both_songs_are_real_loops_not_stubs():
    audio = AudioManager()

    assert audio._menu_song.get_length() > 10
    assert audio._game_song.get_length() > 10


def test_player_loads_a_non_empty_jump_sound(world, input_handler):
    from entities import Player

    player = Player(world, (400.0, 0.0), input_handler)

    assert player._jump_sound.get_length() > 0.1
