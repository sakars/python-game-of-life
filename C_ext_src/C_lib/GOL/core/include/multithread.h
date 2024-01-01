#include <Python.h>
#include <stdio.h>
#include <xmmintrin.h>
#include <process.h>
#include <windows.h>

#pragma once

#ifndef THREAD_COUNT
#define THREAD_COUNT 4
#endif

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