import win32com.client
import os

path = os.path.abspath("Sentinel_Presentation.pptx")
out_dir = os.path.abspath("submission/diagrams")
os.makedirs(out_dir, exist_ok=True)

app = win32com.client.Dispatch("PowerPoint.Application")
app.Visible = True
pres = app.Presentations.Open(path, WithWindow=False)

# Slide 5 = Architecture, Slide 15 = Technology & Integration
targets = {5: "Sentinel_Architecture.png", 15: "Sentinel_Workflow_Integration.png"}
for idx, fname in targets.items():
    slide = pres.Slides(idx)
    slide.Export(os.path.join(out_dir, fname), "PNG", 1920, 1080)

pres.Close()
app.Quit()
print("done", out_dir)
