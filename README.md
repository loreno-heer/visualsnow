# visualsnow
Programs to simulate the appearance of visual snow


# install instructions

- unzip all files in some directory (for some reason the git submodule lygia is empty, this needs to be added manually)
- install python 3.8+ and pip
- on windows you might need to install the microsoft build tools / visual c++
- run:
```
pip install moderngl
pip install moderngl-window
```
- run the program:
```
python3 ./visualsnowsim.py
```

# usage instructions
## visualsnowsim

Use the <kbd>A</kbd> and <kbd>D</kbd> keys to decrease/increase noise(snow) size.
Use the <kbd>Q</kbd> and <kbd>E</kbd> keys to decrease/increase noise(snow) brightness.
Use the <kbd>C</kbd> and <kbd>B</kbd> keys to decrease/increase the cutoff value for noise to appear (amount of noise).
Use the <kbd>T</kbd> and <kbd>U</kbd> keys to change the type of noise (resets the other parameters).
<kbd>ESC</kbd> closes the application.

## example_task

This is a simple app that displays a black screen and gradually adds noise. Press space whenever noise appears to be visible. Results are logged in a CSV file.
