import glob
import os

for ui_file in glob.glob("torf_gui/*.ui"):
    py_file = ui_file.replace(".ui", ".py")
    filename = "ui_" + os.path.basename(py_file)
    output_file = os.path.join("torf_gui", filename)

    print(f"Generating {output_file} from {ui_file}")
    os.system(f"pyuic5 -o {output_file} {ui_file}")
