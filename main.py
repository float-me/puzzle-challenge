import pygame
from pygame import Surface, Vector2, Color
from pygame.sprite import Group
from pygame_plus import *
from pygame import QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN
from typing import List, Dict
from typing_extensions import Self
import os
import re
from prime_generator import find_prime

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

pygame.init()

# 이벤트 제한
pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN])

# 스크린 객체 저장
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
SCREEN_LIKE = Surface(Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))
SCREEN_LIKE.fill(Color("White"))
SCREEN_RECT = SCREEN.get_rect()

pygame.display.set_caption("mini puzzle game")
# FPS를 위한 Clock 생성
clock = pygame.time.Clock()

FPS = 60

BACKGROUND_COLOR = Color('white')

MODE_NAME = ["쉬워요", "헷갈려요", "어려워요", "어지러워요"]
MODE_POINTS = [1, 3, 5, 10]
NUM_LEVELS = [0, 0, 0, 0]

PT = 0

for file in os.listdir("./map"):
    mode, _ = file.rstrip("\n").split("_")
    idx = MODE_NAME.index(mode)
    NUM_LEVELS[idx] += 1

CLEARED = [[False]*i for i in NUM_LEVELS]

SOUND_SELECT_MAP = pygame.mixer.Sound("./music/효과_맵선택.wav")
SOUND_SWITCH_ON = pygame.mixer.Sound("./music/효과_상자버튼.wav")
SOUND_SWITCH_ON.set_volume(0.5)
SOUND_SWITCH_OFF = pygame.mixer.Sound("./music/효과_상자버튼해제.wav")
SOUND_SWITCH_OFF.set_volume(0.5)
SOUND_CLEAR = pygame.mixer.Sound("./music/효과_클리어.wav")
SOUND_CLEAR.set_volume(0.5)
FIRST_CHAN = pygame.mixer.Channel(0)
SECOND_CHAN = pygame.mixer.Channel(1)

DEFAULT_FONT = get_font(40)
def quick_render(text: str, color):
    """
    DEFAULT_FONT로 render해주는 함수입니다.
    """
    return DEFAULT_FONT.render(text, True, Color(color))
def simple_render_gen(size):
    """
    render 함수를 생성해주는 함수입니다.
    """
    def render(text, color):
        f"""
        EF_Rebecca(윈도우용_TTF), {size}의 폰트로 render해주는 함수입니다.
        simple_render_gen에 의해 생성되었습니다.
        """
        return get_font(size).render(text, True, Color(color))
    return render

class MessageSprite(AnimatedSprite):
    def __init__(self, msg, color, position: Position, init: int = 0, mult: int = 1, _sub_init: int = 0, positional_relation="center", render_func=quick_render) -> None:
        super().__init__(position, EMPTY_SURFACE, init, mult, _sub_init, positional_relation)
        self.quick_msg_update(msg, color, render_func)
    def quick_msg_update(self, msg=None, color=None, render_func=None) -> None:
        if msg != None:
            self.msg = msg
        if color != None:
            self.color = color
        if render_func != None:
            self.render_func = render_func
        self.image = self.render_func(self.msg, self.color)

EMPTY_SURFACE = Surface((0, 0))

class Button(Group):
    def __init__(self, msg: str, position: Position, size: Vector2, button_color="Black", text_color="White",
    positional_relation="center", render_func=quick_render) -> None:
        surf = Surface(size)
        surf.fill(button_color)
        self.rect_part = AnimatedSprite(position, surf, positional_relation=positional_relation)
        self.txt_part = MessageSprite(msg, text_color, Position(0, parent=self.rect_part.rect), render_func=render_func)
        super().__init__(self.rect_part, self.txt_part)
    def is_pressed(self, mouse_pos):
        return self.rect_part.rect.collidepoint(*mouse_pos)

ESC_BUTTON = Button("뒤로", Position(75, 750, positional_relation="topleft"), Vector2(100, 50),
render_func=simple_render_gen(20))

class MenuState(State):
    def __init__(self) -> None:
        super().__init__()
        self.background = SCREEN.copy()
        self.background.fill(Color("White"))
        self.bt1 = Button("시작", Position(0, -200, parent=SCREEN_RECT), Vector2(200, 100))
        self.bt2 = Button("저장", Position(0, -50, parent=SCREEN_RECT), Vector2(200, 100))
        self.bt3 = Button("불러오기", Position(0, 100, parent=SCREEN_RECT), Vector2(200, 100))
        self.group = Group(self.bt1, self.bt2, self.bt3)
    def execute(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.bt1.is_pressed(mouse_pos):
                        return LevelState(0)
                    if self.bt2.is_pressed(mouse_pos):
                        return SaveState()
                    if self.bt3.is_pressed(mouse_pos):
                        return LoadState()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:
                        return LevelState(0)
            self.ordinary_work(SCREEN, clock, FPS)

import string
CHAR_LIST = list(string.ascii_lowercase) + list(string.ascii_uppercase) + list("0123456789_@")
def num_to_string(num):
    s = bin(num)[2:]
    res = ""
    for i in range(0, len(s), 6):
        idx = eval("0b"+s[i:i+6])
        res += CHAR_LIST[idx]
    return res

def string_to_num(s):
    res = ""
    for v in s:
        new = bin(CHAR_LIST.index(v))[2:].zfill(6)
        res += new
    return eval("0b"+res)

class SaveState(State):
    def __init__(self) -> None:
        super().__init__()
        self.background = SCREEN.copy()
        self.background.fill(Color("White"))
        p, q = find_prime(), find_prime()
        code = num_to_string(p*q)
        self.file = f"./save/{code}.txt"
        save_expl = Button("저장 코드: 꼭 보관하세요!", Position(0, -150, parent=SCREEN_RECT), Vector2(450, 60),
        render_func=simple_render_gen(30), button_color="Orange")
        self.save_btn = Button("저장", Position(0, 100, parent=SCREEN_RECT), Vector2(200, 100))
        self.group = Group(ESC_BUTTON, self.save_btn, save_expl)
        self.group.add(MessageSprite(num_to_string(p)+num_to_string(q), Color("Black"), Position(0, -60, parent=SCREEN_RECT)))
    def save(self):
        with open(self.file, "w", encoding="UTF-8") as f:
            for line in CLEARED:
                for v in line:
                    f.write(f"{int(v)} ")
                f.write("\n")
    def execute(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if ESC_BUTTON.is_pressed(mouse_pos):
                        return "before"
                    if self.save_btn.is_pressed(mouse_pos):
                        self.save()
                        return "before"
            self.ordinary_work(SCREEN, clock, FPS)

class LoadState(State):
    def __init__(self) -> None:
        super().__init__()
        self.background = SCREEN.copy()
        self.background.fill(Color("White"))
        self.load_expl = Button("저장 코드를 입력하세요!", Position(0, -150, parent=SCREEN_RECT), Vector2(450, 60),
        render_func=simple_render_gen(30), button_color="Orange")
        self.load_btn = Button("불러오기", Position(0, 100, parent=SCREEN_RECT), Vector2(200, 100))
        self.input_box = MessageSprite("", Color("Black"), Position(0, -60, parent=SCREEN_RECT))
        self.group = Group(ESC_BUTTON, self.load_btn, self.load_expl, self.input_box)
    @property
    def msg(self):
        return self.input_box.msg
    @msg.setter
    def msg(self, val):
        return self.input_box.quick_msg_update(msg=val)
    def load(self):
        if len(self.msg) != 16:
            return False
        p, q = string_to_num(self.msg[:8]), string_to_num(self.msg[8:])
        code = num_to_string(p*q)
        file_name = f"./save/{code}.txt"
        if not os.path.exists(file_name):
            return False
        with open(file_name, "r", encoding="UTF-8") as f:
            global CLEARED, PT
            CLEARED = [list(map(lambda x: [False, True][int(x)], line.rstrip('\n').split())) for line in f.readlines()]
            PT = 0
            for idx, line in enumerate(CLEARED):
                PT += MODE_POINTS[idx]*line.count(True)
        return True
    def execute(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    self.load_expl.rect_part.image.fill(Color("Orange"))
                    self.load_expl.txt_part.quick_msg_update(msg="저장 코드를 입력하세요!")
                    if event.key == pygame.K_BACKSPACE:
                            if len(self.msg) > 0:
                                self.msg = self.msg[:-1]
                    elif event.key == pygame.K_RETURN:
                        res = self.load()
                        if res:
                            return "before"
                        else:
                            self.load_expl.rect_part.image.fill(Color("Red"))
                            self.load_expl.txt_part.quick_msg_update(msg="올바르지 않은 코드입니다.")
                    else:
                        val = event.unicode
                        if re.compile("[\w_@]").match(val):
                            self.msg += val
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if ESC_BUTTON.is_pressed(mouse_pos):
                        return "before"
                    if self.load_btn.is_pressed(mouse_pos):
                        res = self.load()
                        if res:
                            return "before"
                        else:
                            self.load_expl.rect_part.image.fill(Color("Red"))
                            self.load_expl.txt_part.quick_msg_update(msg="올바르지 않은 코드입니다.")
            self.ordinary_work(SCREEN, clock, FPS)

class LevelState(State):
    def __init__(self, mode) -> None:
        super().__init__()
        self.background = SCREEN.copy()
        self.background.fill(Color("White"))
        pt_sign = MessageSprite(f"pt: {PT}", Color("Black"), Position(30, positional_relation="topleft"),
        positional_relation="topleft", render_func=simple_render_gen(20))
        num_lines = -((-NUM_LEVELS[mode]) // 5)
        tile_size = 600/max(5, num_lines)
        self.group = Group(ESC_BUTTON, pt_sign)
        center_pos = Position(0, -300, parent=SCREEN_RECT)
        self.difficulty = [Button(MODE_NAME[i], Position(-300+200*i, 0, parent=center_pos), Vector2(150, 50), render_func=simple_render_gen(25)) for i in range(4)]
        self.buttons: List[Button] = []
        self.mode = mode
        for i in range(NUM_LEVELS[mode]):
            position = Vector2(400) + tile_size*(Vector2(i%5, i//5) - Vector2(4, num_lines-1)/2)
            btn = Button(str(i+1), Position(position, positional_relation="topleft"), 0.9*Vector2(tile_size),
            render_func=simple_render_gen(tile_size*0.4))
            self.group.add(btn)
            self.buttons.append(btn)
        for idx, diff in enumerate(self.difficulty):
            exp = Button(f"{MODE_POINTS[idx]} pt ({CLEARED[idx].count(True)}/{NUM_LEVELS[idx]})", Position(0, 50, parent=diff.rect_part), Vector2(120, 30),
            render_func=simple_render_gen(15))
            if all(CLEARED[idx]):
                exp.rect_part.image.fill(Color("Gold"))
                diff.rect_part.image.fill(Color("Gold"))
            if idx == mode:
                diff.rect_part.image.fill(Color("OrangeRed"))
            self.group.add(diff, exp)
    def execute(self):
        running = True
        while running:
            for idx, button in enumerate(self.buttons):
                if CLEARED[self.mode][idx]:
                    button.rect_part.image.fill(Color("Gold"))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        return "before"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if ESC_BUTTON.is_pressed(mouse_pos):
                        return "before"
                    for btn in self.buttons:
                        if btn.is_pressed(mouse_pos):
                            FIRST_CHAN.play(SOUND_SELECT_MAP)
                            return GameState(self.mode, int(btn.txt_part.msg))
                    for idx, diff in enumerate(self.difficulty):
                        if diff.is_pressed(mouse_pos):
                            State.on.pop()
                            return LevelState(idx)
            self.ordinary_work(SCREEN, clock, FPS)

class Direction(Vector2):
    pass
D_c = Direction(0)
D_r = Direction(1, 0)
D_l = Direction(-1, 0)
D_u = Direction(0, -1)
D_d = Direction(0, 1)
TILE_LAND = Surface(Vector2(100))
TILE_LAND.fill(Color("BurlyWood"))
TILE_WALL = Surface(Vector2(100))
TILE_WALL.fill("DimGray")
TILE_ICE = Surface(Vector2(100))
TILE_ICE.fill(Color("LightCyan"))
SHAPE_SWITCH = Surface(Vector2(100), flags=pygame.SRCALPHA)
pygame.draw.circle(SHAPE_SWITCH, Color("SlateGray"), Vector2(50), 35)
SHAPE_SWITCH_PRESSED = Surface(Vector2(100), flags=pygame.SRCALPHA)
pygame.draw.circle(SHAPE_SWITCH_PRESSED, Color("Gold"), Vector2(50), 35)
SHAPE_BOX = Surface(Vector2(100), flags=pygame.SRCALPHA)
pygame.draw.rect(SHAPE_BOX, Color("SandyBrown"), pygame.Rect((20, 20, 60, 60)))
SHAPE_ICYBOX = Surface(Vector2(100), flags=pygame.SRCALPHA)
pygame.draw.rect(SHAPE_ICYBOX, Color("LightSkyBlue"), pygame.Rect((20, 20, 60, 60)))
SHAPE_PLAYER = Surface(Vector2(100), flags=pygame.SRCALPHA)
pygame.draw.polygon(SHAPE_PLAYER, Color("MediumAquaMarine"), ((30, 85), (70, 85), (50, 30)))
pygame.draw.circle(SHAPE_PLAYER, Color("MediumAquaMarine"), Vector2(50, 30), 15)
SHAPE_SKIP_BASE = [Surface(Vector2(100), flags=pygame.SRCALPHA) for i in range(4)]
POLYGON_ARROW = tuple(map(Vector2, ((10, 10), (30, 10), (50, 50), (30, 90), (10, 90), (30, 50))))
POLYGON_ARROW_2 = tuple(map(lambda x: x+Vector2(40, 0), POLYGON_ARROW))
POLYGON_ARROW_3 = tuple(map(lambda x: x+Vector2(-40, 0), POLYGON_ARROW))
POLYGON_ARROW_4 = tuple(map(lambda x: x+Vector2(40, 0), POLYGON_ARROW_2))
for i in range(4):
    surf = SHAPE_SKIP_BASE[i]
    pygame.draw.polygon(surf, Color("LightSalmon"), tuple(map(lambda x: x+Vector2(10*i, 0), POLYGON_ARROW)))
    pygame.draw.polygon(surf, Color("LightSalmon"), tuple(map(lambda x: x+Vector2(10*i, 0), POLYGON_ARROW_2)))
    pygame.draw.polygon(surf, Color("LightSalmon"), tuple(map(lambda x: x+Vector2(10*i, 0), POLYGON_ARROW_3)))
    pygame.draw.polygon(surf, Color("LightSalmon"), tuple(map(lambda x: x+Vector2(10*i, 0), POLYGON_ARROW_4)))
SHAPES_SKIP = [[pygame.transform.rotate(surf, 90*i) for surf in SHAPE_SKIP_BASE] for i in range(4)]

WALL_INFO = {
    "l": {
        (-1, 0): (False, False),
        (1, 0): (False, False),
        (0, -1): (False, False),
        (0, 1): (False, False),
    },
    "i": {
        (-1, 0): (False, False),
        (1, 0): (False, False),
        (0, -1): (False, False),
        (0, 1): (False, False),
    },
    "w": {
        (-1, 0): (True, True),
        (1, 0): (True, True),
        (0, -1): (True, True),
        (0, 1): (True, True),
    },
}

for s in ["r", "l", "d", "u"]:
    WALL_INFO["m"+s] = WALL_INFO["l"]

BOOSTED = False

class GameState(State):
    def __init__(self, mode, level) -> None:
        super().__init__()
        self.background = SCREEN.copy()
        self.background.fill(Color("White"))
        self.level = level
        self.mode = mode
        file_name = f"./map/{MODE_NAME[mode]}_{level}.txt"
        level_sign = MessageSprite(f"\"{MODE_NAME[mode]}\" - Lv. {level}", Color("Black"), Position(30, positional_relation="topleft"),
        positional_relation="topleft")
        self.boost = Button("BOOST", Position(75, 600, positional_relation="topleft"), Vector2(100, 200),
        button_color=Color("Navy"), text_color=Color("LightCoral"), render_func=simple_render_gen(20))
        self.group = Group(level_sign, ESC_BUTTON, self.boost)
        with open(file_name, "r", encoding="UTF-8") as f:
            level_map = [list(line.rstrip('\n').split()) for line in f.readlines()]
            self.y, self.x = len(level_map), len(level_map[0])
            self.size = Vector2(self.x, self.y)
        tile_size = 500 / max(self.x, self.y)
        _resize = lambda surf: pygame.transform.scale(surf, Vector2(tile_size)*0.9)
        tile_land = _resize(TILE_LAND)
        tile_ice = _resize(TILE_ICE)
        tile_wall = _resize(TILE_WALL)
        shape_switch = _resize(SHAPE_SWITCH)
        shape_switch_pressed = _resize(SHAPE_SWITCH_PRESSED)
        shape_box = _resize(SHAPE_BOX)
        shape_player = _resize(SHAPE_PLAYER)
        shape_icybox = _resize(SHAPE_ICYBOX)
        shapes_skip = list(map(lambda lst: list(map(_resize, lst)), SHAPES_SKIP))
        self.tile_map = {}
        class Moveable(AnimatedSprite):
            Map: Dict[tuple, Self] = {}
            def __init__(ins, key: str, pos: Vector2, images: Surface | List[Surface], init: int = 0, mult: int = 1, _sub_init: int = 0, positional_relation="topleft") -> None:
                position = Position(Vector2(400) + (pos - self.size/2)*tile_size, positional_relation="topleft")
                super().__init__(position, images, init, mult, _sub_init, positional_relation)
                ins.key = key
                ins.dir = D_c
                ins.pos = pos
                ins.rate = 0
                ins.speed = ins._speed = 0.03
                Moveable.Map[tuple(pos)] = ins
            def get_map(pos):
                return Moveable.Map[tuple(pos)]
            def set_dir(ins, dir: Direction):
                ins.dir = dir
                if dir == D_c:
                    return True
                tile_now = self.get_tile(ins.pos)
                end_pos = ins.pos + dir
                tile_end = self.get_tile(end_pos)
                if tile_end == None:
                    ins.dir = D_c
                    return False
                rot_dir = dir.rotate(90)
                if WALL_INFO[tile_now][tuple(dir)][0] or WALL_INFO[tile_end][tuple(-dir)][1]:
                    ins.dir = D_c
                    return False
                try:
                    mv = Moveable.get_map(end_pos)
                    if mv.dir in [D_c, -dir, rot_dir, -rot_dir]:
                        ins.dir = D_c
                        return False
                    if mv.dir == dir and mv.speed < ins.speed:
                        ins.dir = D_c
                        return False
                except KeyError:
                    pass

                try:
                    mv = Moveable.get_map(end_pos + dir)
                    if mv.dir == -dir:
                        ins.dir = D_c
                        return False
                except KeyError:
                    pass

                try:
                    mv = Moveable.get_map(end_pos + rot_dir)
                    if mv.dir == -rot_dir:
                        ins.dir = D_c
                        return False
                except KeyError:
                    pass

                try:
                    mv = Moveable.get_map(end_pos - rot_dir)
                    if mv.dir == rot_dir:
                        ins.dir = D_c
                        return False
                except KeyError:
                    pass

            def set_position(ins):
                ins._position_getter = Position(Vector2(400) + (ins.pos - self.size/2)*tile_size, positional_relation="topleft")

            def get(ins):
                if ins.dir == D_c:
                    ins.speed = ins._speed
                    return
                ins.rate += ins.speed
                if ins.rate < 1:
                    ins.move(ins.dir*ins.speed*tile_size)
                    return
                next_pos = ins.pos + ins.dir
                if tuple(next_pos) in Moveable.Map:
                    ins.rate = 1 - ins.speed
                    return
                ins.rate = 0
                
                del Moveable.Map[tuple(ins.pos)]
                ins.pos = next_pos
                cur_tile = self.tile_map[tuple(next_pos)]
                if cur_tile[0] == "m":
                    dir = [D_r, D_d, D_l, D_u][["r", "d", "l", "u"].index(cur_tile[1])]
                    if ins.key == "player":
                        try:
                            box = self.get_map(ins.pos + dir)
                            if box.key in ["box", "icybox"] and box.dir == D_c:
                                box.set_dir(dir)
                                box._speed = box.speed = self.player.speed
                        except KeyError:
                            pass
                    ins.set_dir(dir)
                elif cur_tile == "i":
                    ins.set_dir(ins.dir)
                elif ins.key == "icybox":
                    ins.set_dir(ins.dir)
                else:
                    ins.set_dir(D_c)
                ins.set_position()
                Moveable.Map[tuple(next_pos)] = ins
        self.__Moveable = Moveable
        class Switch(AnimatedSprite):
            lst = []
            def __init__(ins, pos: Vector2, init: int = 0, mult: int = 1, _sub_init: int = 0, positional_relation="topleft") -> None:
                position = Position(Vector2(400) + (pos - self.size/2)*tile_size, positional_relation="topleft")
                super().__init__(position, shape_switch, init, mult, _sub_init, positional_relation)
                ins.pos = pos
                ins.on = False
                Switch.lst.append(ins)
                ins.on_key = None
            def check_pressed(ins):
                try:
                    mv = self.get_map(ins.pos)
                    if mv.dir == D_c:
                        if not ins.on:
                            ins.set_image(shape_switch_pressed)
                            ins.on = True
                            ins.on_key = mv.key
                            if mv.key != "player":
                                SECOND_CHAN.play(SOUND_SWITCH_ON)
                    else:
                        if ins.on:
                            ins.set_image(shape_switch)
                            ins.on = False
                            if ins.on_key != "player":
                                SECOND_CHAN.play(SOUND_SWITCH_OFF)
                except:
                    if ins.on:
                        ins.set_image(shape_switch)
                        ins.on = False
                        if ins.on_key != "player":
                            SECOND_CHAN.play(SOUND_SWITCH_OFF)
                return ins.on
        self.__Switch = Switch
        top_layer = Group()
        bottom_layer = Group()
        for x in range(self.x):
            for y in range(self.y):
                val = level_map[y][x]
                self.tile_map[(x, y)] = val[0]
                pos = Vector2(x, y)
                position = Vector2(400) + (pos - self.size/2)*tile_size
                if val[0] == "l":
                    self.background.blit(tile_land, position)
                elif val[0] == "i":
                    self.background.blit(tile_ice, position)
                elif val[0] == "w":
                    self.background.blit(tile_wall, position)
                    continue
                sub = val[1:]
                if sub == "":
                    continue
                elif sub == "s":
                    switch = Switch(pos)
                    bottom_layer.add(switch)
                elif sub == "b":
                    box = Moveable("box", pos, shape_box)
                    top_layer.add(box)
                elif sub == "sb" or sub == "bs":
                    switch = Switch(pos)
                    bottom_layer.add(switch)
                    box = Moveable("box", pos, shape_box)
                    top_layer.add(box)
                elif sub == "ibs" or sub == "sib":
                    switch = Switch(pos)
                    bottom_layer.add(switch)
                    icybox = Moveable("icybox", pos, shape_icybox)
                    top_layer.add(icybox)
                elif sub == "ib":
                    icybox = Moveable("icybox", pos, shape_icybox)
                    top_layer.add(icybox)
                elif sub == "p":
                    self.player = Moveable("player", pos, shape_player)
                    top_layer.add(self.player)
                elif sub[0] == "m":
                    shapes = shapes_skip[["r", "u", "l", "d"].index(sub[1])]
                    self.move_tile = AnimatedSprite(Position(position, positional_relation="topleft"), shapes, positional_relation="topleft",
                    mult=10)
                    self.tile_map[(x, y)] = sub
                    bottom_layer.add(self.move_tile)
        self.group.add(bottom_layer, top_layer)
        if BOOSTED:
            self.boost.rect_part.image.fill(Color("OrangeRed"))
            self.boost.txt_part.quick_msg_update(color=Color("Navy"))
            self.player._speed = self.player.speed = 0.06
    def get_tile(self, pos: Vector2) -> str|None:
        key = tuple(pos)
        if key in self.tile_map:
            return self.tile_map[key]
        else:
            return None
    def get_map(self, pos):
        return self.__Moveable.get_map(pos)
    @property
    def Map(self):
        return self.__Moveable.Map

    @property
    def switches(self):
        return self.__Switch.lst
    def execute(self):
        global BOOSTED
        running = True
        clicked = False
        while running:
            for mv in self.Map.copy().values():
                mv.get()
            clear = True
            for switch in self.switches:
                pressed = switch.check_pressed()
                if not pressed:
                    clear = False
            if clear:
                if not CLEARED[self.mode][self.level-1]:
                    CLEARED[self.mode][self.level-1] = True
                    global PT
                    PT += MODE_POINTS[self.mode]
                State.on.pop()
                FIRST_CHAN.play(SOUND_CLEAR)
                return ResultState(self.mode, self.level)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_v:
                        if not BOOSTED:
                            self.player._speed = 0.06
                    if event.key == pygame.K_x:
                        State.on.pop()
                        lev_state = State.on.pop()
                        return LevelState(lev_state.mode)
                    if event.key == pygame.K_r:
                        State.on.pop()
                        re_level = GameState(self.mode, self.level)
                        FIRST_CHAN.play(SOUND_SELECT_MAP)
                        return re_level
                    if event.key == pygame.K_b:
                        if BOOSTED:
                            BOOSTED = False
                            self.player._speed = 0.03
                            self.boost.txt_part.quick_msg_update(color=Color("LightCoral"))
                            self.boost.rect_part.image.fill(Color("Navy"))
                        else:
                            BOOSTED = True
                            self.player._speed = 0.06
                            self.boost.txt_part.quick_msg_update(color=Color("Navy"))
                            self.boost.rect_part.image.fill(Color("OrangeRed"))
                    if self.player.dir == D_c:
                        dir = D_c
                        if event.key == pygame.K_LEFT:
                            dir = D_l
                        if event.key == pygame.K_RIGHT:
                            dir = D_r
                        if event.key == pygame.K_UP:
                            dir = D_u
                        if event.key == pygame.K_DOWN:
                            dir = D_d
                        pos = self.player.pos
                        
                        try:
                            box = self.get_map(pos + dir)
                            if box.key in ["box", "icybox"] and box.dir == D_c:
                                box.set_dir(dir)
                                box._speed = box.speed = self.player.speed
                        except KeyError:
                            pass
                        self.player.set_dir(dir)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_v:
                        if not BOOSTED:
                            self.player._speed = 0.03
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = Vector2(pygame.mouse.get_pos())
                    clicked = False
                    if ESC_BUTTON.is_pressed(mouse_pos):
                        State.on.pop()
                        lev_state = State.on.pop()
                        return LevelState(lev_state.mode)
                    elif self.boost.is_pressed(mouse_pos):
                        if BOOSTED:
                            BOOSTED = False
                            self.player._speed = 0.03
                            self.boost.txt_part.quick_msg_update(color=Color("LightCoral"))
                            self.boost.rect_part.image.fill(Color("Navy"))
                        else:
                            BOOSTED = True
                            self.player._speed = 0.06
                            self.boost.txt_part.quick_msg_update(color=Color("Navy"))
                            self.boost.rect_part.image.fill(Color("OrangeRed"))
                    else:
                        clicked = True
                if event.type == pygame.MOUSEBUTTONUP and clicked:
                    clicked = False
                    change = Vector2(pygame.mouse.get_pos()) - mouse_pos
                    arg = change.angle_to(Vector2(0))
                    if self.player.dir == D_c:
                        dir = D_c
                        if 135 <= arg or arg < -135:
                            dir = D_l
                        if -45 <= arg < 45:
                            dir = D_r
                        if 45 <= arg < 135:
                            dir = D_u
                        if -135 <= arg < -45:
                            dir = D_d
                        pos = self.player.pos
                        
                        try:
                            box = self.get_map(pos + dir)
                            if box.key in ["box", "icybox"] and box.dir == D_c:
                                box.set_dir(dir)
                                box._speed = box.speed = self.player.speed
                        except KeyError:
                            pass
                        self.player.set_dir(dir)
            
            Counter.tick()
            if FIRST_CHAN.get_sound():
                SECOND_CHAN.set_volume(0)
            else:
                SECOND_CHAN.set_volume(FIRST_CHAN.get_volume())
            self.ordinary_work(SCREEN, clock, FPS)

class ResultState(State):
    def __init__(self, mode, level) -> None:
        super().__init__()
        self.background = SCREEN.copy()
        lst = [0, 1, 3, 6, 7, 8]
        clear_msg = MessageSprite(f"\"{MODE_NAME[mode]}\" - 레벨 {level}{'을' if level in lst else '를'} 클리어 했습니다!", "Black",
        Position(0, parent=SCREEN_RECT))
        self.esc = Button("홈", Position(0, 75, parent=SCREEN_RECT), Vector2(100, 50),
        render_func=simple_render_gen(20))
        self.group = Group(clear_msg, self.esc)
        if level < NUM_LEVELS[mode]:
            self.nxt = Button("다음", Position(150, 75, parent=SCREEN_RECT), Vector2(100, 50),
            render_func=simple_render_gen(20))
            self.group.add(self.nxt)
        if level > 0:
            self.bef = Button("이전", Position(-150, 75, parent=SCREEN_RECT), Vector2(100, 50),
            render_func=simple_render_gen(20))
            self.group.add(self.bef)
        self.mode = mode
        self.level = level
    def execute(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.esc.is_pressed(mouse_pos):
                        State.on.pop()
                        lev_state = State.on.pop()
                        return LevelState(lev_state.mode)
                    if hasattr(self, "nxt"):
                        if self.nxt.is_pressed(mouse_pos):
                            State.on.pop()
                            FIRST_CHAN.play(SOUND_SELECT_MAP)
                            return GameState(self.mode, self.level + 1)
                    if hasattr(self, "bef"):
                        if self.bef.is_pressed(mouse_pos):
                            State.on.pop()
                            FIRST_CHAN.play(SOUND_SELECT_MAP)
                            return GameState(self.mode, self.level - 1)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        if hasattr(self, "nxt"):
                            State.on.pop()
                            FIRST_CHAN.play(SOUND_SELECT_MAP)
                            return GameState(self.mode, self.level + 1)
                    if event.key == pygame.K_x:
                        State.on.pop()
                        lev_state = State.on.pop()
                        return LevelState(lev_state.mode)
                    if event.key == pygame.K_z:
                        if hasattr(self, "bef"):
                            State.on.pop()
                            FIRST_CHAN.play(SOUND_SELECT_MAP)
                            return GameState(self.mode, self.level - 1)
            self.ordinary_work(SCREEN, clock, FPS)

State.on = [MenuState()]
while State.on[-1]:
    SCREEN.blit(State.on[-1].background, Vector2(0))
    next_state = State.on[-1].execute()
    if next_state == "before":
        State.on.pop()
    else:
        State.on.append(next_state)