import platform
import struct

print("Python bit:", struct.calcsize("P") * 8)
print("Platform:", platform.platform())

try:
    import pyarmor_runtime

    print("pyarmor_runtime import: OK")
    print("pyarmor_runtime file:", pyarmor_runtime.__file__)
except Exception as e:
    print("pyarmor_runtime import: NG")
    print("Error:", repr(e))
