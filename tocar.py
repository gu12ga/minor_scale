import pygame
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

WIDTH = 900
HEIGHT = 200

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escala Microtonal Menor")

FONT = pygame.font.SysFont(None, 32)

SAMPLE_RATE = 44100

# C4
BASE_FREQ = 261.63

# Sua escala em 24 EDO
SCALE = {
    pygame.K_a: ("C", 0),
    pygame.K_s: ("Db/2", 1),
    pygame.K_d: ("Eb", 6),
    pygame.K_f: ("Fb/2", 9),
    pygame.K_g: ("F#/2", 11),
    pygame.K_h: ("G", 14),
    pygame.K_j: ("Ab/2", 15),
    pygame.K_k: ("Bb", 20),
    pygame.K_l: ("B#/2", 23),

    # oitava acima
    pygame.K_q: ("C+", 24),
    pygame.K_w: ("Db/2+", 25),
    pygame.K_e: ("Eb+", 30),
    pygame.K_r: ("Fb/2+", 33),
    pygame.K_t: ("F#/2+", 35),
    pygame.K_y: ("G+", 38),
    pygame.K_u: ("Ab/2+", 39),
    pygame.K_i: ("Bb+", 44),
    pygame.K_o: ("B#/2+", 47),
}

def edo24_freq(step):
    return BASE_FREQ * (2 ** (step / 24))

def piano_wave(freq, duration=2.0):

    t = np.linspace(
        0,
        duration,
        int(SAMPLE_RATE * duration),
        False
    )

    wave = (
        np.sin(2*np.pi*freq*t)
        + 0.5*np.sin(2*np.pi*freq*2*t)
        + 0.3*np.sin(2*np.pi*freq*3*t)
        + 0.15*np.sin(2*np.pi*freq*4*t)
    )

    attack = int(0.00001 * SAMPLE_RATE)
    decay = int(0.15 * SAMPLE_RATE)

    env = np.ones(len(t))

    env[:attack] = np.linspace(0, 1, attack)

    env[attack:attack+decay] = np.linspace(
        1,
        0.6,
        decay
    )

    env[attack+decay:] *= np.exp(
        -4*np.linspace(
            0,
            1,
            len(t)-(attack+decay)
        )
    )

    wave *= env

    wave /= np.max(np.abs(wave))
    wave *= 0.2

    stereo = np.column_stack((wave, wave))

    return np.int16(stereo * 32767)

"""
def piano_wave(freq, duration=4.0):

    t = np.linspace(
        0,
        duration,
        int(SAMPLE_RATE * duration),
        False
    )

    # Base estilo Rhodes:
    # senoides suaves + inharmonicidade leve

    fundamental = 1.0 * np.sin(2 * np.pi * freq * t)

    overtone1 = 0.35 * np.sin(
        2 * np.pi * (freq * 2.01) * t
    )

    overtone2 = 0.18 * np.sin(
        2 * np.pi * (freq * 3.98) * t
    )

    overtone3 = 0.08 * np.sin(
        2 * np.pi * (freq * 6.1) * t
    )

    # Pequena modulação/tremolo
    tremolo = 1 + 0.08 * np.sin(
        2 * np.pi * 4.5 * t
    )

    wave = (
        fundamental
        + overtone1
        + overtone2
        + overtone3
    )

    wave *= tremolo

    # Envelope mais lento
    attack = int(0.08 * SAMPLE_RATE)
    decay = int(0.7 * SAMPLE_RATE)

    env = np.ones(len(t))

    # ataque lento
    env[:attack] = np.linspace(
        0,
        1,
        attack
    )

    # decay suave
    env[attack:attack+decay] = np.linspace(
        1,
        0.75,
        decay
    )

    # sustain longo
    sustain_start = attack + decay

    env[sustain_start:] *= np.exp(
        -1.2 * np.linspace(
            0,
            1,
            len(t)-sustain_start
        )
    )

    wave *= env

    # saturação suave
    wave = np.tanh(wave * 1.3)

    wave /= np.max(np.abs(wave))

    stereo = np.column_stack((wave, wave))

    return np.int16(stereo * 32767)"""

# gera todos os sons uma única vez
SOUNDS = {}

for key, (_, step) in SCALE.items():
    freq = edo24_freq(step)
    arr = piano_wave(freq)
    SOUNDS[key] = pygame.sndarray.make_sound(arr)

running = True

pressed = set()

while running:

    screen.fill((30, 30, 30))

    txt1 = FONT.render(
        "A S D F G H J K L = Escala",
        True,
        (255,255,255)
    )

    txt2 = FONT.render(
        "Q W E R T Y U I O = Oitava acima",
        True,
        (255,255,255)
    )

    txt3 = FONT.render(
        "ESC = sair",
        True,
        (255,255,255)
    )

    screen.blit(txt1, (20, 40))
    screen.blit(txt2, (20, 80))
    screen.blit(txt3, (20, 120))

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key in SOUNDS:

                if event.key not in pressed:

                    pressed.add(event.key)

                    SOUNDS[event.key].play()

        elif event.type == pygame.KEYUP:

            if event.key in pressed:
                pressed.remove(event.key)

pygame.quit()