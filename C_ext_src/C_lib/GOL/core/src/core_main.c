#define PY_SSIZE_T_CLEAN
#include <numpy/ndarrayobject.h>
#include <Python.h>
#include <stdio.h>
#include <time.h>
#include "array_operations.h"
#include "multithread.h"

static PyObject* GOL_init(PyObject* self, PyObject* args) {
	Py_RETURN_NONE;
}


static PyObject* GOL_step_NpArr(PyObject* self, PyObject* args) {

	PyObject* inputOb;
	if (!PyArg_ParseTuple(args, "O", &inputOb)) {
		PyErr_SetString(PyExc_TypeError, "Input must be a numpy array");
		return NULL;
	}
	//printf("Input parsed, inputOb: %p\n", inputOb);
	if(!PyArray_Check(inputOb)) {
		//printf("Input is not a numpy array\n");
		PyErr_SetString(PyExc_TypeError, "Input must be a numpy array");
		return NULL;
	}
	Py_INCREF(inputOb);
	PyArrayObject* input = PyArray_FromArray((PyArrayObject*)inputOb, PyArray_DescrFromType(NPY_INT8), 
		NPY_ARRAY_C_CONTIGUOUS | NPY_ARRAY_ALIGNED | 
		NPY_ARRAY_WRITEABLE | NPY_ARRAY_FORCECAST);
	//printf("Input converted to numpy array\n");
	
	if (input == NULL) {
		PyErr_SetString(PyExc_TypeError, "Unable to convert input to numpy array");
		return NULL;
	}
	//printf("Input converted and checked\n");

	// Check that input is a 2D array of uint8s
	if (PyArray_NDIM(input) != 2) {
		PyErr_SetString(PyExc_TypeError, "Input must be a 2D array");
		return NULL;
	}
	if (PyArray_TYPE(input) != NPY_INT8) {
		PyErr_SetString(PyExc_TypeError, "Input must be a 2D array of uint8s");
		return NULL;
	}
	if (PyArray_DIM(input, 0) < 3) {
		PyErr_SetString(PyExc_ValueError, "Input must have at least 3 rows");
		return NULL;
	}
	if (PyArray_DIM(input, 1) < 3) {
		PyErr_SetString(PyExc_ValueError, "Input must have at least 3 columns");
		return NULL;
	}

	uint8_t* arr = (uint8_t*)PyArray_DATA(input);
	npy_intp* dims = PyArray_DIMS(input);

	// Get the strides of the input array
	npy_intp* strides = PyArray_STRIDES(input);
	
	calculate_next_step(arr, dims, strides);
	Py_DECREF(inputOb);
	//Py_DECREF(input);
	return input;
	
}


static PyObject* GOL_step_NpArr_multithread(PyObject* self, PyObject* args) {

	PyObject* inputOb;
	if (!PyArg_ParseTuple(args, "O", &inputOb)) {
		PyErr_SetString(PyExc_TypeError, "Input must be a numpy array");
		return NULL;
	}
	//printf("Input parsed, inputOb: %p\n", inputOb);
	if(!PyArray_Check(inputOb)) {
		//printf("Input is not a numpy array\n");
		PyErr_SetString(PyExc_TypeError, "Input must be a numpy array");
		return NULL;
	}
	Py_INCREF(inputOb);
	PyArrayObject* input = PyArray_FromArray((PyArrayObject*)inputOb, PyArray_DescrFromType(NPY_INT8), 
		NPY_ARRAY_C_CONTIGUOUS | NPY_ARRAY_ALIGNED | 
		NPY_ARRAY_WRITEABLE | NPY_ARRAY_FORCECAST);
	//printf("Input converted to numpy array\n");
	
	if (input == NULL) {
		PyErr_SetString(PyExc_TypeError, "Unable to convert input to numpy array");
		return NULL;
	}
	//printf("Input converted and checked\n");

	// Check that input is a 2D array of uint8s
	if (PyArray_NDIM(input) != 2) {
		PyErr_SetString(PyExc_TypeError, "Input must be a 2D array");
		return NULL;
	}
	if (PyArray_TYPE(input) != NPY_INT8) {
		PyErr_SetString(PyExc_TypeError, "Input must be a 2D array of uint8s");
		return NULL;
	}
	if (PyArray_DIM(input, 0) < 3) {
		PyErr_SetString(PyExc_ValueError, "Input must have at least 3 rows");
		return NULL;
	}
	if (PyArray_DIM(input, 1) < 3) {
		PyErr_SetString(PyExc_ValueError, "Input must have at least 3 columns");
		return NULL;
	}

	uint8_t* arr = (uint8_t*)PyArray_DATA(input);
	npy_intp* dims = PyArray_DIMS(input);

	// Get the strides of the input array
	npy_intp* strides = PyArray_STRIDES(input);
	
	long long width = dims[1];
	long long height = dims[0];

	printf("width: %lld, height: %lld\n", width, height);
	

	// simple simd by using long longs
	uint8_t* partial_sum = (uint8_t*)calloc(height * (width-2), sizeof(uint8_t));
	if (partial_sum == NULL) {
		PyErr_SetString(PyExc_MemoryError, "Could not allocate memory");
		return NULL;
	}

	npy_intp partial_sum_dims[2] = {dims[0], dims[1]-2};
	npy_intp partial_sum_strides[2] = {dims[1]-2, 1};

	calculate_next_step_multithread_ndarray(arr, dims, strides, partial_sum, partial_sum_dims, partial_sum_strides);
	printf("Done calculating partial sums\n");
	free(partial_sum);
	printf("Done\n");
	Py_DECREF(inputOb);
	printf("Input decrefed\n");
	//Py_DECREF(input);
	return input;
	
}

static PyMethodDef GOL_methods[] = {
	{"init", GOL_init, METH_NOARGS, "Initialize GOL module"},
	{"step_NpArr", GOL_step_NpArr, METH_VARARGS, "Run one step of the simulation using numpy arrays"},
	{"step_list_multithread", GOL_step_list_multithread, METH_VARARGS, "Run one step of the simulation using lists and multithreading"},
	{"step_NpArr_multithread", GOL_step_NpArr_multithread, METH_VARARGS, "Run one step of the simulation using numpy arrays and multithreading"},
	// Add more methods here if needed
	{NULL, NULL, 0, NULL} // Sentinel
};

static struct PyModuleDef GOL_module = {
	PyModuleDef_HEAD_INIT,
	.m_name = "GOLCore",
	.m_doc = "Python extension module for GOL",
	.m_size = -1,
	.m_methods = GOL_methods
};

PyMODINIT_FUNC PyInit_core(void) {
	PyObject* module = PyModule_Create(&GOL_module);
	if (module == NULL) {
		return NULL;
	}
	import_array();
	return module;
}
