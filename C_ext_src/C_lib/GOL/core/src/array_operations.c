#include "array_operations.h"

struct partial_sum {
	int8_t* arr;
	long long* arr_dims;
	long long* arr_strides;
};


static struct partial_sum partial_sum_buffer_setup(const long long* arr_dims) {
	// The partial summing is done in a seperate array
	// that is cached between calls to this function
	// if the array dimensions change, the buffer is invalidated (freed)
	// and a new buffer is created
	static long long partial_dims[2] = {0, 0};
	static long long partial_strides[2]= {0, 0};
	static int8_t* partial = NULL;

	if(partial_dims[0] != arr_dims[0] || partial_dims[1] != arr_dims[1] - 2) {
		if(partial != NULL) {
			free(partial);
		}
		partial_dims[0] = arr_dims[0];
		partial_dims[1] = arr_dims[1] - 2;
		partial = (int8_t*)calloc(partial_dims[0] * partial_dims[1], sizeof(int8_t));
		partial_strides[0] = partial_dims[1];
		partial_strides[1] = 1;
	}

	return (struct partial_sum){
		.arr = partial,
		.arr_dims = partial_dims,
		.arr_strides = partial_strides
	};
}


void calculate_next_step(int8_t* arr, long long* arr_dims, long long* arr_strides) {
	// recreate the partial sum array if the array dimensions have changed
	struct partial_sum par = partial_sum_buffer_setup(arr_dims);
	int8_t* partial = par.arr;
	long long* partial_dims = par.arr_dims;
	long long* partial_strides = par.arr_strides;
	
	// calculate the partial sums
	for (long long i = 0; i < partial_dims[0]; i ++) {
		for (long long j = 0; j < partial_dims[1]; j++) {
			long long index = i * arr_strides[0] + j * arr_strides[1];
			long long partial_index = i * partial_strides[0] + j * partial_strides[1];
			partial[partial_index] =
				arr[index							] +
				arr[index + arr_strides[1]				] +
				arr[index + arr_strides[1] + arr_strides[1]	];
		}
	}

	
	// calculate the next step
	int8_t arr_val;
	for (long long i = 1; i < arr_dims[0] - 1; i++) {
		for (long long j = 1; j < arr_dims[1] - 1; j++) {
			long long index = i * arr_strides[0] + j * arr_strides[1];
			long long partial_index = i * partial_strides[0] + (j - 1) * partial_strides[1];
			arr_val = arr[index];
			arr[index] = 
				partial[partial_index - partial_strides[0]	] +
				partial[partial_index						] +
				partial[partial_index + partial_strides[0]	] -
				arr[index];
			arr[index] = (arr[index] == 3 || (arr[index] == 2 && arr_val == 1) ? 1 : 0);
		}
	}


	return;
}