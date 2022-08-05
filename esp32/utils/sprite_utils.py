import uasyncio as asyncio
import gc
from utils.screen_utils import Screen

class Sprite:

  def __init__(self, name:str = "wlan_sprites", display=None, x=15, y=10, width_height=30):
    self.name = name
    self.play_task = None
    self.display = display
    self.x = x
    self.y = y
    self.width_height = width_height


  def off(self, width_height=30, frames=4, pause_sec=0.3, play_reverse=True):
    loop = asyncio.get_event_loop()
    self.play_task = asyncio.create_task(
      self.play_sprite()
      )

  def on(self):
    try:
      self.play_task.cancel()
    except AttributeError: #type: ignore
      pass
    self.show_frame()
  
  def cancel(self):
    self.play_task.cancel()

  def show_frame(self, frame=4):
    gc.collect
    x_start = (frame-1) * self.width_height
    y_start = 0
    print(f"{x_start}, {y_start}")
    buffer, width, height = self.display.jpg_decode(f"res/{self.name}.jpg", x_start, y_start, self.width_height, self.width_height) 
    self.display.blit_buffer(buffer, self.x, self.y, width, height)
    buffer = None
    gc.collect
  
  async def play_sprite(self, frames=4, pause_sec=0.3, x=15, y=10, play_reverse=True):
      print("play_sprite started {}".format(self.name))
      i = 0
      reverse = play_reverse
      while True:
          gc.collect
          x_start = i * self.width_height # move to i'th frame
          y_start = 0
          #print(f"{i}:{x_start}")
          buffer, width, height = self.display.jpg_decode(f"res/{self.name}.jpg", x_start, y_start, self.width_height, self.width_height) 
          self.display.blit_buffer(buffer, x, y, width, height)
          buffer = None
          gc.collect
          if play_reverse:
            if reverse:
              i += 1
              if i == frames-1:
                reverse = not reverse
            else:
              i -= 1
              if i == 0:
                reverse = not reverse
          else:
            i+=1
            if i == frames:
              i=0
          await asyncio.sleep(pause_sec)

