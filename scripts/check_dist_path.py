from pathlib import Path
p = Path("V:/BDT/backend/app/main.py").resolve()
print("p:", p)
print("parents[0]:", p.parents[0])
print("parents[1]:", p.parents[1])
print("parents[2]:", p.parents[2])
dist_dir = p.parents[2] / "frontend" / "dist"
print("dist_dir:", dist_dir)
print("dist_dir.is_dir():", dist_dir.is_dir())
