# fortran-mdao
This repository demonstrates how to use compiled Fortran functions in OpenMDAO Components through ctypes. The Sellar 
problem, copied from the OpenMDAO documentation, is optimized using functions from a Fortran shared object to compute 
the functions of its two disciplines.

Building the Fortran Shared Object
----------------------------------
To run this demo, the Fortran shared object has to be build first. Since the Fortran source consists of just a single 
source file, no Makefile or CMakeLists.txt was created. Instead, simply build a shared library by issuing the following
command in the root of the repo:
```bash
gfortran -shared -fPIC -Ofast -o sellar.so sellar.f90
```
This command should yield two new files: `sellar.mod` and `sellar.so`. The latter will be used by the OpenMDAO Problem.

> Note that any other compiler than `gfortran` may also be used. 

> Note that the `-Ofast` flag is optional.

Solving the Sellar OpenMDAO Problem
-----------------------------------
The OpenMDAO Problem is defined in the `problem.py` script. Most of this code was copied from the OpenMDAO 
documentation. However, the computation of two disciplines' functions now happens in the compiled Fortran object instead
of in Python.

With the Fortran shared object built, the OpenMDAO Problem can be optimized. Simply run the `problem.py` script. 
This should produce the following output:
```
Optimization terminated successfully.    (Exit mode 0)
            Current function value: 3.1833939517810257
            Iterations: 6
            Function evaluations: 6
            Gradient evaluations: 6
Optimization Complete
-----------------------------------
minimum found at
1.3080263758977621e-14
[1.97763888 0.        ]
minumum objective
3.1833939517810257
```
> Note that the exact values of these numbers may vary from machine to machine, but they should be close to these.