import inspect
from parallex.io.image_loader import RawImageReader

print("=" * 60)
print("RawImageReader API")
print("=" * 60)

print(inspect.signature(RawImageReader.read_window))
print()
print(inspect.getsource(RawImageReader.read_window))
