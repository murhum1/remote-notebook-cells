from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
import shelve
import time
import dill
import subprocess

pre_code = """
import shelve
import dill

___in_shelf = shelve.open('in.txt')
for key in ___in_shelf:
    globals()[key]=___in_shelf[key]
___in_shelf.close()
"""

post_code = """
___variables = vars()
___f = shelve.open('out.txt')
for key in dir():
    try:
        if (dill.pickles(___variables[key]) and key != '___f'):
            ___f[key] = ___variables[key]
    except Exception as e:
        pass
        #print(e)
        #print('ERROR shelving: {0}'.format(key))
___f.close()
"""

# The class MUST call this class decorator at creation time
@magics_class
class GPU(Magics):

    @cell_magic
    def GPUCell(self, line, cell):
        
        var_names = list(self.shell.user_ns.keys())
        var_dir = self.shell.user_ns

        print("Saving current environment... ")
        f = shelve.open('in.txt')
        for key in var_names:
            try:
                if (dill.pickles(var_dir[key]) and key != 'f'):
                    f[key] = var_dir[key]
            except Exception as e:
                #
                # __builtins__, my_shelf, and imported modules can not be shelved.
                #
                # print('ERROR shelving: {0}'.format(key))
                pass
        f.close()
        with open('tmp.py', 'w') as tmp:
            tmp.writelines(pre_code)
            tmp.writelines(cell)
            tmp.writelines(post_code)

        print("Executing GPU code.")
        p = subprocess.Popen(['python', 'tmp.py'], stdout=subprocess.PIPE)
        while True:
            output = p.stdout.readline()
            if output == '' and p.poll() is not None:
                break
            if output:
                print(output.strip())
            p.poll()
        ___out_shelf = shelve.open('out.txt')
        for key in ___out_shelf:
            self.shell.user_ns[key] = ___out_shelf[key]
        ___out_shelf.close()
        return

def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    ipython.register_magics(GPU)
