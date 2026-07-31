import pygame
import math
import random
import sys




pygame.init()




WIDTH, HEIGHT = 800, 500
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman")




LETTER_FONT = pygame.font.SysFont('Courier', 40)
WORD_FONT   = pygame.font.SysFont('cosmicsan', 60)
HINT_FONT   = pygame.font.SysFont('Courier', 25)
FLASH_FONT  = pygame.font.SysFont('Courier', 70, bold=True)
SYS_FONT    = pygame.font.SysFont('Courier', 14, bold=True)
STATUS_FONT = pygame.font.SysFont('Courier', 16, bold=True)
font_big    = pygame.font.SysFont("georgia", 44, bold=True)
font_med    = pygame.font.SysFont("georgia", 26, bold=True)
font_symbol = pygame.font.SysFont("georgia", 54, bold=True)
DARK        = (8,   45,  85)
TEXT_CLR    = (245, 238, 215)
H_RED       = (255, 85,  85)
H_GREEN     = (65,  235, 135)
GREY        = (70,  115, 155)
GALLOWS_CLR = (255, 195, 65)
SKIN_CLR    = (255, 215, 170)
BODY_CLR    = (255, 145, 55)




BLACK       = (20,  20,  20)
BG_COLOR    = (240, 230, 210)
REEL_BG     = (255, 248, 235)
REEL_BORDER = (160, 120, 60)
GOLD        = (212, 160, 30)
DARK_GOLD   = (140, 100, 10)
ORANGE      = (230, 120, 30)
S_GRAY      = (180, 180, 180)
S_DARK_GRAY = (100, 100, 100)
SHADOW      = (100, 80,  40)
WHITE       = (255, 255, 255)




SYMBOLS = ["★", "A", "B", "C", "D", "E"]
SYMBOL_COLORS = {
    "★": (220, 180, 0),
    "A":  (180, 60,  60),
    "B":  (60,  140, 80),
    "C":  (70,  110, 200),
    "D":  (190, 100, 30),
    "E":  (140, 60,  180),
}




def weighted_symbol():
    if random.random() < 0.693:
        return "★"
    return random.choice(["A", "B", "C", "D", "E"])




S_REEL_W    = 118
S_REEL_H    = 118
S_REEL_GAP  = 18
S_REEL_TOP  = 150
S_REEL_START = (WIDTH - (3 * S_REEL_W + 2 * S_REEL_GAP)) // 2
SPIN_DURATION = [1.0, 1.3, 1.6]
SPIN_SPEED    = 900
WIN_SEQ_DUR   = 3.5
RETURN_DELAY  = 4.0




class Reel:
    def __init__(self, index):
        self.index   = index
        self.symbol  = random.choice(SYMBOLS)
        self.spinning = False
        self.speed   = 0.0
        self.elapsed = 0.0
        self.duration = SPIN_DURATION[index]
        self.strip   = [random.choice(SYMBOLS) for _ in range(12)]
        self.strip_y = 0.0
        self.final   = None




    def reset(self):
        self.symbol   = random.choice(SYMBOLS)
        self.spinning = False
        self.speed    = 0.0
        self.elapsed  = 0.0
        self.strip    = [random.choice(SYMBOLS) for _ in range(12)]
        self.strip_y  = 0.0
        self.final    = None




    def start(self, result_symbol):
        self.spinning = True
        self.elapsed  = 0.0
        self.speed    = SPIN_SPEED
        self.strip_y  = 0.0
        self.final    = result_symbol
        self.strip    = [random.choice(SYMBOLS) for _ in range(20)]
        self.strip.append(result_symbol)




    def update(self, dt):
        if not self.spinning:
            return
        self.elapsed += dt
        progress = self.elapsed / self.duration
        if progress >= 1.0:
            self.spinning = False
            self.symbol   = self.final
            self.strip_y  = 0.0
            self.speed    = 0.0
        else:
            ease = 1.0 - max(0.0, (progress - 0.6) / 0.4) ** 2
            self.speed    = SPIN_SPEED * ease
            self.strip_y += self.speed * dt
            self.strip_y  = self.strip_y % (len(self.strip) * S_REEL_H)




    def draw(self, x, y, flash=0.0):
        rect = pygame.Rect(x, y, S_REEL_W, S_REEL_H)
        pygame.draw.rect(win, SHADOW,      rect.move(4, 4), border_radius=14)
        pygame.draw.rect(win, REEL_BG,     rect,            border_radius=14)
        pygame.draw.rect(win, REEL_BORDER, rect, 4,         border_radius=14)
        if self.spinning:
            win.set_clip(pygame.Rect(x, y, S_REEL_W, S_REEL_H))
            scroll = int(self.strip_y) % (len(self.strip) * S_REEL_H)
            for i, sym in enumerate(self.strip):
                sy = y - scroll + i * S_REEL_H
                if y - S_REEL_H < sy < y + S_REEL_H * 2:
                    color = SYMBOL_COLORS.get(sym, BLACK)
                    txt = font_symbol.render(sym, True, color)
                    win.blit(txt, txt.get_rect(center=(x + S_REEL_W // 2, sy + S_REEL_H // 2)))
            win.set_clip(None)
        else:
            color = SYMBOL_COLORS.get(self.symbol, BLACK)
            txt = font_symbol.render(self.symbol, True, color)
            win.blit(txt, txt.get_rect(center=(x + S_REEL_W // 2, y + S_REEL_H // 2)))
        bw = max(3, int(6 * flash)) if flash > 0 else 4
        bc = (255, 220, 0) if flash > 0 else REEL_BORDER
        pygame.draw.rect(win, bc, rect, bw, border_radius=14)




def draw_slot_body():
    body = pygame.Rect(25, 15, WIDTH - 50, HEIGHT - 30)
    pygame.draw.rect(win, SHADOW,          body.move(6, 6), border_radius=28)
    pygame.draw.rect(win, (200, 170, 110), body,            border_radius=28)
    pygame.draw.rect(win, REEL_BORDER,     body, 5,         border_radius=28)
    pygame.draw.rect(win, BG_COLOR,        body.inflate(-20, -20), border_radius=20)




def draw_slot_button(rect, text, base_col, hover_col, text_col, hovered):
    col = hover_col if hovered else base_col
    pygame.draw.rect(win, SHADOW, rect.move(3, 3), border_radius=12)
    pygame.draw.rect(win, col,    rect,            border_radius=12)
    pygame.draw.rect(win, text_col, rect, 2,       border_radius=12)
    label = font_med.render(text, True, text_col)
    win.blit(label, label.get_rect(center=rect.center))




def draw_slot_win_sequence(win_timer):
    progress = win_timer / WIN_SEQ_DUR
    t        = 1.0 - progress
    for i in range(12):
        angle = (2 * math.pi / 12) * i + t * 4
        dist  = 115 + math.sin(t * math.pi * 3 + i) * 22
        cx    = WIDTH  // 2 + int(math.cos(angle) * dist)
        cy    = 255    + int(math.sin(angle) * dist * 0.5)
        size  = max(2, int(8 * (1.0 - t * 0.5)))
        surf  = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 220, 0, int(255 * progress)), (size, size), size)
        win.blit(surf, (cx - size, cy - size))




    banner_alpha = min(255, int(255 * min(1.0, progress * 3)))
    scale        = 0.8 + 0.2 * min(1.0, (1.0 - progress) * 5)
    shadow_surf = font_big.render("★ JACKPOT! ★", True, SHADOW)
    w = max(1, int(shadow_surf.get_width()  * scale))
    h = max(1, int(shadow_surf.get_height() * scale))
    ss = pygame.transform.smoothscale(shadow_surf, (w, h))
    tmp_s = pygame.Surface((w, h), pygame.SRCALPHA)
    tmp_s.blit(ss, (0, 0))
    tmp_s.set_alpha(banner_alpha)
    win.blit(tmp_s, (WIDTH // 2 - w // 2 + 3, 25))
    gold_surf = font_big.render("★ JACKPOT! ★", True, (255, 220, 0))
    w = max(1, int(gold_surf.get_width()  * scale))
    h = max(1, int(gold_surf.get_height() * scale))
    gs = pygame.transform.smoothscale(gold_surf, (w, h))
    tmp_g = pygame.Surface((w, h), pygame.SRCALPHA)
    tmp_g.blit(gs, (0, 0))
    tmp_g.set_alpha(banner_alpha)
    win.blit(tmp_g, (WIDTH // 2 - w // 2, 22))




    hint_alpha = min(255, int(255 * min(1.0, progress * 2)))
    for txt_str, col, off in [
        ("you got a free hint", SHADOW,    (2, 2)),
        ("you got a free hint", DARK_GOLD, (0, 0)),
    ]:
        s   = font_med.render(txt_str, True, col)
        r   = s.get_rect(centerx=WIDTH // 2, top=415)
        tmp = pygame.Surface((s.get_width(), s.get_height()), pygame.SRCALPHA)
        tmp.blit(s, (0, 0))
        tmp.set_alpha(hint_alpha)
        win.blit(tmp, r.move(*off))




WORD_CENTER_X = 490
WORD_Y        = 230
WORD_MAX_W    = 480
RADIUS        = 22
GAP           = 15




_word_font_cache = {}




def get_word_font(size):
    if size not in _word_font_cache:
        _word_font_cache[size] = pygame.font.SysFont('cosmicsan', size)
    return _word_font_cache[size]




def best_word_font(display_str):
    for size in [60, 48, 38, 30, 24]:
        f = get_word_font(size)
        if f.size(display_str)[0] <= WORD_MAX_W:
            return f
    return get_word_font(24)




words = [
    "HYDROGEN","HELIUM","LITHIUM","BERYLLIUM","BORON","CARBON","NITROGEN","OXYGEN","FLUORINE","NEON",
    "SODIUM","MAGNESIUM","ALUMINUM","SILICON","PHOSPHORUS","SULFUR","CHLORINE","ARGON","POTASSIUM","CALCIUM",
    "SCANDIUM","TITANIUM","VANADIUM","CHROMIUM","MANGANESE","IRON","COBALT","NICKEL","COPPER","ZINC",
    "GALLIUM","GERMANIUM","ARSENIC","SELENIUM","BROMINE","KRYPTON","RUBIDIUM","STRONTIUM","YTTRIUM","ZIRCONIUM",
    "NIOBIUM","MOLYBDENUM","TECHNETIUM","RUTHENIUM","RHODIUM","PALLADIUM","SILVER","CADMIUM","INDIUM","TIN",
    "ANTIMONY","TELLURIUM","IODINE","XENON","CESIUM","BARIUM","LANTHANUM","CERIUM","PRASEODYMIUM","NEODYMIUM",
    "PROMETHIUM","SAMARIUM","EUROPIUM","GADOLINIUM","TERBIUM","DYSPROSIUM","HOLMIUM","ERBIUM","THULIUM","YTTERBIUM",
    "LUTETIUM","HAFNIUM","TANTALUM","TUNGSTEN","RHENIUM","OSMIUM","IRIDIUM","PLATINUM","GOLD","MERCURY",
    "THALLIUM","LEAD","BISMUTH","POLONIUM","ASTATINE","RADON","FRANCIUM","RADIUM","ACTINIUM","THORIUM",
    "PROTACTINIUM","URANIUM","NEPTUNIUM","PLUTONIUM","AMERICIUM","CURIUM","BERKELIUM","CALIFORNIUM","EINSTEINIUM","FERMIUM",
    "MENDELEVIUM","NOBELIUM","LAWRENCIUM","RUTHERFORDIUM","DUBNIUM","SEABORGIUM","BOHRIUM","HASSIUM","MEITNERIUM","DARMSTADTIUM",
    "ROENTGENIUM","COPERNICIUM","NIHONIUM","FLEROVIUM","MOSCOVIUM","LIVERMORIUM","TENNESSINE","OGANESSON",
]




FPS   = 60
clock = pygame.time.Clock()




random.seed(42)
STARS = [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
          random.uniform(0.3, 1.1), random.randint(120, 220))
         for _ in range(110)]
random.seed()




BG_GRADIENT = pygame.Surface((WIDTH, HEIGHT))
for _y in range(HEIGHT):
    _t = _y / HEIGHT
    pygame.draw.line(BG_GRADIENT,
                     (int(10 + _t*22), int(60 + _t*40), int(140 - _t*30)),
                     (0, _y), (WIDTH, _y))




def draw_background():
    win.blit(BG_GRADIENT, (0, 0))
    for sx, sy, sr, sbr in STARS:
        bright = min(255, sbr + 40)
        pygame.draw.circle(win, (bright, min(255, bright + 30), 255),
                           (sx, sy), max(1, int(sr)))




def create_letters():
    letters = []
    startx  = round((WIDTH - (RADIUS * 2 + GAP) * 13) / 2)
    starty  = 400
    for i in range(26):
        x = startx + GAP * 2 + ((RADIUS * 2 + GAP) * (i % 13))
        y = starty + ((i // 13) * (GAP + RADIUS * 2))
        letters.append([x, y, chr(65 + i), True])
    return letters




particles   = []
mouse_trail = []




CONFETTI_COLORS = [
    (255, 75,  75), (255, 185, 55), (55, 220, 120),
    (40, 215, 255), (220, 80, 255), (0, 230, 230),
    (255, 255, 80), (255, 130, 190),
]




def spawn_confetti(cx, cy, count=90):
    now = pygame.time.get_ticks()
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3.0, 11.0)
        color = random.choice(CONFETTI_COLORS)
        particles.append({
            'type': 'confetti',
            'x': cx + random.uniform(-10, 10), 'y': cy + random.uniform(-10, 10),
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed - random.uniform(2, 5),
            'w': random.randint(6, 14), 'h': random.randint(3, 7),
            'rot': random.uniform(0, 360), 'rot_speed': random.uniform(-8, 8),
            'r': color[0], 'g': color[1], 'b': color[2],
            'born': now, 'life': random.uniform(1.0, 2.0),
        })




def spawn_smoke(x, y):
    now = pygame.time.get_ticks()
    for _ in range(22):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.2, 5.0)
        base  = random.randint(60, 130)
        particles.append({
            'type': 'smoke',
            'x': x + random.uniform(-8, 8), 'y': y + random.uniform(-8, 8),
            'vx': math.cos(angle) * speed, 'vy': math.sin(angle) * speed - 2.0,
            'radius': random.randint(10, 22),
            'r': base, 'g': base, 'b': base + 30,
            'born': now, 'life': random.uniform(0.6, 1.1),
        })




def spawn_flame(mx, my):
    now   = pygame.time.get_ticks()
    speed = random.uniform(0.4, 1.4)
    angle = random.uniform(-math.pi * 0.65, -math.pi * 0.35)
    r_off = random.uniform(-4, 4)
    frac  = random.random()
    if frac < 0.55:
        r, g, b = 255, random.randint(90, 145), 0
    elif frac < 0.82:
        r, g, b = 255, random.randint(145, 195), 10
    else:
        r, g, b = 255, random.randint(55, 88), 0
    mouse_trail.append({
        'x': mx + r_off, 'y': my + random.uniform(-3, 3),
        'vx': math.cos(angle) * speed * random.uniform(0.2, 0.8),
        'vy': math.sin(angle) * speed,
        'radius': random.uniform(2, 5),
        'r': r, 'g': g, 'b': b,
        'born': now, 'life': random.uniform(0.12, 0.28),
    })




def update_draw_flame_trail():
    now   = pygame.time.get_ticks()
    alive = []
    for p in mouse_trail:
        age  = (now - p['born']) / 1000.0
        if age >= p['life']:
            continue
        frac  = age / p['life']
        alpha = int(160 * (1 - frac) ** 1.4)
        rad   = max(1, int(p['radius'] * (1 - frac * 0.6)))
        surf  = pygame.Surface((rad*2+2, rad*2+2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (p['r'], p['g'], p['b'], alpha), (rad+1, rad+1), rad)
        win.blit(surf, (int(p['x'])-rad-1, int(p['y'])-rad-1))
        p['x'] += p['vx']; p['y'] += p['vy']; p['vy'] -= 0.04
        alive.append(p)
    mouse_trail.clear(); mouse_trail.extend(alive)




def update_draw_particles():
    now   = pygame.time.get_ticks()
    alive = []
    for p in particles:
        age  = (now - p['born']) / 1000.0
        if age >= p['life']:
            continue
        frac = age / p['life']
        if p.get('type') == 'confetti':
            alpha = int(255 * (1 - frac) ** 0.5)
            surf  = pygame.Surface((p['w']+2, p['h']+2), pygame.SRCALPHA)
            surf.fill((p['r'], p['g'], p['b'], alpha))
            rotated = pygame.transform.rotate(surf, p['rot'])
            win.blit(rotated, (int(p['x'])-rotated.get_width()//2,
                               int(p['y'])-rotated.get_height()//2))
            p['x'] += p['vx']; p['y'] += p['vy']
            p['vy'] += 0.25; p['vx'] *= 0.99; p['rot'] += p['rot_speed']
        else:
            alpha = int(200 * (1 - frac) ** 0.7)
            r     = int(p['radius'] * (1 + frac * 1.2))
            surf  = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (p['r'], p['g'], p['b'], alpha), (r+1, r+1), r)
            win.blit(surf, (int(p['x'])-r-1, int(p['y'])-r-1))
            p['x'] += p['vx']; p['y'] += p['vy']
            p['vy'] -= 0.10; p['vx'] *= 0.97
        alive.append(p)
    particles.clear(); particles.extend(alive)




spin_angle = 0.0




def draw_system_icon(cx, cy, wrong):
    size  = 20
    lw    = 3
    color = (255, 80, 80) if wrong else (65, 235, 135)
    for i in range(3):
        base     = spin_angle + i * (2 * math.pi / 3)
        arc_span = math.radians(92)
        arc_end  = base + arc_span
        steps    = 18
        pts      = [(cx + size * math.cos(base + arc_span * s / steps),
                     cy + size * math.sin(base + arc_span * s / steps))
                    for s in range(steps + 1)]
        for j in range(len(pts) - 1):
            pygame.draw.line(win, color,
                             (int(pts[j][0]),   int(pts[j][1])),
                             (int(pts[j+1][0]), int(pts[j+1][1])), lw)
        tip  = (cx + size * math.cos(arc_end), cy + size * math.sin(arc_end))
        perp = arc_end + math.pi / 2
        aw   = 7
        p1   = (tip[0] + aw * math.cos(perp + 0.45), tip[1] + aw * math.sin(perp + 0.45))
        p2   = (tip[0] + aw * math.cos(perp - 0.45), tip[1] + aw * math.sin(perp - 0.45))
        pygame.draw.polygon(win, color, [(int(tip[0]), int(tip[1])),
                                         (int(p1[0]),  int(p1[1])),
                                         (int(p2[0]),  int(p2[1]))])
    label = SYS_FONT.render("RESTARTING..." if wrong else "SYSTEM  READY",
                             True, (255, 80, 80) if wrong else (65, 235, 135))
    win.blit(label, (cx - label.get_width()//2, cy + size + 6))




def draw_danger_symbol(cx, cy, size, alpha):
    h    = int(size * 1.73)
    surf = pygame.Surface((size * 2 + 4, h + 4), pygame.SRCALPHA)
    sx   = size + 2
    pts  = [(sx, 1), (1, h + 1), (size * 2 + 1, h + 1)]
    pygame.draw.polygon(surf, (220, 35, 35, alpha), pts)
    pygame.draw.polygon(surf, (255, 200, 30, min(255, alpha + 50)), pts, 2)
    bar_top = int(h * 0.22)
    bar_bot = int(h * 0.62)
    pygame.draw.line(surf, (255, 230, 50, alpha), (sx, bar_top), (sx, bar_bot), 2)
    pygame.draw.circle(surf, (255, 230, 50, alpha), (sx, int(h * 0.76)), 2)
    win.blit(surf, (cx - size - 2, cy - h//2 - 2))




def draw_status(is_dead, t):
    if not is_dead:
        label = STATUS_FONT.render("STATUS: ALIVE", True, H_GREEN)
        win.blit(label, (14, 12))
        lw = label.get_width(); lh = label.get_height()
        pygame.draw.circle(win, H_GREEN, (14 + lw + 12, 12 + lh//2), 5)
        glow = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(glow, (65, 235, 135, 60), (7, 7), 7)
        win.blit(glow, (14 + lw + 5, 12 + lh//2 - 7))
    else:
        label = STATUS_FONT.render("STATUS: DEAD", True, H_RED)
        win.blit(label, (14, 12))
        lw = label.get_width(); lh = label.get_height()
        pulse = (math.sin(t * 5.0) + 1.0) / 2.0
        draw_danger_symbol(14 + lw + 18, 12 + lh//2, 10, int(55 + pulse * 200))




def draw_gallows():
    pygame.draw.line(win, GALLOWS_CLR, (60,  350), (230, 350), 6)
    pygame.draw.line(win, GALLOWS_CLR, (120, 350), (120,  65), 6)
    pygame.draw.line(win, GALLOWS_CLR, (120,  65), (230,  65), 6)
    pygame.draw.line(win, GALLOWS_CLR, (120, 105), (155,  65), 4)
    pygame.draw.line(win, GALLOWS_CLR, (230,  65), (230,  93), 3)




UPPER_LEN = 22
FORE_LEN  = 19
ARM_LW    = 4
PIVOT_X   = 230
ROPE_END  = 93




def draw_arm(shoulder_x, shoulder_y, neck_x, neck_y, side,
             t, is_dead, struggle_t):
    base_angle = math.radians(150) if side == -1 else math.radians(30)
    if not is_dead:
        swing = math.sin(t * 2.2 + (0 if side == -1 else math.pi)) * 0.38
        upper_angle = base_angle + swing
        elbow_x = shoulder_x + UPPER_LEN * math.cos(upper_angle)
        elbow_y = shoulder_y + UPPER_LEN * math.sin(upper_angle)
        fore_angle = upper_angle + math.radians(18) * side
        hand_x = elbow_x + FORE_LEN * math.cos(fore_angle)
        hand_y = elbow_y + FORE_LEN * math.sin(fore_angle)
    else:


        flail_freq_up   = 28.0
        flail_freq_side = 22.0
        flail_amp_vert  = 1.1
        flail_amp_side  = 0.9
        phase_offset = 0 if side == -1 else math.pi * 0.7
        swing_vert = math.sin(struggle_t * flail_freq_up  + phase_offset) * flail_amp_vert
        swing_side = math.cos(struggle_t * flail_freq_side + phase_offset) * flail_amp_side
        upper_angle = base_angle + swing_vert + swing_side * side
        elbow_x = shoulder_x + UPPER_LEN * math.cos(upper_angle)
        elbow_y = shoulder_y + UPPER_LEN * math.sin(upper_angle)
        fore_angle = upper_angle + math.radians(18) * side + swing_vert * 0.5
        hand_x = elbow_x + FORE_LEN * math.cos(fore_angle)
        hand_y = elbow_y + FORE_LEN * math.sin(fore_angle)




    pygame.draw.line(win, BODY_CLR, (int(shoulder_x), int(shoulder_y)),
                     (int(elbow_x), int(elbow_y)), ARM_LW)
    pygame.draw.circle(win, BODY_CLR, (int(elbow_x), int(elbow_y)), 4)
    pygame.draw.line(win, BODY_CLR, (int(elbow_x), int(elbow_y)),
                     (int(hand_x), int(hand_y)), ARM_LW)
    pygame.draw.circle(win, SKIN_CLR, (int(hand_x), int(hand_y)), 5)
    pygame.draw.circle(win, DARK,     (int(hand_x), int(hand_y)), 5, 1)




def draw_stickman(status, t, struggle_t=0.0, is_dead=False):
    if status == 0:
        return
    HEAD_R = 18
    if not is_dead:
        sway = math.sin(t * 1.9) * 5; bob = math.sin(t * 2.4) * 3
    else:
        sway = math.sin(struggle_t * 20) * 2; bob = 0
    cx       = PIVOT_X + sway
    head_cy  = ROPE_END + HEAD_R + bob
    body_top = head_cy + HEAD_R
    body_bot = body_top + 62 + bob
    arm_y    = body_top + 20
    neck_y   = head_cy + HEAD_R
    if status >= 1:
        pygame.draw.circle(win, SKIN_CLR, (int(cx), int(head_cy)), HEAD_R)
        pygame.draw.circle(win, BODY_CLR, (int(cx), int(head_cy)), HEAD_R, 2)
        if is_dead:
            for ex in (int(cx) - 6, int(cx) + 6):
                ey = int(head_cy) - 3
                pygame.draw.line(win, H_RED, (ex-4, ey-4), (ex+4, ey+4), 2)
                pygame.draw.line(win, H_RED, (ex+4, ey-4), (ex-4, ey+4), 2)
            pygame.draw.arc(win, DARK, pygame.Rect(int(cx)-8, int(head_cy)+6, 16, 8), 0, math.pi, 2)
        else:
            ey = int(head_cy) - 3 + int(bob)
            pygame.draw.circle(win, DARK, (int(cx)-6, ey), 3)
            pygame.draw.circle(win, DARK, (int(cx)+6, ey), 3)
            pygame.draw.arc(win, DARK, pygame.Rect(int(cx)-8, int(head_cy)+4+int(bob), 16, 7), math.pi, 0, 2)
    if status >= 2:
        pygame.draw.line(win, BODY_CLR, (int(cx), int(body_top + bob)), (int(cx), int(body_bot)), 4)
    if status >= 3:
        draw_arm(cx, arm_y + bob, cx, neck_y, -1, t, is_dead, struggle_t)
    if status >= 4:
        draw_arm(cx, arm_y + bob, cx, neck_y, +1, t, is_dead, struggle_t)
    LEG_LEN = 48
    if not is_dead:
        ll_swing = math.sin(t * 1.7) * 9
        rl_swing = math.sin(t * 1.7 + math.pi) * 9
    else:


        ll_swing = math.sin(struggle_t * 30) * 38
        rl_swing = math.sin(struggle_t * 30 + math.pi) * 38
    if status >= 5:
        pygame.draw.line(win, BODY_CLR, (int(cx), int(body_bot)),
                         (int(cx - LEG_LEN + ll_swing), int(body_bot + LEG_LEN)), 4)
    if status >= 6:
        pygame.draw.line(win, BODY_CLR, (int(cx), int(body_bot)),
                         (int(cx + LEG_LEN + rl_swing), int(body_bot + LEG_LEN)), 4)




HINT_BTN = pygame.Rect(666, 175, 120, 44)
HINT_FONT_BTN = pygame.font.SysFont('Courier', 17, bold=True)




def draw_hint_button(hint_used, mx, my):
    hovered = HINT_BTN.collidepoint(mx, my) and not hint_used
    if hint_used:
        pygame.draw.rect(win, (40, 40, 60),   HINT_BTN.move(3, 3), border_radius=10)
        pygame.draw.rect(win, (55, 55, 75),   HINT_BTN,            border_radius=10)
        pygame.draw.rect(win, (90, 90, 110),  HINT_BTN, 2,         border_radius=10)
        cx, cy = HINT_BTN.centerx, HINT_BTN.centery
        pygame.draw.line(win, H_RED, (cx - 16, cy - 16), (cx + 16, cy + 16), 5)
        pygame.draw.line(win, H_RED, (cx + 16, cy - 16), (cx - 16, cy + 16), 5)
    else:
        base_col  = (55, 160, 80) if not hovered else (70, 200, 100)
        pygame.draw.rect(win, (20, 60, 30),  HINT_BTN.move(3, 3), border_radius=10)
        pygame.draw.rect(win, base_col,      HINT_BTN,            border_radius=10)
        pygame.draw.rect(win, (150, 255, 170), HINT_BTN, 2,       border_radius=10)
        label = HINT_FONT_BTN.render("HINT BOX", True, WHITE)
        win.blit(label, label.get_rect(center=HINT_BTN.center))




def draw_hangman(word, Guessed, letters, hangman_status, t, wrong_flash, hint_used, mx, my):
    draw_background()
    draw_gallows()
    draw_stickman(hangman_status, t)
    draw_system_icon(WIDTH - 65, 42, wrong_flash > 0.1)
    draw_status(False, t)
    draw_hint_button(hint_used, mx, my)




    display_word = ""
    for letter in word:
        display_word += (letter if letter in Guessed else "_") + " "
    display_word = display_word.rstrip()
    font = best_word_font(display_word)
    text = font.render(display_word, 1, TEXT_CLR)
    win.blit(text, (WORD_CENTER_X - text.get_width()//2, WORD_Y))




    for letter in letters:
        x, y, ltr, visible = letter
        ring_col = BODY_CLR if visible else GREY
        txt_col  = TEXT_CLR if visible else GREY
        pygame.draw.circle(win, ring_col, (x, y), RADIUS, 2)
        txt = LETTER_FONT.render(ltr, 1, txt_col)
        win.blit(txt, (x - txt.get_width()/2, y - txt.get_height()/2))




    update_draw_particles()
    update_draw_flame_trail()




    if wrong_flash > 0:
        alpha   = int(wrong_flash * 160)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((200, 30, 30, alpha))
        win.blit(overlay, (0, 0))
        bang = FLASH_FONT.render("WRONG!", 1, (255, 255, 80))
        win.blit(bang, (WIDTH//2 - bang.get_width()//2, HEIGHT//2 - bang.get_height()//2 - 30))




    pygame.display.update()




def run_win_animation(word):
    start    = pygame.time.get_ticks()
    FALL_DUR = 750
    TOTAL    = 2800
    PIVOT_X2, PIVOT_Y2 = 60, 350
    SEGS = [
        (60,  350, 230, 350, 6), (120, 350, 120, 65, 6),
        (120, 65,  230, 65,  6), (120, 105, 155, 65, 4),
        (230, 65,  230, 93,  3),
    ]




    def rot(px, py, a):
        dx, dy = px - PIVOT_X2, py - PIVOT_Y2
        return (int(PIVOT_X2 + dx*math.cos(a) - dy*math.sin(a)),
                int(PIVOT_Y2 + dx*math.sin(a) + dy*math.cos(a)))




    def draw_fallen_gallows(angle):
        for x1, y1, x2, y2, lw in SEGS:
            pygame.draw.line(win, GALLOWS_CLR, rot(x1,y1,angle), rot(x2,y2,angle), lw)




    dust_done = confetti_done = False
    while True:
        clock.tick(FPS)
        elapsed = pygame.time.get_ticks() - start
        if elapsed >= TOTAL:
            return True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        mx, my = pygame.mouse.get_pos()
        spawn_flame(mx, my)
        draw_background()
        if elapsed < FALL_DUR:
            angle = ((elapsed / FALL_DUR) ** 2) * math.radians(90)
        else:
            settle_t = min((elapsed - FALL_DUR) / 500.0, 1.0)
            wobble   = math.sin(settle_t * math.pi * 5) * (1 - settle_t) * math.radians(5)
            angle    = math.radians(90) + wobble
        if elapsed >= FALL_DUR and not dust_done:
            dust_done = True
            for x_pos in (180, 240, 300):
                spawn_smoke(x_pos, 345)
        if elapsed >= FALL_DUR and not confetti_done:
            confetti_done = True
            spawn_confetti(WIDTH//2, HEIGHT//2, count=90)
        draw_fallen_gallows(angle)
        update_draw_particles()
        update_draw_flame_trail()
        draw_system_icon(WIDTH - 65, 42, False)
        draw_status(False, elapsed / 1000.0)
        wfont = best_word_font(" ".join(word))
        txt   = wfont.render(" ".join(word), 1, TEXT_CLR)
        win.blit(txt, (WORD_CENTER_X - txt.get_width()//2, WORD_Y))
        if elapsed > FALL_DUR:
            show_frac = min((elapsed - FALL_DUR) / 350.0, 1.0)
            msg_surf  = WORD_FONT.render("You Won!", True, H_GREEN)
            msg_surf.set_alpha(int(show_frac * 255))
            win.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, WORD_Y - 55))
        pygame.display.update()
    return True




def run_death_animation(word):
    start    = pygame.time.get_ticks()
    STRUGGLE = 1800
    TOTAL    = 3400
    while True:
        clock.tick(FPS)
        elapsed = pygame.time.get_ticks() - start
        if elapsed >= TOTAL:
            return True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        mx, my = pygame.mouse.get_pos()
        spawn_flame(mx, my)
        draw_background()
        draw_gallows()
        draw_system_icon(WIDTH - 65, 42, True)
        struggle_t = (elapsed / 1000.0) * 2.0
        is_dead    = elapsed > STRUGGLE
        draw_stickman(6, 0, struggle_t, is_dead)
        draw_status(is_dead, elapsed / 1000.0)
        update_draw_flame_trail()
        if is_dead:
            msg = WORD_FONT.render("You Lost!", 1, H_RED)
            win.blit(msg, (WIDTH/2 - msg.get_width()/2, HEIGHT/2 - msg.get_height()/2))
            ans = HINT_FONT.render(f"The word was:  {word}", 1, TEXT_CLR)
            win.blit(ans, (WIDTH/2 - ans.get_width()/2, HEIGHT/2 + msg.get_height()/2 + 5))
        pygame.display.update()
    return True




scene      = "hangman"
run_game   = True
used_words = []
last_time  = pygame.time.get_ticks() / 1000.0




reels          = [Reel(i) for i in range(3)]
slot_spinning  = False
slot_done      = False
slot_got_result = False
slot_three_star = False
slot_win_timer  = 0.0
slot_message    = ""
slot_msg_timer  = 0.0
slot_win_glow   = 0.0
slot_return_timer = 0.0




spin_btn = pygame.Rect(WIDTH // 2 - 80, 330, 160, 50)




def reset_slot():
    global slot_spinning, slot_done, slot_got_result, slot_three_star
    global slot_win_timer, slot_message, slot_msg_timer, slot_win_glow, slot_return_timer
    for r in reels:
        r.reset()
    slot_spinning     = False
    slot_done         = False
    slot_got_result   = False
    slot_three_star   = False
    slot_win_timer    = 0.0
    slot_message      = ""
    slot_msg_timer    = 0.0
    slot_win_glow     = 0.0
    slot_return_timer = 0.0




while run_game:




    available = [w for w in words if w not in used_words]
    if not available:
        draw_background()
        text = WORD_FONT.render("All Elements Used!", 1, TEXT_CLR)
        win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))
        pygame.display.update()
        pygame.time.delay(3000)
        break




    hangman_status = 0
    Guessed        = []
    word           = random.choice(available)
    used_words.append(word)
    letters        = create_letters()
    game_over      = False
    wrong_flash    = 0.0
    FLASH_DECAY    = 0.035
    hint_used      = False
    reset_slot()




    while not game_over:
        clock.tick(FPS)
        t         = pygame.time.get_ticks() / 1000.0
        dt        = t - last_time
        last_time = t
        dt        = min(dt, 0.05)




        spin_speed  = 5.5 if wrong_flash > 0.05 else 1.8
        spin_angle += spin_speed * dt




        if wrong_flash > 0:
            wrong_flash = max(0.0, wrong_flash - FLASH_DECAY)




        mx, my = pygame.mouse.get_pos()




        if scene == "hangman":
            spawn_flame(mx, my)
            draw_hangman(word, Guessed, letters, hangman_status, t,
                         wrong_flash, hint_used, mx, my)




            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_game = False; game_over = True




                if event.type == pygame.MOUSEBUTTONDOWN:
                    ex, ey = pygame.mouse.get_pos()




                    if HINT_BTN.collidepoint(ex, ey) and not hint_used:
                        scene = "slot"
                        reset_slot()




                    else:
                        for letter in letters:
                            lx, ly, ltr, visible = letter
                            if visible:
                                if math.sqrt((lx - ex)**2 + (ly - ey)**2) < RADIUS:
                                    letter[3] = False
                                    spawn_smoke(lx, ly)
                                    Guessed.append(ltr)
                                    if ltr not in word:
                                        hangman_status += 1
                                        wrong_flash = 1.0




            won = all(l in Guessed for l in word)
            if won:
                if not run_win_animation(word):
                    run_game = False
                game_over = True




            if hangman_status == 6 and not won:
                if not run_death_animation(word):
                    run_game = False
                game_over = True




        else:
            win.fill((170, 140, 80))
            draw_slot_body()




            title = font_med.render("★  HINT BOX  ★", True, DARK_GOLD)
            win.blit(title, title.get_rect(centerx=WIDTH // 2, top=100))




            flash_val = slot_win_timer / WIN_SEQ_DUR if slot_three_star else 0.0
            for i, reel in enumerate(reels):
                rx = S_REEL_START + i * (S_REEL_W + S_REEL_GAP)
                reel.draw(rx, S_REEL_TOP, flash=flash_val)
                reel.update(dt)




            if slot_win_glow > 0 and not slot_three_star:
                glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                glow_surf.fill((255, 220, 0, int(slot_win_glow * 80)))
                win.blit(glow_surf, (0, 0))




            spin_hov = spin_btn.collidepoint(mx, my)




            if not slot_got_result:
                draw_slot_button(spin_btn, "SPIN", ORANGE, GOLD, WHITE,
                                 spin_hov and not slot_spinning)
                if slot_spinning:
                    pygame.draw.rect(win, S_GRAY, spin_btn, border_radius=12)
                    lbl = font_med.render("SPIN", True, S_DARK_GRAY)
                    win.blit(lbl, lbl.get_rect(center=spin_btn.center))
            else:
                if not slot_three_star or slot_win_timer <= 0:
                    pygame.draw.rect(win, S_GRAY, spin_btn, border_radius=12)
                    lbl = font_med.render("SPIN", True, S_DARK_GRAY)
                    win.blit(lbl, lbl.get_rect(center=spin_btn.center))




            if slot_three_star and slot_win_timer > 0:
                draw_slot_win_sequence(slot_win_timer)
                slot_win_timer -= dt
                if slot_win_timer <= 0:
                    slot_win_timer  = 0.0
                    slot_three_star = False
                    slot_message    = "you got a free hint"
                    slot_msg_timer  = 3.0
                    slot_return_timer = 2.5
                    hidden = [l for l in word if l not in Guessed]
                    if hidden:
                        revealed = random.choice(hidden)
                        Guessed.append(revealed)
                        for letter in letters:
                            if letter[2] == revealed:
                                letter[3] = False
                                break
            elif slot_message and slot_msg_timer > 0:
                for txt_s, col, off in [
                    (slot_message, SHADOW,    (2, 2)),
                    (slot_message, DARK_GOLD, (0, 0)),
                ]:
                    s = font_med.render(txt_s, True, col)
                    r = s.get_rect(centerx=WIDTH // 2, top=415)
                    win.blit(s, r.move(*off))
                slot_msg_timer -= dt




            if slot_got_result and not slot_three_star:
                if slot_return_timer > 0:
                    slot_return_timer -= dt
                    secs = max(0, math.ceil(slot_return_timer))
                    back_label = SYS_FONT.render(f"Returning to game in {secs}...", True, TEXT_CLR)
                    win.blit(back_label, back_label.get_rect(centerx=WIDTH // 2, top=466))
                else:
                    scene     = "hangman"
                    hint_used = True




            if slot_spinning and not slot_done:
                if all(not r.spinning for r in reels):
                    slot_done         = True
                    slot_spinning     = False
                    slot_got_result   = True
                    syms = [r.symbol for r in reels]
                    if syms[0] == "★" and syms[1] == "★" and syms[2] == "★":
                        slot_three_star   = True
                        slot_win_timer    = WIN_SEQ_DUR
                        slot_win_glow     = 1.0
                    else:
                        slot_message      = "Out of luck"
                        slot_msg_timer    = 3.0
                        slot_win_glow     = 0.0
                        slot_return_timer = RETURN_DELAY




            pygame.display.update()




            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_game = False; game_over = True




                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if (spin_btn.collidepoint(mx, my)
                            and not slot_spinning
                            and not slot_got_result
                            and not slot_three_star):
                        slot_spinning = True
                        slot_done     = False
                        res = [weighted_symbol() for _ in range(3)]
                        for i, reel in enumerate(reels):
                            reel.start(res[i])




pygame.quit()
sys.exit








