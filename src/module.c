/*
 *
 *+  Copyright (c) 2009 Ian Halpern
 *@  http://impulse.ian-halpern.com
 *
 *   This file is part of Impulse.
 *
 *   Impulse is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   Impulse is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with Impulse.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <Python.h>
#include "impulse.h"
#include <string.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

static PyObject * impulse_getSnapshot( PyObject *self, PyObject *args, PyObject *kwargs ) {
	PyObject *magnitude;

	int fft = 0;

	static char *kwlist[] = { "fft" };

	PyArg_ParseTupleAndKeywords( args, kwargs, "b", kwlist, &fft );

	magnitude = PyTuple_New( 256 );

	double *m = im_getSnapshot( fft );

	int i;
	for ( i = 0; i < 256; i++ )
		PyTuple_SetItem( magnitude, i, PyFloat_FromDouble( m[ i ] ) );

	return magnitude; // PyString_FromStringAndSize( (char *) snapshot, CHUNK );
}

static PyObject *ImpulseError;

static PyMethodDef ImpulseMethods[ ] = {
	{ "getSnapshot",  (PyCFunction)impulse_getSnapshot, METH_VARARGS | METH_KEYWORDS, "Returns the current audio snapshot from Pulseaudio." },
	{ NULL, NULL, 0, NULL }		/* Sentinel */
};

PyMODINIT_FUNC initimpulse ( void ) {
	PyObject *m;

	m = Py_InitModule( "impulse", ImpulseMethods );
	if (m == NULL)
		return;

	ImpulseError = PyErr_NewException( "impulse.error", NULL, NULL );
	Py_INCREF( ImpulseError );
	PyModule_AddObject( m, "error", ImpulseError );

	Py_AtExit( &im_stop );

	im_start( );

	return;
}

