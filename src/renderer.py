import pygame

import settings
from background import load_background
from buttons import (
    BACK_TOP,
    BTN_HOVER,
    BTN_NORMAL,
    BTN_PRESSED,
    BUTTON_FONT,
    BUTTON_SIZE,
    centered_button_rect,
    make_button,
)
from entities import Platform, level_platforms
from pixelart import nine_slice
from world import GameWorld

CARD_BORDER = 20  # px of the card frame art that keep their pixels
CARD_LIFT = 6  # a hovered card is drawn this much higher
THUMB_MARGIN = 24  # a card's preview is inset this far from its sides
PLATE_EDGE = 2  # border width of the HUD plates
TOP_HUD_HEIGHT = 34  # the score plates and level name at the top of the screen
TAG_RISE = 50  # a role tag's top is this far above its player's sprite
CARD_SIZE = (240, 210)  # a level-select card


class GameRenderer:
    def __init__(self, window: pygame.Surface, world: GameWorld) -> None:
        self._window = window
        self._world = world
        self._size = (world.window_w, world.window_h)

        self._grounds: dict[str, Platform] = {}
        self._thumbs: dict[tuple[int, int], pygame.Surface] = {}
        self._card = pygame.image.load("assets/images/ui/card.png").convert_alpha()
        self._card_frames: dict[tuple[int, int], pygame.Surface] = {}

        self._back_rect = centered_button_rect(BACK_TOP)
        self._back_buttons = {
            state: make_button(state, BUTTON_SIZE, "BACK", BUTTON_FONT)
            for state in (BTN_NORMAL, BTN_PRESSED, BTN_HOVER)
        }

        self._font_sm = pygame.font.Font(settings.UI_FONT, 16)
        self._font_title = pygame.font.Font(settings.TITLE_FONT, 72)

        self._lbl_vampire = self._font_sm.render("VAMPIRE", False, settings.HP_RED)
        self._lbl_peasant = self._font_sm.render("PEASANT", False, settings.HP_GREEN)

    # ------------------------------------------------------------------ helpers

    def _ground(self, style: str) -> Platform:
        ground = self._grounds.get(style)
        if ground is None:
            ground = self._grounds[style] = Platform(
                (0, settings.GROUND_Y),
                self._world.window_w,
                int(self._world.window_h - settings.GROUND_Y),
                style=style,
                kind="ground",
            )
        return ground

    def _plate(self, rect: pygame.Rect, edge: tuple[int, int, int]) -> None:
        pygame.draw.rect(self._window, settings.INK, rect)
        pygame.draw.rect(self._window, edge, rect, PLATE_EDGE)

    def _text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        center: tuple[int, int],
        shadow: tuple[int, int, int] | None = settings.INK,
        drop: int = 2,
    ) -> None:
        """Pixel text centered on `center`, with a hard drop shadow."""
        face = font.render(text, False, color)
        rect = face.get_rect(center=center)
        if shadow is not None:
            self._window.blit(font.render(text, False, shadow), rect.move(drop, drop))
        self._window.blit(face, rect)

    # ------------------------------------------------------------------ game

    def draw_game(self, p1, p2, vampire, current_level: int, score_surfs) -> None:
        level = settings.LEVELS[current_level]
        self._window.blit(load_background(level["background"], self._size), (0, 0))
        self._ground(level["style"]).draw(self._window)

        for plat in self._world.platforms:
            plat.draw(self._window)
        for bullet in self._world.bullets:
            bullet.draw(self._window)

        self._draw_sprite_hud(p1, vampire)
        if p2 is not None:
            self._draw_sprite_hud(p2, vampire)

        self._draw_top_hud(p1, p2, current_level, score_surfs)

    def _draw_sprite_hud(self, player, vampire) -> None:
        ix, iy = int(player.x), int(player.y)
        self._draw_role_tag(player, ix, iy, vampire)
        self._draw_health_bar(player, ix, iy)
        player.draw(self._window)

    def _draw_role_tag(self, player, ix, iy, vampire) -> None:
        is_vampire = vampire is player
        role_lbl = self._lbl_vampire if is_vampire else self._lbl_peasant
        tag = pygame.Rect(0, 0, role_lbl.get_width() + 10, role_lbl.get_height() + 6)
        tag.midtop = (ix + player.width // 2, iy - TAG_RISE)
        self._plate(tag, settings.PLUM)
        self._window.blit(role_lbl, role_lbl.get_rect(center=tag.center))

    def _draw_health_bar(self, player, ix, iy) -> None:
        bar_w, bar_h = 52, 7
        bar_x = ix + (player.width - bar_w) // 2
        bar_y = iy - 12
        pct = max(0.0, player.hp / player.max_hp)
        fill = int((bar_w - 2) * pct)
        hp_color = (
            settings.HP_GREEN
            if pct > 0.5
            else (settings.HP_YELLOW if pct > 0.25 else settings.HP_RED)
        )
        pygame.draw.rect(self._window, settings.INK, (bar_x, bar_y, bar_w, bar_h))
        if fill > 0:
            pygame.draw.rect(
                self._window, hp_color, (bar_x + 1, bar_y + 1, fill, bar_h - 2)
            )
        pygame.draw.rect(self._window, settings.RIM, (bar_x, bar_y, bar_w, bar_h), 1)

    def _draw_top_hud(self, p1, p2, current_level: int, score_surfs) -> None:
        pad, panel_h = 10, TOP_HUD_HEIGHT

        p1_surf = score_surfs[0]
        p1_rect = pygame.Rect(0, 0, p1_surf.get_width() + pad * 2, panel_h)
        self._plate(p1_rect, settings.SLATE)
        self._window.blit(p1_surf, p1_surf.get_rect(center=p1_rect.center))

        if p2 is not None:
            p2_surf = score_surfs[1]
            p2_w = p2_surf.get_width() + pad * 2
            p2_rect = pygame.Rect(self._world.window_w - p2_w, 0, p2_w, panel_h)
            self._plate(p2_rect, settings.CRIMSON)
            self._window.blit(p2_surf, p2_surf.get_rect(center=p2_rect.center))

        name = settings.LEVELS[current_level]["name"].upper()
        self._text(name, self._font_sm, settings.RIM, (self._world.window_w // 2, 18))

    # ------------------------------------------------------------ level select

    def back_rect(self) -> pygame.Rect:
        """The level select's BACK button."""
        return self._back_rect

    def draw_level_select(self, pos, pressed: bool = False) -> None:
        """The level select; `pressed` is whether the mouse button is down (for BACK)."""
        self._window.blit(load_background(settings.MENU_BACKGROUND, self._size), (0, 0))

        self._text(
            "Select Level",
            self._font_title,
            settings.RIM,
            (self._world.window_w // 2, 90),
            shadow=settings.CRIMSON,
            drop=3,
        )

        for i, lvl in enumerate(settings.LEVELS):
            rect = self.level_card_rect(i)
            hovered = rect.collidepoint(pos)
            if hovered:
                rect = rect.move(0, -CARD_LIFT)
            self._window.blit(self._card_frame(rect.size), rect)

            self._text(
                f"LEVEL {i + 1}",
                self._font_sm,
                settings.BONE,
                (rect.centerx, rect.y + 34),
            )
            self._text(
                lvl["name"].upper(),
                self._font_sm,
                settings.RIM,
                (rect.centerx, rect.y + 54),
            )
            thumb = self._thumb(i, rect.w - 2 * THUMB_MARGIN)
            thumb_rect = thumb.get_rect(midtop=(rect.centerx, rect.y + 74))
            self._window.blit(thumb, thumb_rect)
            pygame.draw.rect(self._window, settings.INK, thumb_rect.inflate(4, 4), 2)

            if hovered:
                self._text(
                    "CLICK TO PLAY",
                    self._font_sm,
                    settings.GOLD,
                    (rect.centerx, rect.bottom + 22),
                )

        hovered = self._back_rect.collidepoint(pos)
        state = (
            BTN_PRESSED if hovered and pressed else BTN_HOVER if hovered else BTN_NORMAL
        )
        self._window.blit(self._back_buttons[state], self._back_rect)

    def _card_frame(self, size: tuple[int, int]) -> pygame.Surface:
        frame = self._card_frames.get(size)
        if frame is None:
            frame = self._card_frames[size] = nine_slice(self._card, CARD_BORDER, size)
        return frame

    def _thumb(self, level: int, width: int) -> pygame.Surface:
        """A level's whole scene (backdrop, ground, platforms) scaled to a card's preview."""
        thumb = self._thumbs.get((level, width))
        if thumb is None:
            lvl = settings.LEVELS[level]
            scene = load_background(lvl["background"], self._size).copy()
            self._ground(lvl["style"]).draw(scene)
            for plat in level_platforms(level):
                plat.draw(scene)
            height = width * self._world.window_h // self._world.window_w
            thumb = self._thumbs[(level, width)] = pygame.transform.scale(
                scene, (width, height)
            )
        return thumb

    def level_card_rect(self, i: int) -> pygame.Rect:
        n = len(settings.LEVELS)
        cw, ch = CARD_SIZE
        gap = 25
        total_w = n * cw + (n - 1) * gap
        start_x = (self._world.window_w - total_w) // 2
        return pygame.Rect(
            start_x + i * (cw + gap), (self._world.window_h - ch) // 2, cw, ch
        )
