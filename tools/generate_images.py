"""
generate_images.py - builds the original artwork used by the CineSpark website.

Creates these files in assignment2/images/:
    logo.png, favicon.png       site logo and browser-tab icon
    hero.jpg                    home page illustration (cinema audience)
    movie1.jpg ... movie9.jpg   posters for the nine fictional movies

All artwork is drawn from simple shapes and standard Windows fonts using the
Pillow library, so the website does not use any third-party images.

Usage (from the repository root):
    python tools/generate_images.py
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "assignment2", "images")
FONT_DIR = "C:/Windows/Fonts/"

SCALE = 2                              # draw at 2x, then shrink for smooth edges
PW, PH = 400 * SCALE, 600 * SCALE      # poster canvas size

RATING_COLOURS = {
    "G": ("#15803d", "#ffffff"),
    "PG": ("#facc15", "#1a1a1a"),
    "M": ("#2563eb", "#ffffff"),
    "MA15+": ("#dc2626", "#ffffff"),
}


# ---------------------------------------------------------------------------
# Small drawing helpers
# ---------------------------------------------------------------------------
def s(value):
    """Convert a 1x design measurement to canvas pixels."""
    return int(round(value * SCALE))


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), int(size))


def hex_rgb(colour):
    colour = colour.lstrip("#")
    return tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4))


def rgba(colour, alpha=255):
    return hex_rgb(colour) + (alpha,)


def mix(c0, c1, t):
    a, b = hex_rgb(c0), hex_rgb(c1)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(size, stops):
    """Vertical gradient image. stops = [(0.0, '#hex'), ..., (1.0, '#hex')]."""
    width, height = size
    img = Image.new("RGBA", size)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / max(height - 1, 1)
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0) if p1 > p0 else 0
                draw.line([(0, y), (width, y)], fill=mix(c0, c1, k) + (255,))
                break
    return img


def draw_on(img, fn, blur=0):
    """Run fn(draw) on a transparent layer, optionally blur it, then blend onto img."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer))
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


def glow(img, box, colour, blur, alpha=255):
    draw_on(img, lambda d: d.ellipse(box, fill=rgba(colour, alpha)), blur)


def bottom_shade(img, height, alpha, colour="#05050c"):
    """Darken the bottom of an image so small print stays readable."""
    shade = Image.new("RGBA", (img.width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shade)
    for y in range(height):
        draw.line([(0, y), (img.width, y)], fill=rgba(colour, int(alpha * y / height)))
    img.alpha_composite(shade, (0, img.height - height))


def rotated_rect(cx, cy, w, h, angle):
    a = math.radians(angle)
    points = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        points.append((cx + dx * math.cos(a) - dy * math.sin(a),
                       cy + dx * math.sin(a) + dy * math.cos(a)))
    return points


def heart_points(cx, cy, size, angle=0):
    a = math.radians(angle)
    points = []
    for i in range(72):
        t = 2 * math.pi * i / 72
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        x, y = x * size / 16, y * size / 16
        points.append((cx + x * math.cos(a) - y * math.sin(a),
                       cy + x * math.sin(a) + y * math.cos(a)))
    return points


def gear(draw, cx, cy, r, teeth, colour):
    points = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4)
        radius = r if i % 4 in (0, 1) else r * 0.8
        points.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    draw.polygon(points, fill=colour)
    hole = r * 0.35
    draw.ellipse((cx - hole, cy - hole, cx + hole, cy + hole), fill=(0, 0, 0, 0))


def branch(draw, x, y, angle, length, width, depth, rnd, colour):
    """Recursive bare tree branch (used on the horror poster)."""
    if depth == 0 or length < 3:
        return
    x2 = x + math.cos(math.radians(angle)) * length
    y2 = y - math.sin(math.radians(angle)) * length
    draw.line((x, y, x2, y2), fill=colour, width=max(1, int(width)))
    for delta in (-rnd.uniform(15, 38), rnd.uniform(15, 38)):
        branch(draw, x2, y2, angle + delta, length * rnd.uniform(0.6, 0.78),
               width * 0.66, depth - 1, rnd, colour)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def text_width(text, fnt, tracking=0):
    if not tracking:
        left, _, right, _ = fnt.getbbox(text)
        return right - left
    return sum(fnt.getlength(ch) for ch in text) + tracking * (len(text) - 1)


def put_text(draw, x, y, text, fnt, fill, tracking=0, stroke=0, stroke_fill=None):
    if not tracking:
        draw.text((x, y), text, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        return
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += fnt.getlength(ch) + tracking


def fit(name, text, max_width, max_size, tracking=0):
    size = max_size
    while size > 12 and text_width(text, font(name, size), tracking) > max_width:
        size -= 2
    return font(name, size)


def centered_text(img, top, text, fnt, colour, alpha=255, tracking=0,
                  stroke=0, stroke_colour=None, halo=None):
    """Draw text centred horizontally with its glyph tops at `top`. Returns glyph bottom."""
    bbox = fnt.getbbox(text)
    width = text_width(text, fnt, tracking)
    x = (img.width - width) / 2 - (0 if tracking else bbox[0])
    y = top - bbox[1]
    if halo:
        halo_colour, radius = halo
        draw_on(img, lambda d: put_text(d, x, y, text, fnt, rgba(halo_colour), tracking,
                                        stroke + max(2, radius // 3), rgba(halo_colour)), radius)
    stroke_fill = rgba(stroke_colour) if stroke_colour else None
    draw_on(img, lambda d: put_text(d, x, y, text, fnt, rgba(colour, alpha), tracking,
                                    stroke, stroke_fill))
    return y + bbox[3]


def finish_poster(img, lines, title_top, tagline, rating, ink="#ffffff",
                  tag_colour=None, shade=True):
    """Add the shared poster typography: studio line, title, tagline and rating row."""
    if shade:
        bottom_shade(img, s(190), 215)
    centered_text(img, s(22), "CINESPARK PICTURES PRESENTS", font("arialbd.ttf", s(11)),
                  ink, 210, tracking=s(3))

    y = title_top
    for line in lines:
        y = centered_text(img, y, line["text"], line["font"], line["colour"],
                          tracking=line.get("tracking", 0), stroke=line.get("stroke", 0),
                          stroke_colour=line.get("stroke_colour"), halo=line.get("halo"))
        y += line.get("gap", s(8))

    if tagline:
        centered_text(img, y + s(6), tagline, fit("georgiai.ttf", tagline, s(340), s(16)),
                      tag_colour or ink, 240)

    centered_text(img, s(530), "A CINESPARK ORIGINAL  \u2022  ORIGINAL ARTWORK  \u2022  FICTIONAL FILM",
                  font("ARIALN.TTF", s(10)), ink, 190, tracking=s(1))

    # Rating badge + "IN CINEMAS NOW", centred together as one row
    label = "IN CINEMAS NOW"
    label_font = font("arialbd.ttf", s(15))
    badge_font = font("arialbd.ttf", s(13))
    box_w = s(58) if rating == "MA15+" else s(38)
    gap = s(12)
    total = box_w + gap + text_width(label, label_font, s(3))
    x0 = (PW - total) / 2
    box = (x0, s(551), x0 + box_w, s(577))
    centre_y = (box[1] + box[3]) / 2
    fill, text_colour = RATING_COLOURS[rating]

    def row(d):
        d.rounded_rectangle(box, radius=s(4), fill=rgba(fill))
        bb = badge_font.getbbox(rating)
        d.text((x0 + (box_w - (bb[2] - bb[0])) / 2 - bb[0], centre_y - (bb[1] + bb[3]) / 2),
               rating, font=badge_font, fill=rgba(text_colour))
        lb = label_font.getbbox(label)
        put_text(d, x0 + box_w + gap, centre_y - (lb[1] + lb[3]) / 2, label, label_font,
                 rgba(ink), tracking=s(3))
    draw_on(img, row)


def save_poster(img, number):
    path = os.path.join(OUT_DIR, "movie%d.jpg" % number)
    img.convert("RGB").resize((400, 600), Image.Resampling.LANCZOS).save(
        path, quality=86, optimize=True, progressive=True)
    print("saved", path)


def new_poster(stops):
    return gradient((PW, PH), stops)


# ---------------------------------------------------------------------------
# Posters
# ---------------------------------------------------------------------------
def poster_skyline():
    img = new_poster([(0, "#120c2c"), (0.4, "#4a1a5c"), (0.72, "#e2553a"), (1, "#ffb347")])
    glow(img, (s(95), s(235), s(305), s(445)), "#ffd27a", s(40), 230)
    draw_on(img, lambda d: d.ellipse((s(140), s(280), s(260), s(400)), fill=rgba("#ffe2a8")))

    def buildings(d, colour, base, variance, window, seed, wmin, wmax):
        rnd = random.Random(seed)
        x = -s(10)
        while x < PW:
            bw = s(rnd.randint(wmin, wmax))
            top = PH - s(base + rnd.randint(0, variance))
            d.rectangle((x, top, x + bw, PH), fill=rgba(colour))
            if window:
                for wy in range(top + s(10), PH - s(10), s(14)):
                    for wx in range(x + s(6), x + bw - s(8), s(12)):
                        if rnd.random() < 0.22:
                            d.rectangle((wx, wy, wx + s(5), wy + s(7)), fill=rgba(window, 220))
            x += bw + s(rnd.randint(2, 8))

    draw_on(img, lambda d: buildings(d, "#3a1840", 240, 150, None, 2, 30, 70))
    draw_on(img, lambda d: buildings(d, "#140a1c", 130, 190, "#ffbf69", 3, 40, 90))

    def crane_and_runner(d):
        dark = rgba("#0b0610")
        d.line((s(345), PH, s(345), s(150)), fill=dark, width=s(5))
        d.line((s(300), s(155), s(395), s(155)), fill=dark, width=s(5))
        d.line((s(385), s(155), s(385), s(215)), fill=dark, width=s(2))
        # runner leaping between rooftops
        d.ellipse((s(222), s(178), s(240), s(196)), fill=dark)
        d.line((s(229), s(198), s(214), s(236)), fill=dark, width=s(7))
        d.line((s(225), s(206), s(250), s(190)), fill=dark, width=s(5))
        d.line((s(225), s(206), s(200), s(214)), fill=dark, width=s(5))
        d.line((s(214), s(236), s(240), s(248)), fill=dark, width=s(6))
        d.line((s(214), s(236), s(196), s(250)), fill=dark, width=s(6))
        d.line((s(196), s(250), s(188), s(268)), fill=dark, width=s(6))
    draw_on(img, crane_and_runner)

    lines = [
        {"text": "SKYLINE", "font": fit("impact.ttf", "SKYLINE", s(330), s(110)),
         "colour": "#ffffff", "halo": ("#ff6a3d", s(10)), "gap": s(4)},
        {"text": "PURSUIT", "font": fit("impact.ttf", "PURSUIT", s(330), s(110)),
         "colour": "#ffb347", "halo": ("#000000", s(8))},
    ]
    finish_poster(img, lines, s(318), "One witness. Eighty floors. No way down.", "M")
    save_poster(img, 1)


def poster_lanterns():
    img = new_poster([(0, "#060d2b"), (0.55, "#17306b"), (1, "#2c4f93")])
    rnd = random.Random(7)

    def stars(d):
        for _ in range(140):
            x, y, r = rnd.randint(0, PW), rnd.randint(0, s(330)), rnd.choice([1, 1, 2, 2, 3])
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, rnd.randint(90, 230)))
    draw_on(img, stars)

    lanterns = [(rnd.randint(25, 375), rnd.randint(70, 380), rnd.choice([7, 9, 11, 14, 18, 24]))
                for _ in range(24)]
    draw_on(img, lambda d: [d.ellipse((s(x - r * 2), s(y - r * 2), s(x + r * 2), s(y + r * 2)),
                                      fill=rgba("#ff9f43", 170)) for x, y, r in lanterns], s(14))

    def bodies(d):
        for x, y, r in lanterns:
            d.rounded_rectangle((s(x - r * 0.7), s(y - r), s(x + r * 0.7), s(y + r)),
                                radius=s(r * 0.45), fill=rgba("#ffd27a"))
            d.rectangle((s(x - r * 0.4), s(y - r - 2), s(x + r * 0.4), s(y - r + 1)),
                        fill=rgba("#7a3e10"))
            d.rounded_rectangle((s(x - r * 0.35), s(y - r * 0.5), s(x + r * 0.35), s(y + r * 0.6)),
                                radius=s(r * 0.3), fill=rgba("#fff3c4"))
    draw_on(img, bodies)

    def hills(d):
        d.polygon([(0, s(455)), (s(70), s(410)), (s(140), s(440)), (s(230), s(380)),
                   (s(320), s(430)), (s(400), s(400)), (PW, PH), (0, PH)], fill=rgba("#0e1d45"))
        d.polygon([(0, s(500)), (s(90), s(470)), (s(170), s(485)), (s(260), s(455)),
                   (s(400), s(490)), (PW, PH), (0, PH)], fill=rgba("#08112b"))
        # girl holding up a lantern on the hill
        d.ellipse((s(108), s(430), s(122), s(444)), fill=rgba("#050a1c"))
        d.polygon([(s(115), s(442)), (s(102), s(474)), (s(128), s(474))], fill=rgba("#050a1c"))
        d.line((s(120), s(450), s(134), s(426)), fill=rgba("#050a1c"), width=s(3))
    draw_on(img, hills)
    glow(img, (s(124), s(404), s(148), s(428)), "#ffb347", s(8), 220)
    draw_on(img, lambda d: d.rounded_rectangle((s(131), s(410), s(141), s(424)), radius=s(3),
                                               fill=rgba("#ffe39a")))

    lines = [
        {"text": "THE LANTERN", "font": fit("georgiab.ttf", "THE LANTERN", s(300), s(46)),
         "colour": "#fff1d0", "tracking": s(4), "halo": ("#ff9f43", s(8)), "gap": s(6)},
        {"text": "KEEPERS", "font": fit("georgiab.ttf", "KEEPERS", s(340), s(84)),
         "colour": "#ffe3a3", "halo": ("#ff9f43", s(12))},
    ]
    finish_poster(img, lines, s(392), "Every light holds a dream.", "G")
    save_poster(img, 2)


def poster_plus_one():
    img = new_poster([(0, "#ff8fab"), (0.6, "#ffb3a7"), (1, "#ffd6a5")])
    rnd = random.Random(11)
    colours = ["#ffffff", "#ffd166", "#06d6a0", "#7b2cbf", "#ef476f"]

    def confetti(d):
        for _ in range(140):
            x, y = rnd.randint(0, PW), rnd.randint(0, PH)
            colour = rgba(rnd.choice(colours), rnd.randint(150, 230))
            if rnd.random() < 0.5:
                d.polygon(rotated_rect(x, y, s(rnd.randint(4, 10)), s(rnd.randint(8, 16)),
                                       rnd.randint(0, 180)), fill=colour)
            else:
                r = s(rnd.randint(2, 5))
                d.ellipse((x - r, y - r, x + r, y + r), fill=colour)
    draw_on(img, confetti)

    def rings(d):
        gold, rose = rgba("#e9b949"), rgba("#d98b8b")
        d.ellipse((s(100), s(140), s(240), s(280)), outline=gold, width=s(16))
        d.ellipse((s(170), s(140), s(310), s(280)), outline=rose, width=s(16))
        d.arc((s(100), s(140), s(240), s(280)), 25, 95, fill=gold, width=s(16))
        d.polygon([(s(170), s(118)), (s(184), s(132)), (s(170), s(150)), (s(156), s(132))],
                  fill=rgba("#ffffff"))
    draw_on(img, lambda d: d.ellipse((s(108), s(150), s(318), s(290)), fill=rgba("#7b2cbf", 60)), s(18))
    draw_on(img, rings)

    lines = [
        {"text": "PLUS ONE", "font": fit("seguibl.ttf", "PLUS ONE", s(320), s(78)),
         "colour": "#3d0c2e", "gap": s(4)},
        {"text": "PROBLEMS", "font": fit("seguibl.ttf", "PROBLEMS", s(330), s(78)),
         "colour": "#ffffff", "stroke": s(3), "stroke_colour": "#3d0c2e"},
    ]
    finish_poster(img, lines, s(335), "She needed a date. She got a disaster.", "M",
                  ink="#3d0c2e", tag_colour="#5a1846", shade=False)
    save_poster(img, 3)


def poster_harbour():
    horizon = s(330)
    img = new_poster([(0, "#1c2741"), (1, "#1c2741")])
    img.paste(gradient((PW, horizon), [(0, "#1c2741"), (0.6, "#5d6b8a"), (1, "#e0b08f")]), (0, 0))
    glow(img, (s(150), s(260), s(250), s(400)), "#ffd6a0", s(30), 230)
    draw_on(img, lambda d: d.ellipse((s(175), s(290), s(225), s(340)), fill=rgba("#ffe7c2")))
    img.paste(gradient((PW, PH - horizon), [(0, "#3b5c74"), (1, "#0b1620")]), (0, horizon))
    rnd = random.Random(5)

    def sea(d):
        for i in range(26):
            width = s(70 - i * 2.4)
            y = horizon + s(4 + i * 6)
            d.line((PW / 2 - width / 2, y, PW / 2 + width / 2, y), fill=rgba("#ffd6a0", 150 - i * 5),
                   width=s(2))
        for _ in range(70):
            x, y = rnd.randint(0, PW), rnd.randint(horizon + s(10), PH)
            length = s(rnd.randint(10, 30))
            d.line((x, y, x + length, y), fill=rgba("#9cc3d5", rnd.randint(40, 110)), width=s(1))
    draw_on(img, sea)

    def coast(d):
        dark = rgba("#0a1218")
        d.polygon([(0, s(420)), (s(40), s(405)), (s(95), s(418)), (s(130), s(445)), (s(150), PH),
                   (0, PH)], fill=dark)
        d.polygon([(s(48), s(410)), (s(84), s(410)), (s(76), s(270)), (s(56), s(270))],
                  fill=rgba("#e9e4da"))
        for y in (300, 345, 390):
            d.polygon([(s(56 - (y - 270) * 0.06), s(y)), (s(76 + (y - 270) * 0.06), s(y)),
                       (s(77 + (y + 14 - 270) * 0.06), s(y + 14)), (s(55 - (y + 14 - 270) * 0.06), s(y + 14))],
                      fill=rgba("#b23a48"))
        d.rectangle((s(54), s(252), s(78), s(270)), fill=rgba("#ffe08a"))
        d.polygon([(s(50), s(252)), (s(66), s(236)), (s(82), s(252))], fill=dark)
        # sail boat on the horizon
        d.polygon([(s(290), s(326)), (s(334), s(326)), (s(326), s(334)), (s(298), s(334))],
                  fill=rgba("#1a2233"))
        d.line((s(312), s(326), s(312), s(286)), fill=rgba("#1a2233"), width=s(2))
        d.polygon([(s(314), s(288)), (s(314), s(322)), (s(334), s(322))], fill=rgba("#1a2233"))
    draw_on(img, lambda d: d.polygon([(s(66), s(260)), (PW, s(205)), (PW, s(300))],
                                     fill=rgba("#fff3c4", 70)), s(14))
    draw_on(img, coast)

    lines = [
        {"text": "QUIET", "font": font("georgia.ttf", s(64)), "colour": "#ffffff",
         "tracking": s(16), "gap": s(10)},
        {"text": "HARBOUR", "font": fit("georgia.ttf", "HARBOUR", s(330), s(64), s(12)),
         "colour": "#ffe7c2", "tracking": s(12)},
    ]
    finish_poster(img, lines, s(64), "Some tides always bring you home.", "M")
    save_poster(img, 4)


def poster_neon_orbit():
    img = new_poster([(0, "#05010f"), (0.5, "#180a36"), (1, "#2a0e4f")])
    rnd = random.Random(3)

    def stars(d):
        for _ in range(260):
            x, y, r = rnd.randint(0, PW), rnd.randint(0, PH), rnd.choice([1, 1, 1, 2, 2, 3])
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, rnd.randint(60, 230)))
    draw_on(img, stars)

    cx, cy, radius = s(200), s(240), s(118)
    glow(img, (cx - radius - s(30), cy - radius - s(30), cx + radius + s(30), cy + radius + s(30)),
         "#4cc9f0", s(40), 110)

    ring = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(ring)
    ring_draw.ellipse((cx - radius * 1.7, cy - radius * 0.34, cx + radius * 1.7, cy + radius * 0.34),
                      outline=rgba("#4cc9f0"), width=s(7))
    ring_draw.ellipse((cx - radius * 1.5, cy - radius * 0.27, cx + radius * 1.5, cy + radius * 0.27),
                      outline=rgba("#f72585"), width=s(3))
    back = Image.new("RGBA", img.size, (0, 0, 0, 0))
    front = Image.new("RGBA", img.size, (0, 0, 0, 0))
    back.paste(ring.crop((0, 0, PW, cy)), (0, 0))
    front.paste(ring.crop((0, cy, PW, PH)), (0, cy))
    back = back.rotate(14, center=(cx, cy), resample=Image.Resampling.BICUBIC)
    front = front.rotate(14, center=(cx, cy), resample=Image.Resampling.BICUBIC)

    img.alpha_composite(back.filter(ImageFilter.GaussianBlur(s(6))))
    img.alpha_composite(back)

    def planet(d):
        for k in range(60):
            t = k / 59
            r = radius * (1 - 0.72 * t)
            px, py = cx - radius * 0.3 * t, cy - radius * 0.3 * t
            colour = mix("#1e0846", "#7b2cbf", t / 0.6) if t < 0.6 else mix("#7b2cbf", "#ff6ad5", (t - 0.6) / 0.4)
            d.ellipse((px - r, py - r, px + r, py + r), fill=colour + (255,))
    draw_on(img, planet, s(2))
    img.alpha_composite(front.filter(ImageFilter.GaussianBlur(s(6))))
    img.alpha_composite(front)

    # small ship with an engine trail
    draw_on(img, lambda d: d.line((s(40), s(408), s(96), s(392)), fill=rgba("#4cc9f0"), width=s(6)), s(5))
    draw_on(img, lambda d: d.polygon([(s(112), s(386)), (s(90), s(384)), (s(94), s(398))],
                                     fill=rgba("#e8f7ff")))

    lines = [
        {"text": "NEON", "font": fit("seguibl.ttf", "NEON", s(320), s(96), s(14)),
         "colour": "#ffffff", "tracking": s(14), "halo": ("#4cc9f0", s(12)), "gap": s(2)},
        {"text": "ORBIT", "font": fit("seguibl.ttf", "ORBIT", s(320), s(96), s(14)),
         "colour": "#ffffff", "tracking": s(14), "halo": ("#f72585", s(12))},
    ]
    finish_poster(img, lines, s(318), "The station is falling. The stars are calling.", "M")
    save_poster(img, 5)


def poster_hollow_lane():
    img = new_poster([(0, "#020504"), (0.6, "#0b1a17"), (1, "#1a332d")])
    glow(img, (s(220), s(40), s(380), s(200)), "#e8f0d8", s(40), 150)

    def moon(d):
        d.ellipse((s(255), s(75), s(345), s(165)), fill=rgba("#e9edd8"))
        for x, y, r in ((285, 105, 9), (318, 132, 12), (300, 145, 6)):
            d.ellipse((s(x - r), s(y - r), s(x + r), s(y + r)), fill=rgba("#cfd5bd"))
    draw_on(img, moon)

    rnd = random.Random(13)
    draw_on(img, lambda d: (branch(d, s(30), PH, 82, s(170), s(16), 8, rnd, rgba("#010302")),
                            branch(d, s(372), PH, 98, s(160), s(15), 8, rnd, rgba("#010302"))))

    def house(d):
        black = rgba("#030605")
        d.rectangle((s(125), s(300), s(275), s(420)), fill=black)
        d.polygon([(s(110), s(302)), (s(200), s(222)), (s(290), s(302))], fill=black)
        d.rectangle((s(238), s(236), s(256), s(280)), fill=black)
        d.rectangle((s(190), s(370), s(212), s(420)), fill=rgba("#0d1714"))
        d.rectangle((s(228), s(325), s(252), s(352)), fill=rgba("#0d1714"))
        for x in range(0, 400, 12):
            d.rectangle((s(x), s(425), s(x + 3), s(450)), fill=black)
        d.rectangle((0, s(432), PW, s(436)), fill=black)
    draw_on(img, house)
    glow(img, (s(140), s(315), s(190), s(370)), "#ffcf6e", s(12), 200)
    draw_on(img, lambda d: d.rectangle((s(152), s(326), s(176), s(356)), fill=rgba("#ffcf6e")))
    draw_on(img, lambda d: [d.ellipse((s(x - 120), s(y - 18), s(x + 120), s(y + 18)),
                                      fill=(220, 235, 225, 46))
                            for x, y in ((80, 440), (250, 452), (380, 436), (160, 470))], s(14))

    lines = [
        {"text": "MIDNIGHT AT", "font": font("timesbd.ttf", s(30)), "colour": "#c9d1c1",
         "tracking": s(8), "gap": s(10)},
        {"text": "HOLLOW LANE", "font": fit("timesbd.ttf", "HOLLOW LANE", s(340), s(70), s(4)),
         "colour": "#f1ead7", "tracking": s(4), "halo": ("#8b0000", s(10))},
    ]
    finish_poster(img, lines, s(404), "Every door leads somewhere. Some lead back.", "MA15+")
    save_poster(img, 6)


def poster_grandpa():
    img = new_poster([(0, "#ffd23f"), (1, "#ffb627")])
    cx, cy = s(200), s(235)

    def rays(d):
        for i in range(24):
            if i % 2:
                continue
            a0, a1 = 2 * math.pi * i / 24, 2 * math.pi * (i + 1) / 24
            d.polygon([(cx, cy), (cx + s(700) * math.cos(a0), cy + s(700) * math.sin(a0)),
                       (cx + s(700) * math.cos(a1), cy + s(700) * math.sin(a1))],
                      fill=rgba("#ffffff", 55))
    draw_on(img, rays)

    def phone(d):
        navy = rgba("#1b1f4b")
        d.rounded_rectangle((s(115), s(85), s(285), s(385)), radius=s(24), fill=navy)
        d.rounded_rectangle((s(127), s(108), s(273), s(362)), radius=s(10), fill=rgba("#8ee0f0"))
        # grandpa on the screen
        d.polygon([(s(140), s(362)), (s(150), s(300)), (s(250), s(300)), (s(260), s(362))],
                  fill=rgba("#ef476f"))
        d.polygon([(s(186), s(300)), (s(200), s(320)), (s(214), s(300))], fill=rgba("#ffffff"))
        d.ellipse((s(140), s(214), s(160), s(236)), fill=rgba("#f2c094"))
        d.ellipse((s(240), s(214), s(260), s(236)), fill=rgba("#f2c094"))
        d.ellipse((s(148), s(160), s(252), s(290)), fill=rgba("#f2c094"))
        d.ellipse((s(140), s(178), s(166), s(214)), fill=rgba("#ffffff"))
        d.ellipse((s(234), s(178), s(260), s(214)), fill=rgba("#ffffff"))
        d.ellipse((s(180), s(170), s(206), s(184)), fill=rgba("#fbd9b6"))
        d.ellipse((s(164), s(208), s(196), s(238)), outline=navy, width=s(4))
        d.ellipse((s(204), s(208), s(236), s(238)), outline=navy, width=s(4))
        d.line((s(196), s(220), s(204), s(220)), fill=navy, width=s(3))
        d.ellipse((s(176), s(219), s(184), s(227)), fill=navy)
        d.ellipse((s(216), s(219), s(224), s(227)), fill=navy)
        d.ellipse((s(170), s(246), s(230), s(266)), fill=rgba("#ffffff"))
        d.arc((s(184), s(256), s(216), s(280)), 20, 160, fill=navy, width=s(3))
        # LIVE badge
        d.rounded_rectangle((s(136), s(118), s(180), s(136)), radius=s(4), fill=rgba("#e63e6d"))
        live = font("arialbd.ttf", s(11))
        d.text((s(145), s(120)), "LIVE", font=live, fill=rgba("#ffffff"))

    draw_on(img, lambda d: d.rounded_rectangle((s(121), s(93), s(291), s(393)), radius=s(24),
                                               fill=rgba("#7a4b00", 90)), s(8))
    draw_on(img, phone)

    def reactions(d):
        label_font = font("seguibl.ttf", s(14))
        for x, y, text in ((300, 130, "2.4M"), (52, 200, "980K"), (296, 300, "15M")):
            d.rounded_rectangle((s(x), s(y), s(x + 82), s(y + 30)), radius=s(15), fill=rgba("#ffffff"))
            d.polygon(heart_points(s(x + 18), s(y + 16), s(8)), fill=rgba("#e63e6d"))
            d.text((s(x + 32), s(y + 4)), text, font=label_font, fill=rgba("#1b1f4b"))
        for x, y, size in ((340, 95, 10), (40, 270, 12), (330, 360, 9), (70, 140, 8)):
            d.polygon(heart_points(s(x), s(y), s(size), 15), fill=rgba("#e63e6d"))
    draw_on(img, reactions)

    lines = [
        {"text": "GRANDPA", "font": fit("seguibl.ttf", "GRANDPA", s(330), s(80)),
         "colour": "#1b1f4b", "gap": s(4)},
        {"text": "GOES VIRAL", "font": fit("seguibl.ttf", "GOES VIRAL", s(330), s(60)),
         "colour": "#e63e6d", "stroke": s(2), "stroke_colour": "#ffffff"},
    ]
    finish_poster(img, lines, s(390), "He just wanted to video-call the grandkids.", "PG",
                  ink="#1b1f4b", tag_colour="#3a2e00", shade=False)
    save_poster(img, 7)


def poster_paper_hearts():
    img = new_poster([(0, "#fbe3ec"), (0.5, "#e7dcff"), (1, "#c6d8ff")])
    glow(img, (s(80), s(180), s(320), s(420)), "#ffffff", s(50), 200)

    tower = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(tower)
    ink = rgba("#3b3470")
    d.line((s(200), s(196), s(200), s(222)), fill=ink, width=s(3))
    d.polygon([(s(195), s(220)), (s(205), s(220)), (s(214), s(330)), (s(186), s(330))], fill=ink)
    d.rectangle((s(178), s(330), s(222), s(339)), fill=ink)
    d.polygon([(s(184), s(339)), (s(216), s(339)), (s(234), s(420)), (s(166), s(420))], fill=ink)
    d.rectangle((s(156), s(420), s(244), s(431)), fill=ink)
    d.polygon([(s(162), s(431)), (s(238), s(431)), (s(280), s(520)), (s(120), s(520))], fill=ink)
    d.ellipse((s(160), s(470), s(240), s(570)), fill=(0, 0, 0, 0))
    for y0, y1, x0, x1 in ((345, 415, 188, 212), (230, 325, 196, 204)):
        d.line((s(x0), s(y0), s(x1), s(y1)), fill=rgba("#6c63b5"), width=s(1))
        d.line((s(x1), s(y0), s(x0), s(y1)), fill=rgba("#6c63b5"), width=s(1))
    d.rectangle((0, s(518), PW, s(522)), fill=rgba("#3b3470", 120))
    img.alpha_composite(tower)

    rnd = random.Random(21)
    hearts = [(rnd.randint(30, 370), rnd.randint(200, 500), rnd.randint(10, 24), rnd.randint(-30, 30),
               rnd.choice(["#e63e6d", "#ff8fab", "#ffffff", "#f15bb5"])) for _ in range(15)]
    draw_on(img, lambda dr: [dr.polygon(heart_points(s(x + 3), s(y + 4), s(size), angle),
                                        fill=(40, 20, 60, 70)) for x, y, size, angle, _ in hearts], s(3))

    def paper_hearts(dr):
        for x, y, size, angle, colour in hearts:
            dr.polygon(heart_points(s(x), s(y), s(size), angle), fill=rgba(colour))
            a = math.radians(angle)
            top = (s(x) + math.sin(-a) * s(size) * -0.2, s(y) - math.cos(a) * s(size) * 0.25)
            tip = (s(x) - math.sin(a) * s(size) * 1.0, s(y) + math.cos(a) * s(size) * 1.0)
            dr.line((top, tip), fill=(0, 0, 0, 40), width=s(1))
    draw_on(img, paper_hearts)

    lines = [
        {"text": "Paper Hearts", "font": fit("georgiaz.ttf", "Paper Hearts", s(340), s(62)),
         "colour": "#2a2350", "gap": s(6)},
        {"text": "in Paris", "font": font("georgiai.ttf", s(40)), "colour": "#e63e6d"},
    ]
    finish_poster(img, lines, s(60), "Follow your heart. Literally.", "PG",
                  ink="#2a2350", tag_colour="#2a2350", shade=False)
    save_poster(img, 8)


def poster_robo_pup():
    img = new_poster([(0, "#0b8a7f"), (0.55, "#1fbf8f"), (1, "#7ed957")])
    draw_on(img, lambda d: (gear(d, s(60), s(110), s(70), 10, (255, 255, 255, 45)),
                            gear(d, s(350), s(260), s(90), 12, (255, 255, 255, 40)),
                            gear(d, s(330), s(70), s(40), 8, (255, 255, 255, 50))))
    draw_on(img, lambda d: [d.line((s(20), s(y), s(20 + length), s(y)), fill=(255, 255, 255, 120),
                                   width=s(3)) for y, length in ((250, 70), (280, 95), (310, 60), (338, 80))])

    def dog(d):
        outline, metal = rgba("#24384a"), rgba("#e3ebf2")
        d.line((s(132), s(285), s(98), s(240)), fill=outline, width=s(7))
        d.ellipse((s(88), s(228), s(110), s(250)), fill=rgba("#ff5d73"), outline=outline, width=s(3))
        for x in (142, 176, 236, 268):
            d.rounded_rectangle((s(x), s(325), s(x + 22), s(378)), radius=s(8), fill=metal,
                                outline=outline, width=s(4))
            d.ellipse((s(x - 4), s(368), s(x + 26), s(384)), fill=outline)
        d.rounded_rectangle((s(128), s(268), s(296), s(342)), radius=s(30), fill=metal,
                            outline=outline, width=s(5))
        d.rounded_rectangle((s(170), s(287), s(244), s(323)), radius=s(10), fill=rgba("#9fb3c8"))
        for i, colour in enumerate(("#ff5d73", "#ffd23f", "#4cc9f0")):
            d.ellipse((s(182 + i * 18), s(298), s(194 + i * 18), s(310)), fill=rgba(colour))
        d.polygon([(s(250), s(205)), (s(262), s(150)), (s(286), s(198))], fill=outline)
        d.polygon([(s(294), s(198)), (s(316), s(150)), (s(326), s(206))], fill=outline)
        d.line((s(288), s(190), s(288), s(160)), fill=outline, width=s(4))
        d.ellipse((s(279), s(146), s(297), s(164)), fill=rgba("#ffd23f"), outline=outline, width=s(3))
        d.rounded_rectangle((s(240), s(188), s(334), s(272)), radius=s(26), fill=metal,
                            outline=outline, width=s(5))
        d.rounded_rectangle((s(254), s(208), s(320), s(240)), radius=s(14), fill=rgba("#123047"))
        d.rounded_rectangle((s(300), s(240), s(352), s(266)), radius=s(10), fill=rgba("#cfd9e3"),
                            outline=outline, width=s(4))
        d.ellipse((s(338), s(244), s(354), s(258)), fill=outline)
        d.rectangle((s(246), s(262), s(300), s(276)), fill=rgba("#ff5d73"))
        d.ellipse((s(266), s(270), s(282), s(286)), fill=rgba("#ffd23f"), outline=outline, width=s(2))

    draw_on(img, lambda d: d.ellipse((s(110), s(372), s(320), s(396)), fill=(0, 40, 30, 90)), s(6))
    draw_on(img, dog)
    glow(img, (s(262), s(212), s(312), s(238)), "#4cf0e8", s(6), 220)
    draw_on(img, lambda d: (d.ellipse((s(268), s(217), s(284), s(233)), fill=rgba("#c9fffb")),
                            d.ellipse((s(292), s(217), s(308), s(233)), fill=rgba("#c9fffb"))))

    lines = [
        {"text": "ROBO PUP", "font": fit("seguibl.ttf", "ROBO PUP", s(330), s(80)),
         "colour": "#ffffff", "stroke": s(4), "stroke_colour": "#0b3d3a", "gap": s(4)},
        {"text": "RESCUE", "font": fit("seguibl.ttf", "RESCUE", s(300), s(64)),
         "colour": "#ffd23f", "stroke": s(4), "stroke_colour": "#0b3d3a"},
    ]
    finish_poster(img, lines, s(390), "Big heart. Bigger batteries.", "PG")
    save_poster(img, 9)


# ---------------------------------------------------------------------------
# Home page hero illustration (1200 x 800)
# ---------------------------------------------------------------------------
def hero():
    w, h = 1200 * SCALE, 800 * SCALE
    img = gradient((w, h), [(0, "#07081a"), (0.5, "#151036"), (1, "#241445")])

    # screen glow and light spilling onto the audience
    glow(img, (s(180), s(30), s(1020), s(520)), "#ff7a6b", s(70), 120)
    draw_on(img, lambda d: d.polygon([(s(250), s(450)), (s(950), s(450)), (s(1200), s(800)), (0, s(800))],
                                     fill=rgba("#ff9a8b", 34)), s(30))

    # movie playing on the screen
    sx0, sy0, sx1, sy1 = s(250), s(80), s(950), s(450)
    scene = gradient((sx1 - sx0, sy1 - sy0), [(0, "#ffb26b"), (0.55, "#ff5e78"), (1, "#7b2d8e")])
    sd = ImageDraw.Draw(scene)
    sw, sh = scene.size
    sd.ellipse((sw / 2 - s(70), sh * 0.55 - s(70), sw / 2 + s(70), sh * 0.55 + s(70)), fill=rgba("#ffe29a"))
    sd.polygon([(0, sh * 0.7), (sw * 0.2, sh * 0.5), (sw * 0.4, sh * 0.68), (sw * 0.62, sh * 0.45),
                (sw * 0.8, sh * 0.62), (sw, sh * 0.5), (sw, sh), (0, sh)], fill=rgba("#4a1c6b"))
    sd.polygon([(0, sh * 0.85), (sw * 0.3, sh * 0.7), (sw * 0.55, sh * 0.82), (sw * 0.78, sh * 0.72),
                (sw, sh * 0.8), (sw, sh), (0, sh)], fill=rgba("#2a0f45"))
    for bx, by in ((0.3, 0.25), (0.34, 0.22), (0.7, 0.3)):
        sd.line((sw * bx - s(12), sh * by - s(6), sw * bx, sh * by), fill=rgba("#3a1250"), width=s(3))
        sd.line((sw * bx, sh * by, sw * bx + s(12), sh * by - s(6)), fill=rgba("#3a1250"), width=s(3))
    mask = Image.new("L", scene.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw, sh), radius=s(8), fill=255)
    draw_on(img, lambda d: d.rounded_rectangle((sx0 - s(10), sy0 - s(10), sx1 + s(10), sy1 + s(10)),
                                               radius=s(12), fill=rgba("#05050c")))
    img.paste(scene, (sx0, sy0), mask)

    # red curtains and valance
    def curtains(d):
        for side in (0, 1):
            for i in range(9):
                x = i * s(20) if side == 0 else w - (i + 1) * s(20)
                colour = "#7a1427" if i % 2 == 0 else "#5a0f1f"
                d.rectangle((x, 0, x + s(20), h), fill=rgba(colour))
        d.rectangle((0, 0, w, s(46)), fill=rgba("#5a0f1f"))
        for i in range(0, 1200, 60):
            d.ellipse((s(i), s(26), s(i + 60), s(66)), fill=rgba("#5a0f1f"))
    draw_on(img, curtains)
    draw_on(img, lambda d: (d.rectangle((s(150), 0, s(200), h), fill=rgba("#000000", 120)),
                            d.rectangle((w - s(200), 0, w - s(150), h), fill=rgba("#000000", 120))), s(20))

    # rows of seats with audience silhouettes (back row first)
    rnd = random.Random(42)
    rows = [(520, 64, 50, 10), (600, 82, 62, 12), (690, 104, 76, 14), (790, 132, 92, 16)]
    popcorn_seats = {(1, 3), (3, 2)}
    for row_index, (y, seat_w, seat_h, gap) in enumerate(rows):
        step = seat_w + gap
        offset = (w - s(step) * (w // s(step))) / 2 - (s(step) / 2 if row_index % 2 else 0)
        count = int(w // s(step)) + 2
        for i in range(count):
            x = offset + i * s(step)
            head_r = s(seat_w * 0.27)
            hx, hy = x + s(seat_w) / 2, s(y) - head_r * 0.45
            seated = rnd.random() < 0.62

            def seat(d, x=x, hx=hx, hy=hy, seated=seated, head_r=head_r):
                if seated:
                    d.ellipse((hx - head_r, hy - head_r, hx + head_r, hy + head_r), fill=rgba("#07060f"))
                    d.arc((hx - head_r, hy - head_r, hx + head_r, hy + head_r), 200, 340,
                          fill=rgba("#ff9a8b", 150), width=s(2))
                d.rounded_rectangle((x, s(y), x + s(seat_w), s(y + seat_h)), radius=s(seat_w * 0.22),
                                    fill=rgba("#2b1238"))
                d.arc((x, s(y), x + s(seat_w), s(y + seat_h)), 200, 340, fill=rgba("#6b3380"), width=s(2))
            draw_on(img, seat)

            if (row_index, i) in popcorn_seats and seated:
                px, py = hx + head_r * 1.1, hy - head_r * 0.2

                def popcorn(d, px=px, py=py, size=head_r):
                    for k in range(5):
                        d.ellipse((px - size * 0.5 + k * size * 0.25, py - size * 0.45, px - size * 0.15 + k * size * 0.25,
                                   py - size * 0.1), fill=rgba("#fff1b8"))
                    d.polygon([(px - size * 0.55, py - size * 0.2), (px + size * 0.55, py - size * 0.2),
                               (px + size * 0.4, py + size * 0.9), (px - size * 0.4, py + size * 0.9)],
                              fill=rgba("#e63946"))
                    d.line((px, py - size * 0.2, px, py + size * 0.9), fill=rgba("#ffffff"), width=s(5))
                draw_on(img, popcorn)

    path = os.path.join(OUT_DIR, "hero.jpg")
    img.convert("RGB").resize((1200, 800), Image.Resampling.LANCZOS).save(
        path, quality=84, optimize=True, progressive=True)
    print("saved", path)


# ---------------------------------------------------------------------------
# Logo + favicon
# ---------------------------------------------------------------------------
def draw_icon(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgba("#ffb627"))
    d.ellipse((cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82), fill=rgba("#0d0f1e"))
    d.polygon([(cx - r * 0.28, cy - r * 0.42), (cx - r * 0.28, cy + r * 0.42), (cx + r * 0.46, cy)],
              fill=rgba("#ffb627"))
    sx, sy, k = cx + r * 0.74, cy - r * 0.74, r * 0.34
    d.polygon([(sx, sy - k), (sx + k * 0.28, sy - k * 0.28), (sx + k, sy), (sx + k * 0.28, sy + k * 0.28),
               (sx, sy + k), (sx - k * 0.28, sy + k * 0.28), (sx - k, sy), (sx - k * 0.28, sy - k * 0.28)],
              fill=rgba("#ff6b81"))


def logo():
    k = 4                                  # draw at 4x for crisp edges
    img = Image.new("RGBA", (360 * k, 96 * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_icon(d, 48 * k, 50 * k, 34 * k)
    word_font = font("seguibl.ttf", 50 * k)
    cine_w = word_font.getlength("Cine")
    bbox = word_font.getbbox("CineSpark")
    y = 48 * k - (bbox[1] + bbox[3]) / 2
    d.text((100 * k, y), "Cine", font=word_font, fill=rgba("#f2f3fa"))
    d.text((100 * k + cine_w, y), "Spark", font=word_font, fill=rgba("#ffb627"))
    img.resize((360, 96), Image.Resampling.LANCZOS).save(os.path.join(OUT_DIR, "logo.png"), optimize=True)

    icon = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw_icon(ImageDraw.Draw(icon), 120, 136, 100)
    icon.resize((64, 64), Image.Resampling.LANCZOS).save(os.path.join(OUT_DIR, "favicon.png"), optimize=True)
    print("saved logo.png and favicon.png")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    logo()
    hero()
    poster_skyline()
    poster_lanterns()
    poster_plus_one()
    poster_harbour()
    poster_neon_orbit()
    poster_hollow_lane()
    poster_grandpa()
    poster_paper_hearts()
    poster_robo_pup()
