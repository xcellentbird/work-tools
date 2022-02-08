def convert_tsm_json(json_data:dict, img_path:str, site_rename:dict) -> dict:
    data_format = dict()
    new_img_name = json_data["img_name"]
    site, day, time, light, weather = '', '2020_01_01', '00_00_00', '', ''
    if "weather" in json_data.keys():
        weather = json_data["weather"]
    if "time" in json_data.keys():
        light = json_data["time"]
        
    try:
        contents = new_img_name.split('_')
        site,date = contents[0], contents[2]
        yyyy, MM, dd, time = date.split('-')
        hh, mm, sec = time.split('.')
        time = '_'.join([hh, mm, sec])
        day = '_'.join([yyyy, MM, dd])
    except:
        pass

    data_format["dtype"] = "label"
    data_format["img_name"] = new_img_name
    data_format["img_path"] = '/'.join([img_path, new_img_name])
    img_size = {}
    img_size["width"], img_size["height"] = json_data["image_size"][:2]
    data_format["img_size"] = img_size
    
    objects = []
    class_cnts = dict()
    for obj in json_data["objects"]:
        obj_name = obj["tag"]
        if obj_name not in class_cnts:
            class_cnts[obj_name] = 0
        class_cnts[obj_name] += 1
        bbox = dict()
        bbox["x_min"], bbox["y_min"] = obj["bbox"][0:2]
        bbox["x_max"], bbox["y_max"] = obj["bbox"][2:4]
        bbox_size = {"width": bbox["x_max"] - bbox["x_min"],
                    "height": bbox["y_max"] - bbox["y_min"]}
        objects.append({"class": obj_name,
                        "bbox": bbox,
                        "bbox_size": bbox_size})

    data_format["objects"] = objects
    data_format["object_cnt"] = len(objects)
    data_format["class_cnts"] = class_cnts
    data_format["country"] = 'korea'
    data_format["dataset"] = 'pyeongtaek'
    if site in site_rename:
        site = site_rename[site]
    else:
        site = ''
    data_format["site"] = site
    data_format["date"] = day + "-" + time
    data_format["light"] = light
    if weather == "rainny":
        weather = "rainy"
    data_format["weather"] = weather

    return data_format