from PIL import Image, ImageFilter
import math
import sys
import os

# todo:
#   allow spaces to be trimmed off

# Binary way to create ascii shit!!

#10240 + 1 = |⠁
#      + 2 = |⠂
#      + 4 = |⠄
# and so on. Could construct ascii character for given pixel with
# brigtnesses such as 
# . 
# . .
#  
#   .
# by doing 10240 + 1 + 2 + 16 + 128

def get_brightness(r, g, b):
    # alternative means of calcing brightness
    return ( math.sqrt(0.299*(r**2) + 0.587*(g**2) + 0.114*(b**2)))
    #return int((r + g + b) / 3)

def calc_avg_pixel_colour(img, x, y, w, h, cutoff):
    r = 0
    g = 0
    b = 0
    num_px = 0
    for i in range(x, min(x + 2, w)):
        for j in range(y, min(y + 4, h)):
            R, G, B = img.getpixel((i, j))
            # Minor change so that pixels that aren't shown dont effect the average
            if get_brightness(R, G, B) > cutoff:
                r += R
                g += G
                b += B
                num_px += 1
    if num_px == 0:
        return (0, 0, 0)
    return (int(r / num_px), int(g / num_px), int(b / num_px))

def rgb_text(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def rgb_bg(r, g, b, text):
    return f"\033[48;2;{r};{g};{b}m{text}\033[0m"

def calc_img_arr(img, width, height, cutoff):
    str_arr = []
    for i in range(0, height, 4):
        str = ""
        for j in range(0, width, 2):
            val = 10240
            for k in range(0, 2):
                for l in range(0, 3):
                    if (j + k) < width and (i + l) < height:
                        R,G,B = img.getpixel((j + k, i + l))
                        if get_brightness(R,G,B) > cutoff:
                            val += 2 ** ((k * 3) + l)
            if (i + 3 < height):
                R,G,B = img.getpixel((j, i + 3))
                if get_brightness(R, G, B) > cutoff:
                    val += 64
                if (j + 1 < width):
                    R,G,B = img.getpixel((j + 1, i + 3))
                    if get_brightness(R, G, B) > cutoff:
                        val += 128
            str += chr(val)
            #str += rgb_text(r, g, b, chr(val))
            #print(chr(val), end="")
            #print(rgb_text(r, g, b, chr(val)), end="")
            #print(rgb_bg(r, g, b, chr(val)), end="")
        #print("") 
        str_arr.append(str)
    return str_arr

def remove_edges_from_char(edge_char, fill_char):
    edge_num = ord(edge_char) - 10240
    fill_num = ord(fill_char) - 10240
    new_num = (edge_num ^ fill_num) & (~edge_num)
    return_ch = chr(new_num + 10240)
    return return_ch
    
# doesnt really look very good if im being honest
def replace_img_edges(edge_arr, fill_arr, img, width, height, cutoff):
    new_arr = []
    gs_img = img.convert("L")
    gs_img = gs_img.convert("RGB")
    
    for i in range(0, len(edge_arr)):
        new_str = ""
        for j in range(0, len(edge_arr[i])):
            if ord(fill_arr[i][j]) == 10240:
                new_str += chr(10240)
            elif ord(edge_arr[i][j]) != 10240:
                r, g, b = calc_avg_pixel_colour(img, j * 2, i * 4, width, height, cutoff)
                new_str += rgb_text(r, g, b, remove_edges_from_char(edge_arr[i][j], fill_arr[i][j]))
                #new_str += rgb_text(r, g, b, fill_arr[i][j])
            else:
                r, g, b = calc_avg_pixel_colour(img, j * 2, i * 4, width, height, cutoff)
                new_str += rgb_text(r, g, b, fill_arr[i][j])
        new_arr.append(new_str)
    return new_arr

def gen_col_arr(img, width, height, cutoff):
    col_arr = []
    for i in range(0, height, 4):
        new_arr = []
        for j in range(0, width, 2):
            new_arr.append(calc_avg_pixel_colour(img, j, i, width, height, cutoff))
        col_arr.append(new_arr)
    return col_arr
            

def do_output(arr, col_arr, trim):
    first_str = -1
    last_str = 0
    first_char = len(arr[0])
    last_char = 0
    for i in range(0, len(arr)):
        for j in range(0, len(arr[i])):
            if ord(arr[i][j]) != 10240:
                if first_str == -1:
                    first_str = i
                last_str = i + 1
                if j < first_char:
                    first_char = j
                if j > last_char:
                    last_char = j + 1
    if trim:
        print("")
        for i in range(first_str, last_str):
            for j in range(first_char, last_char):

                r, g, b = col_arr[i][j]
                print(rgb_text(r, g, b, arr[i][j]), end="")

            print("")
            #print(arr[i])
        print("")
    else:
        print("")
        for i in range(first_str, last_str):
            for j in range(0, len(arr[0])):
                r, g, b = col_arr[i][j]
                print(rgb_text(r, g, b, arr[i][j]), end="")
            print("")
        print("")


def do_output_no_col(arr, trim):
    first_str = -1
    last_str = 0
    first_char = len(arr[0])
    last_char = 0
    for i in range(0, len(arr)):
        for j in range(0, len(arr[i])):
            if ord(arr[i][j]) != 10240:
                if first_str == -1:
                    first_str = i
                last_str = i + 1
                if j < first_char:
                    first_char = j
                if j > last_char:
                    last_char = j + 1
    for i in range(first_str, last_str):
        if trim:
            for j in range(first_char, last_char):
                print(arr[i][j], end="")

            print("")
        else:
            print(arr[i])
    print("")
 

# KEY
"""
---------
|1  |8  |
|2  |16 |
|4  |32 |
|64 |128|
---------
"""

def main():

    
    str_arr = []
    try:
        img = Image.open(sys.argv[1])
    except:
        print("Image not found")
        img = Image.open("/home/will/python/image_ascii_converter/mask.png")
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        IMG_WIDTH = int(sys.argv[2]) * 2
    else:
        IMG_WIDTH = os.get_terminal_size()[0] * 2
    if len(sys.argv) > 3 and sys.argv[3].isdigit():
        CUTOFF = int(sys.argv[3]) 
    else:
        CUTOFF = 70
    img = img.convert("RGB")
    width, height = img.size
    ratio = width / height
    IMG_HEIGHT = int(IMG_WIDTH / ratio)
    img = img.resize((IMG_WIDTH , IMG_HEIGHT))
    #res = res.convert("L")
    #res = res.convert("RGB")
    arr = calc_img_arr(img, IMG_WIDTH, IMG_HEIGHT, CUTOFF)
    # Edge detection
    # More to do its not really working properly yet
    res = img.convert("L")
    res = res.filter(ImageFilter.FIND_EDGES)
    res = res.convert("RGB")
    

    arr2 = calc_img_arr(res, IMG_WIDTH, IMG_HEIGHT, 100)

    do_output_no_col(arr, trim = True)

    do_output_no_col(arr2, trim = True)
    new_edges = replace_img_edges(arr2, arr, img, IMG_WIDTH, IMG_HEIGHT, CUTOFF)
    col_arr = gen_col_arr(img, IMG_WIDTH, IMG_HEIGHT, CUTOFF)
    do_output(arr, col_arr, trim = True)
main()
