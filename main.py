from funcs import *

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--path', help='file path', required=True, type=str)
parser.add_argument('--input', help='user input', required=True, type=str)
args = parser.parse_args()
path = args.path


# variables
# -------------------------------------------------------------------------------------------
xref_dict,root_obj,decompressed_stream = None, None, None
linearized, validation = False, False
first_obj_dict = {}
all_xrefs = []
# -------------------------------------------------------------------------------------------

# read first ten bytes
first_10_bytes = read_pdf(path, 10)
header_info = first_10_bytes.split(b"\n",1)[0]
if header_info.count(b"%") > 1:
    header_info = header_info.split(b"%",2)[1].decode()
else:
    header_info = header_info.decode()

print(header_info)
# check if the file is a pdf file or not
if "PDF" in header_info:
    # gather all objects
    pdf_content = read_pdf(path, -1)
    all_obj_dicts = extract_all_objects(pdf_content)

    # decompress the ObjStm objects as a first job and gather the missing objects
    objstm_objs = []
    for num, obj in all_obj_dicts.items():
        for key, value in obj.items():
            if key == b"Type" and value == b"ObjStm":
                first = int(obj.get(b"First"))
                n_val = int(obj.get(b"N"))
                filter_ = obj.get(b"Filter")
                stream = obj.get(b"stream")
                if filter_ == b"FlateDecode":
                    decompressed_stream = decompress_data(stream)
                else:
                    print("future development")
                objstm_objs.append([n_val, first,decompressed_stream])

    # process ObjStm objects and update all_obj_dict
    for obj in objstm_objs:
        n_val, first = obj[0], obj[1]
        obj = obj[2]

        obj_num_list = []
        if n_val > 1:
            nums_list = obj[:first].strip(b"\n\r ").split(b" ")
            nums_list = [int(nums_list[i]) for i in range(0, len(nums_list), 2)]
            obj_num_list = nums_list
        else:
            obj_num_list.append(int(obj[:first].strip(b"\n\r ").split(b" ",1)[0]))
        pure_obj = obj[first:]
        try:
            objs_list = pure_obj.split(b">>",n_val)[:-1]
            for num, obj_ in zip(obj_num_list, objs_list):
                the_obj = obj_ + b">>"
                all_obj_dicts[num] = process_object(the_obj)
        except ValueError:
            print("future development 2")

    # gather all objects to main dictionary with their object numbers
    for num, obj in all_obj_dicts.items():
        for key, value in obj.items():
            if key == b"Type" and value == b"Catalog":
                # ROOT
                root = obj
                # PAGES ROOT NODE
                pages_root = go_ref_or_stay(root[b"Pages"], all_obj_dicts)
                # ALL PAGES
                all_pages = traverse_page_tree(pages_root, all_obj_dicts)

                # get user input loop
                page_selection = None
                while True:
                    interval, invalid_in_list, all_ = False, False, False
                    user_inp = args.input
                    if user_inp.strip(" ") == "all":
                        all_ = True
                        break
                    try:
                        page_selection = [int(user_inp.strip(" "))]
                        if 0 < page_selection[0] < len(all_pages)+1:
                            break
                        else:
                            print("Invalid input")
                            exit()
                    except ValueError:
                        try:
                            page_selection = [int(i.strip(" ")) for i in user_inp.split("-")]
                            if len(page_selection) != 2:
                                print("Invalid input")
                                exit()
                            else:
                                interval = True
                                break
                        except ValueError:
                            try:
                                page_selection = list(map(int, user_inp.split(",")))
                                for i in page_selection:
                                    if not (0 < i < len(all_pages)+1):
                                        print("Invalid input")
                                        invalid_in_list = True
                                if invalid_in_list:
                                    print("Invalid input")
                                    exit()
                                else:
                                    break
                            except ValueError:
                                print("Invalid input")
                                exit()

                # this page rendering is only for this file (beta version 1.0)
                i = 0
                for page in all_pages:
                    i += 1

                    if not all_:
                        if interval:
                            if page_selection[0] > i or i > page_selection[1]:
                                continue
                        else:
                            if i not in page_selection:
                                continue

                    xobject = None, None, None, None
                    contents = page.get(b"Contents")
                    mediabox = page.get(b"MediaBox")
                    resources = page.get(b"Resources")
                    cropbox = page.get(b"CropBox")

                    # GET RESOURCES OBJECT
                    if resources:
                        xobject = resources.get(b"XObject")

                        # get xobject if exist in the file
                        if xobject:
                            for key_, value_ in xobject.items():
                                xobject[key_] = go_ref_or_stay(value_, all_obj_dicts)
                                xobject[key_] = xobject[key_] if not isinstance(xobject[key_], bytes) else None


                    # GET CONTENTS (this is only for single contents, special for this file)
                    if contents:
                        contents = go_ref_or_stay(contents, all_obj_dicts)
                        contents = decompress_data(contents[b"stream"]) if contents.get(b"Filter") == b"FlateDecode"\
                            else contents[b"stream"]

                    im = process_page(contents, mediabox, xobject, cropbox)
                    im.save(f"../images/Page-{i}.png")
                    print(f"Page-{i}.png saved...")

                print(f"Conversion successful!")

else:
    print("This file is not a pdf file...")





























