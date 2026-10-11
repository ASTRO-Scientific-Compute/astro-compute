"""Fixed public demo admission; no environment or CLI override."""

WORKLOADS = (
    'SPACE_GWOSC_FFT256_V1',
    'SPACE_GWOSC_CONVOLUTION_V1',
    'SPACE_GWOSC_XCORR_V1',
    'SIGNAL_FIR_ACCUMULATE_I16_V1',
)
MAX_MATHSPECS = 4


def require_workload(workload_id):
    if workload_id not in WORKLOADS:
        raise ValueError('MathSpec outside the four-task demo allowlist')


def select_workloads(count):
    if type(count) is not int or not 1 <= count <= MAX_MATHSPECS:
        raise ValueError('The demo permits 1 to 4 MathSpecs per run')
    return WORKLOADS[:count]


class RunAdmission:
    def __init__(self):
        self.started = set()

    def admit(self, workload_id):
        require_workload(workload_id)
        if workload_id in self.started:
            raise ValueError('MathSpec already started in this demo run')
        if len(self.started) >= MAX_MATHSPECS:
            raise ValueError('Four-MathSpec demo limit reached')
        self.started.add(workload_id)
