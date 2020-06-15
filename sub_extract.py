from os import path
from itertools import groupby
import glob
import json
from pathlib import Path
import pymkv
import subprocess

ROOT_PATH = Path("/mnt/d/shaft")
SOURCE_PATH = ROOT_PATH / Path("source")
SUB_PATH = ROOT_PATH / Path("subs")
FONT_TYPES = ["application/x-truetype-font", "application/vnd.ms-opentype"]

SUB_MAP = {
    "SubRip/SRT": "srt",
    "VobSub": "vob",
    "SubStationAlpha": "ssa"    
}

files = glob.glob(path.join(SOURCE_PATH , "**", "*.mkv"), recursive=True)

def get_mkv_data(file_path: str):
    information = json.loads(subprocess.check_output([
        "mkvmerge",
        "--identify",
        "-J",
        file_path]).decode())
    return information

for f in files:    
    sub_path = SUB_PATH / Path(f).relative_to(SOURCE_PATH)
    sub_path = Path(path.splitext(sub_path)[0])    
    print(sub_path)
    sub_path.mkdir(exist_ok=True, parents=True)
    information = get_mkv_data(f)

    attachments = information["attachments"]

    sub_tracks = [t for t in information["tracks"] if t["type"] == "subtitles"]

    track_map = { t["id"]: str(t["id"]) + "_" + t["properties"]["language"] + "." + SUB_MAP[t["codec"]]
    for t in sub_tracks}
    
    args = [
        "mkvextract",
        "attachments",
        f] + list(map(lambda a: f"{a['id']}:{sub_path / a['file_name']}", attachments))
    subprocess.check_output(args)
    

    args = [
        "mkvextract",
        "tracks",
        f] + [f"{k}:{sub_path / v}" for k,v in track_map.items()]
    subprocess.run(args, check=True)