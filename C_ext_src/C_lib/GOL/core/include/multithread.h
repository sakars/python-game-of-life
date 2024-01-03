#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdio.h>
#include <xmmintrin.h>
#include <process.h>
#include <windows.h>

#pragma once

#ifndef THREAD_COUNT
#define THREAD_COUNT 4
#endif

void calculate_next_step_multithread(long long width, long long height, char* arr, char* next, char* partial_sum);

PyObject* GOL_step_list_multithread(PyObject* self, PyObject* args);

struct partial_sum_thread_args {
	char* arr;
	char* partial_sum;
	int height;
	int width;
	int y_start;
	int y_step;

};

struct full_sum_thread_args {
	char* arr;
	char* partial_sum;
	char* next;
	int height;
	int width;
	int y_start;
	int y_step;
};

struct partial_sum_ndarray_thread_args {
	char* arr;
	char* partial_sum;
	npy_intp* arr_dims;
	npy_intp* arr_strides;
	npy_intp* partial_sum_dims;
	npy_intp* partial_sum_strides;
	long long y_start;
	long long y_step;
};

struct full_sum_ndarray_thread_args {
	char* arr;
	char* partial_sum;
	npy_intp* arr_dims;
	npy_intp* arr_strides;
	npy_intp* partial_sum_dims;
	npy_intp* partial_sum_strides;
	long long y_start;
	long long y_step;
};

void calculate_next_step_multithread_ndarray(uint8_t* arr, npy_uintp* arr_dims, npy_uintp* arr_strides, uint8_t* partial_sum, npy_uintp* partial_sum_dims, npy_uintp* partial_sum_strides);