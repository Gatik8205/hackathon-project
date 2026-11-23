import importlib.metadata as md
for d in md.distributions():
    try:
        d.read_text("entry_points.txt")
    except Exception as e:
        print("BAD:", getattr(d, "_path", d), "->", e)
print("scan done")