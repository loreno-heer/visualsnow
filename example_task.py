import math
import moderngl_window
import random
import moderngl
import numpy as np
import logging
import csv


from pathlib import Path

from moderngl_window import resources
from moderngl_window.utils.scheduler import Scheduler


## BUGFIX resource handling in moderngl_window library
from moderngl_window.opengl.program import *
import re
def handle_includes(self, load_source_func, depth=0, source_id=0):
        """Inject includes into the shader source.
        This happens recursively up to a max level in case the users has
        circular includes. We also build up a list of all the included
        sources in the root shader.

        Args:
            load_source_func (func): A function for finding and loading a source
            depth (int): The current include depth (increase by 1 for every call)
        """
        if depth > 100:
            raise ShaderError(
                "Reaching an include depth of 100. You probably have circular includes"
            )

        current_id = source_id
        while True:
            for nr, line in enumerate(self._lines):
                line = line.strip()
                if line.startswith("#include"):
                    path = re.search(r'#include\s+"?([^"]+)',line)[1]
                    current_id += 1
                    _, source = load_source_func(path)
                    source = ShaderSource(
                        None,
                        path,
                        source,
                        defines=self._defines,
                        id=current_id,
                        root=False,
                    )
                    source.handle_includes(
                        load_source_func, depth=depth + 1, source_id=current_id
                    )
                    self._lines = self.lines[:nr] + source.lines + self.lines[nr + 1:]
                    self._source_list += source.source_list
                    current_id = self._source_list[-1].id
                    break
            else:
                break

# monkey patch
moderngl_window.opengl.program.ShaderSource.handle_includes = handle_includes

MAX_SAMPLES = 10

        
global part_id 
global session_id

class VisualSnowSim(moderngl_window.WindowConfig):
    """
    Demonstrates handling mouse, keyboard, render and resize events
    """
    gl_version = (3, 3)
    title = "Visual Snow Simulator"
    cursor = False
    vsync = True
    fullscreen = True
    aspect_ratio = None
    #log_level = logging.DEBUG

    # Workaround for incomlete include handling in moderngl_window
    resources.register_program_dir((Path(__file__) / '../shaders/lygia/math').resolve())
    resources.register_program_dir((Path(__file__) / '../shaders/lygia/generative').resolve())
    resources.register_program_dir((Path(__file__) / '../shaders').resolve())
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.wnd.exit_key = None

        self.part_id = part_id
        self.session_id = session_id
        self.outfile_name = "sampledata-" + self.part_id + "-" + self.session_id + ".csv"
        with open(self.outfile_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(["Participant ID", "Session ID", "Noisetype", "Brightness", "Cutoff", "Size"])
        

        self.scheduler = Scheduler(self.timer)

        
        self.prog = self.load_program('snowshader.glsl')
        vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0])
        self.vbo = self.ctx.buffer(vertices.astype('f4'))
        self.vao = self.ctx.vertex_array(self.prog,self.vbo, 'in_vert')

        u_size = self.prog['u_size']
        u_size.value = 1.0
        
        u_bright = self.prog['u_bright']
        u_bright.value = 0.0

        u_noisetype = self.prog['u_noisetype']
        u_noisetype.value = 1

        u_cutoff = self.prog['u_cutoff']
        u_cutoff.value = 0.9

        self.samples_count = 0

        self.brightness_change_event = self.scheduler.run_every(self.change_brightness, 0.01)

    def change_brightness(self):
        u_bright = self.prog['u_bright']
        u_bright.value = min(u_bright.value + 0.0001,1.0)
        
        if u_bright.value == 1.0:
                self.scheduler.cancel(self.color_changing_event)

    def render(self, time: float, frametime: float):
        self.scheduler.execute()
        u_time = self.prog["u_time"]
        u_time.value = time
        
        # need to pass resolution. use window size (which is probably wrong but should not matter in full screen)
        u_resolution = self.prog["u_resolution"]
        u_resolution.value = self.window_size
        
        self.ctx.clear(0.0,0.0,0.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)



    def print_noisesettings(self):
        u_noisetype = self.prog['u_noisetype']
        u_size = self.prog['u_size']
        u_bright = self.prog['u_bright']
        u_cutoff = self.prog['u_cutoff']

        print("Noisetype: ", u_noisetype.value)
        print("Noise Size: ", u_size.value)
        print("Brightness: ", u_bright.value)
        print("Cutoff value: ", u_cutoff.value)

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys


        if action == keys.ACTION_PRESS:
            
            if key == keys.SPACE:
                print("Space key pressed")
                self.print_noisesettings()
                self.scheduler.cancel(self.brightness_change_event)
                

                with open(self.outfile_name, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows([self.part_id, self.session_id, str(self.prog['u_noisetype'].value), str(self.prog['u_bright'].value), str(self.prog['u_cutoff'].value), str(self.prog['u_size'].value)])

                self.prog['u_bright'].value = 0.0
                self.samples_count = self.samples_count + 1
                if self.samples_count == MAX_SAMPLES:
                    self.close()
                else:
                    self.brightness_change_event = self.scheduler.run_every(self.change_brightness, 0.01)
        


if __name__ == '__main__':
    print("Press the SPACE key whenever you can see noise (different from own visual snow) appear on the screen")
    part_id = input("Participant ID: ")
    session_id = input("Session ID: ")
    moderngl_window.run_window_config(VisualSnowSim)
    
