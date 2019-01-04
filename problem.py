# Copyright (c) 2019 Daniel de Vries
# This code is licensed under MIT license (see LICENSE for details)
"""This script defines and optimizes the Sellar problem using Fortran for discipline computation."""
from ctypes import byref, c_double, cdll
import numpy as np
from openmdao.api import Problem, Group, ExplicitComponent, IndepVarComp, ExecComp,\
    NonlinearBlockGS, ScipyOptimizeDriver
import os

# Load the Fortran shared object as a ctypes library
here = os.path.dirname(__file__)
lib_file = os.path.abspath(os.path.join(here, 'sellar.so'))
lib_sellar = cdll.LoadLibrary(lib_file)

# Make sure the discipline functions return c_doubles
lib_sellar.d1.restype = c_double
lib_sellar.d2.restype = c_double


def _pass(var):
    """Utility function to wrap a python float in a c_double and byref to pass it to Fortran functions."""
    return byref(c_double(var))


class D1(ExplicitComponent):
    """Definition of the first Sellar discipline Component.

    This Component computes y1 = z1**2 + z2 + x1 - 0.2*y2 using the Fortran function d1.
    """

    def setup(self):
        self.add_input('z', val=np.zeros(2))
        self.add_input('x', val=0.)
        self.add_input('y2', val=1.0)
        self.add_output('y1', val=1.0)
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        z1 = inputs['z'][0]
        z2 = inputs['z'][1]
        x1 = inputs['x']
        y2 = inputs['y2']
        outputs['y1'] = lib_sellar.d1(_pass(z1), _pass(z2), _pass(x1), _pass(y2))


class D2(ExplicitComponent):
    """Definition of the second Sellar discipline Component.

    This Component computes y2 = y1**0.5 + z1 + z2 using the Fortran function d2.
    """

    def setup(self):
        self.add_input('z', val=np.zeros(2))
        self.add_input('y1', val=1.0)
        self.add_output('y2', val=1.0)
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        z1 = inputs['z'][0]
        z2 = inputs['z'][1]
        y1 = inputs['y1']
        outputs['y2'] = lib_sellar.d2(_pass(z1), _pass(z2), _pass(y1))


class MDA(Group):
    """Definition of the Sellar Multi-Disciplinary Analysis (MDA) Group."""

    def setup(self):
        indeps = self.add_subsystem('indeps', IndepVarComp(), promotes=['*'])
        indeps.add_output('x', 1.0)
        indeps.add_output('z', np.array([5.0, 2.0]))

        cycle = self.add_subsystem('cycle', Group(), promotes=['*'])
        cycle.add_subsystem('D1', D1(), promotes=['*'])
        cycle.add_subsystem('D2', D2(), promotes=['*'])
        cycle.nonlinear_solver = NonlinearBlockGS()

        self.add_subsystem('F', ExecComp('f = x**2 + z[1] + y1 + exp(-y2)',
                                         z=np.array([0.0, 0.0]), x=0.0), promotes=['*'])

        self.add_subsystem('G1', ExecComp('g1 = 3.16 - y1'), promotes=['*'])
        self.add_subsystem('G2', ExecComp('g2 = y2 - 24.0'), promotes=['*'])


if __name__ == '__main__':
    # Setup and optimize the Sellar OpenMDAO Problem
    prob = Problem()
    prob.model = MDA()
    prob.driver = ScipyOptimizeDriver()

    prob.driver.options['optimizer'] = 'SLSQP'
    prob.driver.options['tol'] = 1e-8

    prob.model.add_design_var('x', lower=0, upper=10)
    prob.model.add_design_var('z', lower=0, upper=10)
    prob.model.add_objective('f')
    prob.model.add_constraint('g1', upper=0)
    prob.model.add_constraint('g2', upper=0)

    prob.setup()
    prob.set_solver_print(level=0)

    prob.model.approx_totals()

    prob.run_driver()

    print('minimum found at')
    print(prob['x'][0])
    print(prob['z'])

    print('minumum objective')
    print(prob['f'][0])
