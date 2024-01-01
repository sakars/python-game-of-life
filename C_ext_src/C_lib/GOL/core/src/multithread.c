#include "multithread.h"




void __cdecl full_sum_calc(void* arg) {
	struct full_sum_thread_args* args = (struct full_sum_thread_args*)arg;
	char* arr = args->arr;
	int height = args->height;
	int width = args->width;
	int y_start = args->y_start;
	int y_step = args->y_step;
	char* partial_sum = args->partial_sum;
	char* next = args->next;
	int y_iter;
	int x_iter;
	// calculate full sums from partial sums
	for(y_iter=y_start; y_iter<height-2;y_iter+=y_step){
		// partial loop unrolling for all but the last n<8 elements
		for(x_iter=0; x_iter<width-2-8; x_iter+=8) {
			*(uint64_t*)(next+(y_iter+1)*(width)+x_iter+1) = 
				*(uint64_t*)(partial_sum+(y_iter+0)*(width-2)+x_iter) +
				*(uint64_t*)(partial_sum+(y_iter+1)*(width-2)+x_iter) +
				*(uint64_t*)(partial_sum+(y_iter+2)*(width-2)+x_iter) -
				*(uint64_t*)(arr+(y_iter+1)*(width)+x_iter+1);
			//printf("next: %llx\n", *(uint64_t*)(next+y_iter*(width-2)+x_iter));
		}
		// do the last n<8 elements
		for(x_iter-=8; x_iter<width-2; x_iter++) {
			next[(y_iter+1)*(width)+x_iter+1] = 
				partial_sum[(y_iter+0)*(width-2)+x_iter] +
				partial_sum[(y_iter+1)*(width-2)+x_iter] +
				partial_sum[(y_iter+2)*(width-2)+x_iter] -
				arr[(y_iter+1)*(width)+x_iter+1];
		}
	}
}




void __cdecl partial_sum_calc(void* arg) {
	//printf("Running thread o_ o\n");
	struct partial_sum_thread_args* args = (struct partial_sum_thread_args*)arg;
	char* arr = args->arr;
	int height = args->height;
	int width = args->width;
	int y_start = args->y_start;
	int y_step = args->y_step;
	char* partial_sum = args->partial_sum;
	int y_iter;
	int x_iter;
	for (y_iter = y_start; y_iter<height;y_iter+=y_step) {
		// do partial loop unrolling for all but the last n<8 elements
		for(x_iter = 0;x_iter<(width-2)-8;x_iter+=8) {
			*(uint64_t*)(partial_sum + y_iter*(width-2) + x_iter) = 
				*(uint64_t*)(arr + (y_iter)*width + (x_iter+0)) + 
				*(uint64_t*)(arr + (y_iter)*width + (x_iter+1)) +
				*(uint64_t*)(arr + (y_iter)*width + (x_iter+2));
			//printf("partial sum: %llu\n", *(uint64_t*)(partial_sum + y_iter*(width-2) + x_iter));
		}
		// do the last n<8 elements
		for(x_iter-=8;x_iter<(width-2);x_iter++) {
			partial_sum[y_iter*(width-2)+x_iter] = 
				arr[y_iter*width+x_iter+0] + 
				arr[y_iter*width+x_iter+1] + 
				arr[y_iter*width+x_iter+2];
		}
	}
	
}

// This function is called from Python,
// it takes in a 2D array of booleans or 0/1 integers and returns a new 2D array of booleans
// representing the next step in the simulation
// The input array is modified in-place
PyObject* GOL_step_list_multithread(PyObject* self, PyObject* args) {
	clock_t c_start = clock(), c_chk, c_cpy1, c_cpy2, c_sum, c_next, c_end;
	PyObject* input;
	if (!PyArg_ParseTuple(args, "O", &input)) {
		return NULL;
	}
	// Check that input is a 2D array of booleans
	if (!PyList_Check(input)) {
		PyErr_SetString(PyExc_TypeError, "Input must be a 2D array");
		return NULL;
	}
	Py_ssize_t height = PyList_Size(input);
	if (height < 3) {
		PyErr_SetString(PyExc_ValueError, "Input must have at least 3 rows");
		return NULL;
	}
	if (height == 0) {
		PyErr_SetString(PyExc_ValueError, "Input must have at least one row");
		return NULL;
	}
	PyObject* row_ref = PyList_GetItem(input, 0);
	if (!PyList_Check(row_ref)) {
		PyErr_SetString(PyExc_TypeError, "Input must be a 2D array");
		return NULL;
	}
	Py_ssize_t width = PyList_Size(row_ref);
	if (width < 3) {
		PyErr_SetString(PyExc_ValueError, "Input must have at least 3 columns");
		return NULL;
	}
	if (width == 0) {
		PyErr_SetString(PyExc_ValueError, "Input must have at least one column");
		return NULL;
	}
	c_chk = clock();
	c_cpy1 = clock();
	//printf("Input checked :D\n");
	// clone input array into a C array
	char* arr = (char*)calloc(height * width, sizeof(char));
	if (arr == NULL) {
		PyErr_SetString(PyExc_MemoryError, "Could not allocate memory");
		return NULL;
	}
	{
		PyObject* row_ref;
		for (Py_ssize_t i = 0; i < height; i++) {
			row_ref = PyList_GetItem(input, i);
			const Py_ssize_t row_offset = i * width;
			for (Py_ssize_t j = 0; j < width; j++) {
				arr[row_offset + j] = (char)PyLong_AsLong(PyList_GetItem(row_ref, j));
			}
		}
	}
	c_cpy2 = clock();
	// run the simulation
	//printf("Running simulation o_ o\n");
	// allocate memory for the next step and the sums
	char* next = (char*)calloc(height * width, sizeof(char));
	if (next == NULL) {
		PyErr_SetString(PyExc_MemoryError, "Could not allocate memory");
		return NULL;
	}
	

	// simple simd by using long longs
	char* partial_sum = (char*)calloc(height * width-2, sizeof(char));
	if (partial_sum == NULL) {
		PyErr_SetString(PyExc_MemoryError, "Could not allocate memory");
		return NULL;
	}
	Py_BEGIN_ALLOW_THREADS
	
	struct partial_sum_thread_args partial_args[THREAD_COUNT];
	HANDLE partial_threads[THREAD_COUNT];
	for (int i=0;i<THREAD_COUNT;i++) {
		partial_args[i] = (struct partial_sum_thread_args){
			.arr = arr,
			.partial_sum = partial_sum,
			.height = height, 
			.width = width, 
			.y_start = i,
			.y_step = THREAD_COUNT
		};
		partial_threads[i] = _beginthreadex(NULL, 0, partial_sum_calc, &partial_args[i], 0, NULL);
	}

	//WaitForSingleObject((HANDLE)handle, INFINITE);
	WaitForMultipleObjects(THREAD_COUNT, (HANDLE*)partial_threads, TRUE, INFINITE);
	c_sum = clock();
	/*
	// print partial sums
	for (int i=0;i<height;i++) {
		for (int j=0;j<width-2;j++) {
			printf("%d ", partial_sum[i*(width-2)+j]);
		}
		printf("\n");
	}
	*/
	struct full_sum_thread_args full_args[THREAD_COUNT];
	HANDLE full_threads[THREAD_COUNT];
	for (int i=0;i<THREAD_COUNT;i++) {
		full_args[i] = (struct full_sum_thread_args){
			.arr = arr,
			.partial_sum = partial_sum,
			.next = next,
			.height = height, 
			.width = width, 
			.y_start = i,
			.y_step = THREAD_COUNT
		};
		full_threads[i] = _beginthreadex(NULL, 0, full_sum_calc, &full_args[i], 0, NULL);
	}

	WaitForMultipleObjects(THREAD_COUNT, (HANDLE*)full_threads, TRUE, INFINITE);
	c_next = clock();
	// print partial sums
	/*
	for (int i=0;i<height;i++) {
		for (int j=0;j<width;j++) {
			printf("%d ", next[i*(width)+j]);
		}
		printf("\n");
	}
	*/
	
	
	for (int h=0;h<height;h++) {
		for (int i=0;i<width;i++) {
			next[h*width+i] = (char)(next[h*width+i] == 3 || (next[h*width+i] == 2 && arr[h*width+i] == 1));
		}
	}
	Py_END_ALLOW_THREADS
	free(partial_sum);

	// copy the next step into the python array
	for(int i=1; i<height-1;i++) {
		for(int j=1;j<width-1; j++) {
			// we already checked that the input is a 2D array of booleans or 0/1 integers
			PyObject* row = PyList_GET_ITEM(input, i);
			int e = PyList_SetItem(row, j, PyLong_FromLong(next[i*width+j]));
			if(e == -1) {
				PyErr_SetString(PyExc_RuntimeError, "Could not set item in list");
				return NULL;
			}
		}
	}
	

	// free memory
	free(arr);
	free(next);
	c_end = clock();
	/*printf("chk: %f\n copy over: %f\n partial_calc: %f\n full_calc: %f\n copy over: %f\n", 
		(double)(c_chk-c_start)/CLOCKS_PER_SEC,
		(double)(c_cpy2-c_chk)/CLOCKS_PER_SEC,
		(double)(c_sum-c_cpy2)/CLOCKS_PER_SEC,
		(double)(c_next-c_sum)/CLOCKS_PER_SEC,
		(double)(c_end-c_next)/CLOCKS_PER_SEC);
	*/


	Py_RETURN_NONE;
}


