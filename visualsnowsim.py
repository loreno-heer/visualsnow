# Copyright (c) 2023 Loreno Heer.
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import math
import moderngl_window
import random
import moderngl
import numpy as np
import logging

from pathlib import Path

from moderngl_window import resources


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
        self.prog = self.load_program('snowshader.glsl')
        vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0])
        self.vbo = self.ctx.buffer(vertices.astype('f4'))
        self.vao = self.ctx.vertex_array(self.prog,self.vbo, 'in_vert')

        u_size = self.prog['u_size']
        u_size.value = 1.0
        
        u_bright = self.prog['u_bright']
        u_bright.value = 0.1

        u_noisetype = self.prog['u_noisetype']
        u_noisetype.value = 1

        u_cutoff = self.prog['u_cutoff']
        u_cutoff.value = 0.9
        

    def render(self, time: float, frametime: float):
        u_time = self.prog["u_time"]
        u_time.value = time
        
        # need to pass resolution. use window size (which is probably wrong but should not matter in full screen)
        u_resolution = self.prog["u_resolution"]
        u_resolution.value = self.window_size
        
        self.ctx.clear(0.0,0.0,0.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)

    def snowtype_defaults(self):
        """those are the defaults that work on my monitor and produce snow that is most similar to the condition
           values likely need to be changed significantly for different GPU and monitor
        """
        u_size = self.prog['u_size']
        u_bright = self.prog['u_bright']
        u_cutoff = self.prog['u_cutoff']

        noisetype = self.prog['u_noisetype'].value

        if noisetype == 0:
            u_size.value,u_bright.value,u_cutoff.value=1.0,0.1,0.8
        elif noisetype == 1:
            u_size.value,u_bright.value,u_cutoff.value=1.0,0.1,0.9
        elif noisetype == 2:
            u_size.value,u_bright.value,u_cutoff.value=20.4,0.02,0.7
        elif noisetype == 3:
            u_size.value,u_bright.value,u_cutoff.value=10.0,0.05,0.8
        elif noisetype == 4:
            u_size.value,u_bright.value,u_cutoff.value=10.6,0.03,0.9
        elif noisetype == 5: #for simulating flashing lights
            u_size.value,u_bright.value,u_cutoff.value=1.0,0.1,0.8
        elif noisetype == 6: # slow noise
            u_size.value,u_bright.value,u_cutoff.value=9.0,0.01,0.3
        elif noisetype == 7: 
            u_size.value,u_bright.value,u_cutoff.value=14.8,0.01,0.8
        elif noisetype == 8: 
            u_size.value,u_bright.value,u_cutoff.value=6.6,0.02,0.8
        elif noisetype == 9: 
            u_size.value,u_bright.value,u_cutoff.value=4.1,0.01,0.9
        elif noisetype == 10: 
            u_size.value,u_bright.value,u_cutoff.value=1.0,0.1,0.8

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
            # Snow size keys
            if key == keys.A:
                self.prog['u_size'].value = max(self.prog['u_size'].value - 0.1, 1.0)
            if key == keys.D:
                self.prog['u_size'].value = self.prog['u_size'].value + 0.1

            # Brightness keys
            if key == keys.Q:
                self.prog['u_bright'].value = max(self.prog['u_bright'].value - 0.01, 0.0)
            if key == keys.E:
                self.prog['u_bright'].value = min(self.prog['u_bright'].value + 0.01, 1.0)

            # Noise type keys
            if key == keys.T:
                self.prog['u_noisetype'].value = max(self.prog['u_noisetype'].value - 1,0)
            if key == keys.U:
                self.prog['u_noisetype'].value = min(self.prog['u_noisetype'].value + 1,10)
            if key == keys.T or key == keys.U:
                # Initialize default values for snow type
                self.snowtype_defaults()

            # Cutoff point for the noise to appear
            if key == keys.C:
                self.prog['u_cutoff'].value = max(self.prog['u_cutoff'].value - 0.1, 0.0)
            if key == keys.B:
                self.prog['u_cutoff'].value = min(self.prog['u_cutoff'].value + 0.1, 1.0)
                
            self.print_noisesettings()




if __name__ == '__main__':
    moderngl_window.run_window_config(VisualSnowSim)
