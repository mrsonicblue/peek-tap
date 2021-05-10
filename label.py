import displayio

class Label(displayio.TileGrid):
    def __init__(self, bitmap: displayio.Bitmap, *, pixel_shader: Union[ColorConverter, Palette],
        font_maps: list = [], text: str = "",
        width: int = 1, height: int = 1,
        tile_width: int = 1, tile_height: int = 1,
        x: int = 0, y: int = 0
    ):
        super().__init__(bitmap=bitmap, pixel_shader=pixel_shader, width=width, height=height, tile_width=tile_width, x=x, y=y)
        self.font_maps = font_maps
        self._text = text
        self.width = width
        self.height = height

        self.render_text()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self.render_text()

    def render_text(self):
        ts = len(self._text)
        i = 0
        map = 0
        y = 0
        while y < self.height:
            x = 0
            while x < self.width:
                if i < ts:
                    while True:
                        c = ord(self._text[i])
                        i += 1
                        if c == 10: # newline
                            if x > 0:
                                y += 1
                                x = 0
                        elif c < 10: # switch font
                            map = c
                        else:
                            break # render character

                    if y >= self.height:
                        break

                    if c in self.font_maps[map]:
                        self[x, y] = self.font_maps[map][c]
                    else:
                        self[x, y] = 0
                else:
                    self[x, y] = 0
                x += 1
            y+=1