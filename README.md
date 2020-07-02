# visualization for corewar
> __NOTE__
> the project is __not__ done !

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
to run in demo mode you can use `stdout_test_writer.py` as a source for stdin of `corewar_visual.py`:
```
$ ./stdout_test_writer.py | ./corewar_visual.py
```

on windows the command is:
```
stdout_test_writer.py | corewar_visual.py
```
