# visualization for corewar

visualization is implemented in __python 3__ 
using [pyside2](https://pypi.org/project/PySide2/) - Qt framework port for python

![image](https://user-images.githubusercontent.com/58115884/129872533-d0f99ca5-3ef6-4181-b9db-dabc5e3747b7.png)

# installing dependencies
```
$ pip install pyside2
```

# running visualization
to run the visualizer use:
```
$ corewar_visual.py
```
but usually you need something like:
```
$ ./corewar batman.cor | ./corewar_visual.py
```
or
```
$ ./corewar batman.cor | python3 corewar_visual.py
```
as `corewar_visual.py` expects data from `corewar` on its `stdin`

# demo
to run in demo mode you can use `vm_output_emu.py` as a source for stdin of `corewar_visual.py`:
```
$ ./vm_output_emu.py | ./corewar_visual.py
```

on windows the command is:
```
python vm_output_emu.py | python corewar_visual.py
```
