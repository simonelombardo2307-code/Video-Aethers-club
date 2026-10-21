"""Natural daylight Rec.709 look; no matte blacks or blue/teal shadow tint."""
from __future__ import annotations
import numpy as np

CURVE_IN = np.array([0, .025, .06, .12, .22, .40, .58, .76, .88, .95, 1.0], np.float32)
CURVE_OUT = np.array([0, .012, .038, .085, .175, .35, .56, .75, .87, .935, .97], np.float32)


def smoothstep(low, high, x):
    x = np.clip((x - low) / (high - low), 0, 1)
    return x * x * (3 - 2 * x)


def look_rgb(rgb: np.ndarray) -> np.ndarray:
    """The portable LUT portion, operating on normalized display-referred RGB."""
    rgb = np.asarray(rgb, np.float32)
    y = rgb[..., 0] * .2126 + rgb[..., 1] * .7152 + rgb[..., 2] * .0722
    tone = np.interp(y, CURVE_IN, CURVE_OUT).astype(np.float32)
    vegetation = smoothstep(.015, .16, rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2]))
    vegetation *= smoothstep(.06, .28, y)
    saturation = .98 - .13 * vegetation
    chroma_scale = np.minimum(1.0, tone / np.maximum(y, .00001)) * saturation
    out = tone[..., None] + (rgb - y[..., None]) * chroma_scale[..., None]
    # Natural amber sunlight, without tinting deep shadows or a neutral white shirt.
    warmth = smoothstep(.35, .75, y) * (1 - smoothstep(.88, 1.0, y))
    neutral = 1 - smoothstep(.02, .10, np.max(rgb, axis=-1) - np.min(rgb, axis=-1))
    warmth *= 1 - .9 * neutral * smoothstep(.55, .85, y)
    out += warmth[..., None] * np.array([.007, .002, -.006], np.float32)
    out -= (vegetation * .005)[..., None]
    return np.clip(out, 0, 1)


def grade_frame(frame: np.ndarray, source_frame: int, timeline_frame: int) -> np.ndarray:
    rgb = frame.astype(np.float32) / 255
    if source_frame < 118:
        gains, ev = (0.998, 1.0, 1.012), 0.0
    elif source_frame < 200:
        gains, ev = (1.005, 1.0, .998), .005
    elif source_frame < 238:
        gains, ev = (.996, 1.0, 1.008), -.035
    elif source_frame < 541:
        gains, ev = (1.003, 1.002, .999), .015
    else:
        gains, ev = (1.008, 1.002, .995), .015
    balanced = np.clip(rgb * np.array(gains, np.float32) * (2 ** ev), 0, 1)
    out = look_rgb(balanced)
    y = out[..., 0] * .2126 + out[..., 1] * .7152 + out[..., 2] * .0722
    rng = np.random.default_rng(7381 + timeline_frame)
    # Fine monochromatic grain with controlled RMS; blacks and whites stay clean.
    grain = rng.normal(0, .0025, (*y.shape, 1)).astype(np.float32)
    grain *= (.4 + .6 * np.sqrt(np.clip(4 * y * (1 - y), 0, 1)))[..., None]
    out += grain
    return np.clip(np.rint(out * 255), 0, 255).astype(np.uint8)


def save_cube(path, size=33):
    # .cube convention: red varies fastest, then green, then blue.
    grid = np.linspace(0, 1, size, dtype=np.float32)
    b, g, r = np.meshgrid(grid, grid, grid, indexing='ij')
    values = look_rgb(np.stack((r, g, b), axis=-1)).reshape(-1, 3)
    with open(path, 'w') as f:
        f.write('TITLE "Aethers Clean Natural Rec709"\n')
        f.write('# Rec709 SDR input. No Log transform, stabilization, grain or shot balance.\n')
        f.write(f'LUT_3D_SIZE {size}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        np.savetxt(f, values, fmt='%.7f %.7f %.7f')
