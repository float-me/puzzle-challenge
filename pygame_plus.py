import pygame
from pygame import Surface, Vector2
from pygame.sprite import Group, Sprite
from typing import List
from typing_extensions import Self
from itertools import zip_longest

import os

__all__ = [
    "AnimatedSprite", "Counter", "Position", "State", "imgload", "animeload", "get_font", "resize_rate", "resize_size",
    "LOCATION_MAP"
]

NoneType = type(None)

def imgload(filename: str) -> List[Surface]:
    """
    파일명으로 이미지를 로드하는 함수입니다.
    """
    img = pygame.image.load(f"./img/{filename}")
    return img.convert_alpha()

def animeload(foldername: str) -> List[Surface]:
    """
    폴더명으로 애니메이션을 로드하는 함수입니다.
    """
    return [imgload(f"{foldername}/{file}") for file in os.listdir(f"./img/{foldername}")]

rescale = pygame.transform.scale
def resize_rate(image: Surface, rate: float):
    return rescale(image, Vector2(image.get_size())*rate)

def resize_size(image: Surface, x_size: int|float):
    x, _ = image.get_size()
    return resize_rate(image, x_size/x)

def get_font(size: int|float, fontname:str ="EF_Rebecca(윈도우용_TTF)") -> pygame.font.Font:
    """
    폰트명으로 font 폴더 내의 폰트를 로드하여 pygame.font.Font 객체를 생성하는 함수입니다.
    기본 폰트는 EF_Rebecca(윈도우용_TTF)입니다.
    """
    return pygame.font.Font(f"./fonts/{fontname}.ttf", int(size))

class Counter:
    """
    수를 세주는 클래스입니다. 카운트가 n이 되면 다시 0으로 초기화됩니다.

    Args:
        n: 카운트 한계
        init: 초기 카운트
        mult: 1 카운트가 올라가는 프레임 수
        _sub_init: 카운트를 뺀 초기값의 프레임 수
    """
    _arr: List[Self] = []
    def __init__(self, n: int, init: int=0, mult: int=1, _sub_init: int=0) -> None:
        self.count = init
        self._sub_count = _sub_init
        self._mult = mult
        self._n = n
        Counter._arr.append(self)
    def flip(self) -> bool:
        """
        개별적인 수 세기 함수입니다. 카운트가 n에 도달했는지 여부를 return합니다.
        """
        self._sub_count += 1
        if self._sub_count == self._mult:
            self._sub_count = 0
            self.count += 1
            if self.count == self._n:
                self.count = 0
                return True
        return False
    def tick() -> None:
        """
        일괄적인 수 세기 함수입니다.
        """
        for counter in Counter._arr:
            counter.flip()

class Position:
    def __init__(self, *args, parent: NoneType|Self|pygame.Rect|Surface|Sprite=None, positional_relation="center",
    animated=False, init: int=0, mult: int=1, _sub_init: int=0):
        if animated:
            self._positions = [Vector2(v) for v in args]
        else:
            self._positions = [Vector2(*args)]
        self.parent = parent
        self._positional_relation = positional_relation
        self._counter = Counter(len(self._positions), init, mult, _sub_init)
    @property
    def pure_position(self):
        return self._positions[self._counter.count]
    def __add__(self, other: Vector2):
        new = self.copy()
        new._positions = [position + other for position in new._positions]
        return new
    def copy(self) -> Self:
        return Position(*self._positions[:], parent=self.parent, positional_relation=self._positional_relation,
        animated=True, init=self._counter.count, mult=self._counter._mult, _sub_init=self._counter._sub_count)
    @property
    def position(self):
        position = self.pure_position
        if self.parent == None:
            return position
        if isinstance(self.parent, pygame.Rect):
            parent_position = getattr(self.parent, self._positional_relation)
            return position + parent_position
        if isinstance(self.parent, Surface):
            parent_position = getattr(self.parent.get_rect(), self._positional_relation)
            return position + parent_position
        if isinstance(self.parent, Sprite):
            parent_position = getattr(self.parent.rect, self._positional_relation)
            return position + parent_position
        return position + self.parent.position

class AnimatedSprite(Sprite):
    def __init__(self, position: Position, images: Surface|List[Surface], init: int=0, mult: int=1, _sub_init: int=0,
    positional_relation="center") -> None:
        super().__init__()
        if isinstance(images, Surface):
            images = [images]
        self._images = images
        self._position_getter = position
        self._positional_relation = positional_relation
        self._counter = Counter(len(images), init, mult, _sub_init)
    @property
    def image(self):
        return self._images[self._counter.count]
    @image.setter
    def image(self, val: Surface|List[Surface]):
        if isinstance(val, Surface):
            val = [val]
        self._images = val
        self._counter = Counter(len(self._images))
    def set_image(self, val: Surface|List[Surface], init: int=0, mult: int=1, _sub_init: int=0):
        self.image = val
        self._counter = Counter(len(self._images), init, mult, _sub_init)
    @property
    def rect(self):
        r = self.image.get_rect()
        setattr(r, self._positional_relation, self.position)
        return r
    @property
    def position(self):
        return self._position_getter.position
    def move(self, *args, animated=False):
        if animated:
            for p, v in zip_longest(self._position_getter._positions, args, fillvalue=args[-1]):
                p += v
        else:
            self._position_getter._positions[0] += pygame.Vector2(*args)
    def update(self) -> None:
        pass

class State:
    on: List[Self] = []
    def execute(self):
        pass
    def _execute(self, SCREEN, clock, FPS):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        return "before"
            self.ordinary_work(SCREEN, clock, FPS)

    def ordinary_work(self, SCREEN: pygame.Surface, clock: pygame.time.Clock, FPS: int):
        self.group: Group
        self.background: pygame.Surface

        # self.group 그룹안에 든 모든 Sprite update
        self.group.update()
        # 모든 sprite 화면에 그려주기
        self.group.draw(SCREEN)
        pygame.display.update()

        self.group.clear(SCREEN, self.background)

        clock.tick(FPS)

LOCATION_MAP = {(0, -3): 'box_bright', (3, -1): 'box_dark', (0, 0): 'map1-1', (0, -1): 'map1-2', (0, -2): 'map1-3', (1, -2): 'map1-4', (1, -3): 'map2-1', (2, -3): 'map2-2', (3, -3): 'map2-3', (4, -3): 'map2-4', (5, -3): 'map2-5', (5, -2): 'map3-1', (5, -1): 'map3-2', (4, -1): 'map3-3', (4, 0): 'map3-4', (3, 0): 'map3-5', (6, -1): 'map3-6', (6, 0): 'map3-7', (2, 0): 'map4-1', (2, 1): 'map4-2', (1, 0): 'map4-3', (1, 1): 'map4-4'}
