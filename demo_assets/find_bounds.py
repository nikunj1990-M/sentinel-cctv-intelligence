from PIL import Image
im = Image.open('demo_assets/anpr_check2.png').convert('RGB')
w, h = im.size
px = im.load()
x = 551
prev_dark = False
for y in range(0, h):
    r, g, b = px[x, y]
    dark = (r < 15 and g < 15 and b < 15)
    if dark and not prev_dark:
        print('goes dark at y=', y)
    if not dark and prev_dark:
        print('goes light at y=', y, (r, g, b))
    prev_dark = dark
