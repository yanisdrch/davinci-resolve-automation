import sys
import os

modules_path = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"

if os.path.isdir(modules_path) and modules_path not in sys.path:
    sys.path.append(modules_path)

import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")

if not resolve:
    print("error: resolve empty")
    raise SystemExit(1)

project_manager = resolve.GetProjectManager()
project_name = "hellooooooo woooooooorld"
project = project_manager.CreateProject(project_name)

if project:
    print(f"Le projet est bien créé")
else: print(f"Le projet n'a pas pu être créé...")