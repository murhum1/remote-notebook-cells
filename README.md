# remote-notebook-cells
PoC for executing Jupyter notebook cells remotely, e.g. to run a single cell on a GPU machine

The example defines a jupyter cell magic `GPUCell` in `GPU.py`, which
1) saves as much as possible of the notebook's state
2) imports the state and runs the GPU cell in its own python process - this could be for example a remote python process or anything
3) saves the remote state and imports it in the original notebook
