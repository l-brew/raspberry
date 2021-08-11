#!/usr/bin/env python3
import debugpy

def debug():
    debugpy.listen(('0.0.0.0' , 5678))
    print("Waiting for debugger to attach")
    debugpy.wait_for_client()
    debugpy.breakpoint()
    print('break on this line')