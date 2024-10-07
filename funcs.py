from zlib import decompress
from io import BytesIO
from PIL import Image
import argparse

# read pdf file binary
def read_pdf(path, bytes_to_read = -1, seek = 0, reverse = 0 ):
    with open(path, 'rb') as f:
        f.seek(seek, reverse)
        content = f.read(bytes_to_read)
    return content

# process object, create dictionary and return it
# (this function supports max 3 digit object numbers)
def process_object(content):
    #print(content)
    current_dict, new_dict = {}, {}
    stack, item_list, num_str, param_stack, temp_list = [], [], [], [], []
    key = value = None
    bool_1 = False
    i = arr = hex_arr = str_arr = 0
    while i < len(content):
        if not (arr or str_arr or hex_arr):
            if content[i:i + 2] == b'<<':
                new_dict = {}
                if key:
                    current_dict[key] = new_dict
                    key = value = None
                stack.append(current_dict)
                current_dict = new_dict
                i += 2
                continue
            elif content[i:i + 2] == b">>":
                if key and value:
                    current_dict[key] = value
                    item_list = []
                elif key and not value:
                    value = b"".join(item_list)
                    current_dict[key] = value
                    item_list = []
                if len(stack[-1]):
                    last_dict = stack.pop()
                    current_dict = last_dict
                key = value = None
                i += 2
                continue
            elif content[i:i + 1] == b"\n" or content[i:i + 1] == b" " or content[i:i + 1] == b"\r":
                if item_list and not key:
                    key = b"".join(item_list)
                    item_list = []
                i += 1
                continue
            elif content[i:i + 1] == b" ":
                if not key and item_list:
                    key = b"".join(item_list)
                    item_list = []
                i += 1
                continue
            elif content[i:i + 1] == b"[":
                if not key and item_list:
                    key = b"".join(item_list)
                arr += 1
                i += 1
                continue
            elif content[i:i + 1] == b"<":
                hex_arr += 1
                i += 1
                continue
            elif content[i:i + 1] == b">":
                if key and not value:
                    value = param_stack[0]
                    current_dict[key] = value
                    param_stack = []
                    value = key = None
                i += 1
                continue
            elif content[i:i + 1] == b"(":
                if not key:
                    key = b"".join(item_list)
                item_list = []
                str_arr += 1
                i += 1
                continue
            elif content[i:i + 1] == b")":
                if key and not value:
                    value = b"".join(param_stack)
                    current_dict[key] = value
                    key = value = None
                    param_stack = []

                i += 1
                continue
            elif content[i:i + 6] == b"stream":
                key = b"stream"
                value = content[i + 6 :].split(b"endstream", 1)[0].strip(b"\n\r ")
                i += len(key) + len(value) + 12
                value = value.strip(b"\n\r ")
                current_dict[key] = value
                key = value = None
                continue
            else:
                add_on_2 = 0
                if content[i:i + 1] == b"/":
                    if item_list and not key:
                        key = b"".join(item_list)
                        item_list = []
                    elif item_list and key and not value:
                        value = b"".join(item_list)
                        current_dict[key] = value
                        key = value = None
                        item_list = []
                    elif key and value:
                        current_dict[key] = value
                        key = value = None
                        item_list = []
                    else:
                        first = content[i:].split(b" ", 1)[0].strip(b">")
                        if first.count(b"/") > 1:
                            first = first.split(b"/", 2)[1]
                            add_on_2 = 1
                        if first.count(b"<<") > 0:
                            first = first.split(b"<<", 1)[0]
                        if first.count(b">>") > 0:
                            first = first.split(b">>", 1)[0]
                        if first.count(b"[") > 0:
                            first = first.split(b"[", 1)[0]
                            arr += 1
                            add_on_2 += 1
                        if first.count(b"(") > 0:
                            first = first.split(b"(", 1)[0]
                            str_arr += 1
                            add_on_2 += 1
                        if first.count(b"<") == 1:
                            first = first.split(b"<", 1)[0]
                            hex_arr += 1
                        if key and not value:
                            value = first.strip(b"/([")
                        else:
                            key = first.strip(b"/([")
                        i += len(first) + add_on_2

                    continue
                else:
                    try:
                        int(content[i:i +3].replace(b" ",b"N"))
                        item_list.append(content[i:i + 3])
                        i += 3
                    except (ValueError, IndexError):
                        try:
                            int(content[i:i + 2].replace(b" ",b"N"))
                            item_list.append(content[i:i + 2])
                            i += 2
                        except (ValueError, IndexError):
                            item_list.append(content[i:i + 1])
                            if len(item_list) > 2 and item_list[-1] == b"R" and item_list[-2] == b"0" and (
                                    b"0" <= item_list[-3] <= b"999"):
                                value = b"R" + item_list[-3]
                            i += 1

        elif arr:
            if not (hex_arr or str_arr):
                if content[i:i + 1] == b"<":
                    if num_str:
                        param_stack.append(b"".join(num_str))
                        num_str.clear()

                    hex_arr += 1
                    i += 1
                    continue
                elif content[i:i + 1] == b"R":
                    if num_str and num_str[-1] == b"0" and (b"0" <= num_str[-2] <= b"999"):
                        num_str.append(b"R" + num_str[-2])
                        num_str.pop(-2)
                        num_str.pop(-2)
                    if not key:
                        key = num_str[0].strip(b"/")
                        num_str.pop(0)

                    i += 1
                elif content[i:i + 1] == b">":
                    if num_str:
                        param_stack.append(b"".join(num_str))
                    num_str.clear()
                    if key and not value:
                        value = param_stack
                        current_dict[key] = value
                        key = value = None
                    hex_arr -= 1
                    i += 1
                    continue
                elif content[i:i + 1] == b"\n" or content[i:i + 1] == b" " or content[i:i + 1] == b"\r":
                    if temp_list:
                        num_str.append(b"".join(temp_list))
                        temp_list.clear()
                    i += 1
                    continue
                elif content[i:i + 1] == b"/":
                    add_on = 0
                    first = content[i:].split(b"]", 1)[0].strip(b">")
                    if first.count(b"[") > 0:
                        first = first.split(b"[", 1)[0]
                        arr += 1
                        add_on = 1
                    elif first.count(b" ") > 0:
                        first = first.split(b" ", 1)[0]
                    elif first.count(b"/") > 1:
                        first = first.split(b"/", 2)[1]
                        add_on = 1
                    elif first.count(b"(") > 0:
                        first = first.split(b"(", 1)[0]
                        str_arr += 1
                    value = first.strip(b"/")
                    temp_list.append(value)
                    bool_1 = True
                    i += len(first) + add_on
                elif content[i:i + 1] == b"(":
                    if num_str:
                        param_stack.append(b"".join(num_str))
                        num_str.clear()
                    i += 1
                elif content[i:i + 1] == b")":
                    if num_str:
                        param_stack.append(b"".join(num_str))
                        num_str.clear()
                    if key and not value:
                        value = param_stack
                        current_dict[key] = value
                        key = value = None
                        param_stack = []
                    i += 1
                elif content[i:i + 1] == b"]":
                    if temp_list and not bool_1:
                        num_str.append(b"".join(temp_list))
                        temp_list.clear()
                    elif temp_list:
                        [param_stack.append(el) for el in temp_list]
                        temp_list.clear()
                    if num_str:
                        [param_stack.append(el) for el in num_str]
                        num_str.clear()
                    if len(param_stack) > 1:
                        value = param_stack
                    elif len(param_stack) == 1:
                        value = param_stack[0]
                    else:
                        value = b""
                    param_stack = []
                    current_dict[key] = value
                    key = value = None
                    arr -= 1
                    i += 1
                    bool_1 = False
                    continue
                elif content[i:i + 1] == b"-" or (b"0" <= content[i:i + 1] <= b"9"):
                    temp_list.append(content[i:i + 1])
                    i += 1
                elif content[i:i + 1] == b" ":
                    if num_str:
                        param_stack.append(b"".join(num_str))
                        num_str.clear()
                    i += 1
                else:
                    temp_list.append(content[i:i + 1])
                    i += 1
            else:
                if hex_arr:
                    parts = content[i:].split(b">", 1)
                    first = parts[0]
                    jump_len = len(first)
                    param_stack.append(b"<" + first + b">")
                    i += jump_len + 1
                    hex_arr -= 1
                    continue

                elif str_arr:
                    parts = content[i:].split(b")", 1)
                    first = parts[0]
                    jump_len = len(first)
                    param_stack.append(first)
                    i += jump_len
                    continue

        elif hex_arr:
            parts = content[i:].split(b">", 1)
            first = b"<" + parts[0] + b">"
            jump_len = len(first)
            param_stack.append(first)
            i += jump_len
            hex_arr -= 1
            continue

        elif str_arr:
            parts = content[i:].split(b")", 1)
            first = parts[0]
            before_slash = content[i:].split(b"/")[0].strip(b"()")
            if before_slash == first:
                if key and not value:
                    value = first
                i += len(first)
                str_arr -= 1
                continue
            k = 2
            while b")" in parts[1]:
                parts = content[i:].split(b")", i)
                first = b")".join(parts[:k])
                k += 1

            jump_len = len(first)
            if b"\xdele" in first:
                temp = first.split(b"\xdele", 1)
                first = temp[0][:-1] + temp[-1]
            param_stack.append(first)
            i += jump_len
            str_arr -= 1
            continue

    return current_dict

# decompressing for flate decode
def decompress_data(data):
    decompressed_data = decompress(data)
    return decompressed_data

# find and extract all objects into a dictionary as individual dictionaries
# (this function is for this file's syntax (\r\n separated), should be developed
# for different files)
def extract_all_objects(content):
    obj_dicts = {}
    objects = content.split(b"endobj")[:-1]
    objects = [obj.strip(b"\n\r ") for obj in objects]
    for obj in objects:
        parts = []
        # throw the comments %
        if not b"stream" in obj:
            for part in obj.split(b"\n"):
                if part.startswith(b"%"):
                    continue
                else:
                    parts.append(part)
            obj = b"\n".join(parts)

        obj_parts = obj.split(b" 0 obj")
        obj_num = obj_parts[0].split(b"\n")[-1].strip(b"\r ")
        try:
            obj_num = int(obj_num)
        except ValueError:
            print("fix me 1")
            break
        pure_obj = obj_parts[1].strip(b"\r\n ")
        pure_obj = process_object(pure_obj)
        obj_dicts[obj_num] = pure_obj
    return obj_dicts

# if input is a reference, return its object as a dictionary
def go_ref_or_stay(byte, dictionary):
    try:
        if byte[:1] == b"R":
            return dictionary[int(byte[1:])]
        else:
            return byte
    except KeyError:
        return byte

# start from root pages node and get all page nodes
def traverse_page_tree(page_node, all_obj_dicts):
    # return when reach to page object
    if page_node.get(b"Type") == b"Page":
        return page_node

    # get the kids list if object type is Pages
    if page_node.get(b"Type") == b"Pages":
        kids = page_node.get(b"Kids", [])
        all_pages = []

        # get kids dictionary by their references and repeat
        for kid_ref in kids:
            kid_obj = go_ref_or_stay(kid_ref, all_obj_dicts)
            pages = traverse_page_tree(kid_obj, all_obj_dicts)
            # add the found page objects to the list
            if pages:
                all_pages.extend(pages if isinstance(pages, list) else [pages])

        return all_pages
    return None

# process page object
def process_page(contents_list, mediabox, xobject, cropbox):
    page_width = float(mediabox[2]) - float(mediabox[0])
    page_height = float(mediabox[3]) - float(mediabox[1])

    canvas = Image.new('RGB', (int(page_width), int(page_height)), 'white')
    im = handle_content_stream(canvas, contents_list, xobject)
    # offset for cropping and placing the image in the middle
    offset = int((float(mediabox[3]) - float(cropbox[3])) - (float(cropbox[1]) - float(mediabox[1])))
    im = im.crop((
        float(cropbox[0]),
        float(cropbox[1]) + offset,
        float(cropbox[2]),
        float(cropbox[3]) + offset
    ))
    return im

# process content stream (this function is only for image-only pdf files)
# {all parameters are being kept in param stack.
# if it meets a command, it is sent to the
# main stack with the parameters of the command}
def handle_content_stream(image, stream, xobj_dict):
    if stream:
        save,stack = {}, {}
        stack.update({b"cm":[b"1.0", b"0.0", b"0.0", b"1.0", b"0.0", b"0.0"]})
        stack.update({"reverse":False})
        param_stack, tj_arr, td_arr, array_stack, hex_str, num_str = [], [], [], [], [], []
        arr = str_arr = hex_arr = 0

        commands = stream.strip(b"\n").replace(b"\n", b"||").replace(b" ",b"||").replace(b"\r",b"||")

        if commands:
            i = 0
            while i < len(commands):
                if not (arr or str_arr or hex_arr):
                    if commands[i:i+2] == b"||":
                        i += 2
                        continue
                    elif commands[i:i+2] == b"<<":
                        block = commands[i:].split(b">>",1)[0] + b">>"
                        i += len(block)
                        continue
                    elif commands[i:i+1] == b"[":
                        arr += 1
                        i += 1
                        continue
                    elif commands[i:i+1] == b"(":
                        str_arr += 1
                        i += 1
                        continue
                    elif commands[i:i+1] == b")":
                        i += 1
                        continue
                    elif commands[i:i+1] == b"<":
                        hex_arr += 1
                        i += 1
                        continue
                    elif commands[i:i+1] == b">":
                        hex_arr -= 1
                        i += 1
                        continue
                    elif commands[i:i+2] == b"BT" or commands[i:i+2] == b"ET" or \
                            commands[i:i + 2] == b"Td":
                        param_stack = []
                        i += 2
                        continue
                    elif commands[i:i+1] == b"q":
                        save = stack
                        i += 1
                    elif commands[i:i+1] == b"Q":
                        stack = save
                        i += 1
                    elif commands[i:i+2] == b"cm":
                        stack[b"cm"] = param_stack
                        param_stack = []
                        i += 2
                    elif commands[i:i+3] == b"BDC":
                        param_stack = []
                        i += 3
                    elif commands[i:i+3] == b"EMC":
                        param_stack = []
                        i += 3
                    elif commands[i:i+2] == b"Do":
                        cm_parms = stack[b"cm"]
                        cm(cm_parms, stack)
                        xobj = do(param_stack, xobj_dict, stack)
                        param_stack = []
                        if xobj:
                            # print the page object image in the middle of the page
                            image.paste(xobj, ((image.width - xobj.width) // 2, (image.height - xobj.height) // 2))
                        i += 2
                    else:
                        parts = commands[i:].split(b"||",1)
                        first = parts[0]
                        rest = parts[-1]
                        param_stack.append(first)
                        i += len(first)

                        if first == rest:
                            break

                elif arr:
                    if commands[i:i+1] == b"<":
                        if num_str:
                            param_stack.append(b"".join(num_str))
                            num_str.clear()
                        hex_arr += 1
                        i += 1
                        continue
                    elif commands[i:i+2] == b"||" and not str_arr:
                        if num_str:
                            param_stack.append(b"".join(num_str))
                            num_str.clear()
                        i += 2
                        continue
                    elif commands[i:i+1] == b">":
                        if num_str:
                            param_stack.append(b"".join(num_str))
                        num_str.clear()
                        hex_arr -= 1
                        i += 1
                        continue
                    elif commands[i:i+1] == b"(":
                        if num_str:
                            param_stack.append(b"".join(num_str))
                            num_str.clear()
                        i += 1
                        str_arr += 1
                    elif commands[i:i+1] == b")":
                        if num_str:
                            param_stack.append(b"".join(num_str))
                            num_str.clear()
                        i += 1
                    elif commands[i:i+1] == b"]":
                        if num_str:
                            param_stack.append(b"".join(num_str))
                            num_str.clear()
                        arr -= 1
                        i += 1
                        continue
                    elif not hex_arr and (commands[i:i+1] == b"-" or (b"0" <= commands[i:i + 1] <= b"9")):
                        num_str.append(commands[i:i+1])
                        i += 1
                    else:
                        if hex_arr:
                            parts = commands[i:].split(b">", 1)
                            first = parts[0]
                            jump_len = len(first)
                            param_stack.append(b"<" + first + b">")
                            i += jump_len
                            continue

                        if str_arr:
                            parts = commands[i:].split(b")", 1)
                            a = 2
                            first = parts[0]
                            while first.count(b"(") != first.count(b")"):
                                parts_2 = commands[i:].split(b")", a)
                                first = b")".join(parts_2[:a])
                                a += 1
                            jump_len = len(first)
                            first = first.replace(b"||", b" ").replace(b"\\", b"")
                            if b"\xdele" in first:
                                temp = first.split(b"\xdele", 1)
                                first = temp[0][:-1] + temp[-1]
                            param_stack.append(first)
                            i += jump_len
                            str_arr -= 1
                            continue

                elif str_arr:
                    parts = commands[i:].split(b")",1)
                    a = 2
                    first = parts[0]
                    while first.count(b"(") != first.count(b")"):
                        parts_2 = commands[i:].split(b")", a)
                        first = b")".join(parts_2[:a])
                        a += 1
                    jump_len = len(first)
                    first = first.replace(b"||",b" ").replace(b"\\",b"")
                    if b"\xdele" in first:
                        temp = first.split(b"\xdele", 1)
                        first = temp[0][:-1] + temp[-1]
                    param_stack.append(first)
                    i += jump_len
                    str_arr -= 1
                    continue

                elif hex_arr:
                    parts = commands[i:].split(b">",1)
                    first = parts[0]
                    jump_len = len(first)
                    param_stack.append(first)
                    i += jump_len
                    continue
    return image

# function of concatenate matrix (cm) command
# {in this code, this function is only used for image x and y scaling, only for this file}
def cm(parms, stack):
    a, b, c, d, e, f = (float(parms[0]),
                        float(parms[1]),
                        float(parms[2]),
                        float(parms[3]),
                        float(parms[4]),
                        float(parms[5]))

    stack["scale_x"] = a
    stack["scale_y"] = d

# function of "Do" comment, for drawing the images
def do(parms, xobj_dict, stack):
    parm = parms[0].strip(b"/")
    ret_obj = None

    if parm in xobj_dict.keys():
        xobj = xobj_dict[parm]

        # get xobj parameters (for this file only subtype, stream and filter are required)
        filter_ = xobj.get(b"Filter")
        subtype = xobj.get(b"Subtype")
        stream = xobj.get(b"stream")

        if subtype == b"Image":
            if filter_ == b"JPXDecode" or filter_ == b"DCTDecode":
                image = Image.open(BytesIO(stream)).resize((int(stack["scale_x"]), int(stack["scale_y"])))
                ret_obj = image

    return ret_obj














