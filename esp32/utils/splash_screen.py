from machine import Pin, SoftSPI
try:
    import st7789
    import meteo as font 
    from st7789 import WHITE, BLACK

except ImportError as e: # type: ignore
    print("import error: " + e)


class Display:
    """
    Everything here is prefilled for TTGO-T-Display. Modularity is possible with BoardConfig,
    but loading time is more important right now.
    """
    def __init__(self):
        self.progress_last = (0,100) # progress, max_progress
        spi = SoftSPI(baudrate=20000000, polarity=0,  sck=Pin(18), mosi=Pin(19), miso=Pin(2)) # Pin 2 is not really used
        w=240
        h=135
        self.display = st7789.ST7789(
            spi, h, w,
            cs = Pin(5, Pin.OUT),
            backlight = Pin(4, Pin.OUT),
            reset=Pin(23, Pin.OUT),
            dc=Pin(16, Pin.OUT),
            rotation=1
        )
        self.display.init()
        
    def splash_screen(self):
        """fast loading for just the start-screen"""
        # import scriptc as font
        self.display.draw(font,"Erika",65,50, WHITE, 1.5)
        self.display.draw(font,"electronic",65,85, WHITE, 0.8)

    def show_progress(self, progress=0, max=100, y_from=100, bar_height=10):
       
        progress_last, max_last = self.progress_last
        redraw=False
        if max_last != max:
                progress_last = round(max/max_last)
                redraw = True

        margin = 20
        tft=self.display
        tft_width = tft.width()
        progress_filled_width = round((tft_width - 2*margin) / max * progress)
        progress_filled_width_last = round((tft_width - 2*margin) / max * progress_last)

        print(f"{progress}:{progress_filled_width}")
        
        if redraw:
                print(f"redrawing: {max_last}:{max}")
                reset_rect = (margin+1, #x
                        y_from+1, #y
                        tft_width-margin-1, #width
                        bar_height-1, #height
                        BLACK)
                tft.fill_rect(*reset_rect)
                white_rect = (progress_filled_width_last+margin, #x
                        y_from, #y
                        progress_filled_width-progress_filled_width_last, #width
                        bar_height, #height
                        WHITE)
                tft.fill_rect(*white_rect)
        elif progress_last <= progress:
            white_rect = (progress_filled_width_last+margin, #x
                        y_from, #y
                        progress_filled_width-progress_filled_width_last, #width
                        bar_height, #height
                        WHITE)
            print("white_rect", white_rect)
            tft.fill_rect(*white_rect)

        elif progress_last > progress:
            fill_black_width = progress_filled_width_last - progress_filled_width + margin
            black_rect = (progress_filled_width, #x
                        y_from, #y
                        fill_black_width, #width
                        bar_height, #height
                        BLACK) # color
            print("black_rect", black_rect)
            tft.fill_rect(*black_rect) # color

        #rect(x, y, width, height, color)
        tft.rect(margin, y_from, tft_width-2*margin, bar_height, WHITE) # outer rect
        self.progress_last = progress, max