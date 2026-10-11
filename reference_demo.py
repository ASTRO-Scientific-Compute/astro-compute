"""A small exact CPU example, not a GPU performance benchmark."""
import struct
from science_library.reference import prepare

if __name__ == '__main__':
    job = prepare('ENGINEERING_CSR_MATVEC_I32_V1', {
        'rowptr': [0, 2, 2, 3], 'col': [0, 1, 1],
        'values': [2, -1, 3], 'vector': [4, 5],
    })
    print('CPU reference: CSR matrix-vector product')
    print('Exact row outputs:', struct.unpack('<3q', job.reference))
    print('No GPU execution or performance measurement was performed.')
