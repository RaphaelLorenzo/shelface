# import torch
import argparse
import os
import sys
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")
import sys
from PIL import Image
import datetime
import cv2
import random

import tkinter #python 3 syntax
import numpy as np

root = tkinter.Tk()
root.withdraw()

SCREEN_WIDTH, SCREEN_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()

AVAILABLE_FACE_TYPES = ["still", "animated"]
here = os.path.dirname(__file__)
ANIMATIONS_DIR = os.path.join(here, "assets", "animations")


def get_available_animations(animations_dir):
    # list all subdirectories in animations_dir
    return [d for d in os.listdir(animations_dir) if os.path.isdir(os.path.join(animations_dir, d))]


def display_face(face_list, frame_rate=30):
    counter = 0
    cv2.namedWindow("Face", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Face", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    while True:
        cv2.imshow("Face", face_list[counter])
        key = cv2.waitKey(int(1000 / frame_rate))
        counter += 1
        counter %= len(face_list)
        if key == ord('q') or key == 27:
            break

def get_face_resized(face, mode):
    if args.full_screen == "pad":
        # pad in black and put the image in the center
        background = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)
        face_height, face_width = face.shape[:2]
        x_offset = (SCREEN_WIDTH - face_width) // 2
        y_offset = (SCREEN_HEIGHT - face_height) // 2
        background[y_offset:y_offset+face_height, x_offset:x_offset+face_width] = face
        face = background
    
    elif args.full_screen == "resize_pad":
        # resize either to screen width or height, keeping aspect ratio
        face_height, face_width = face.shape[:2]
        
        # print("face aspect ratio : {}".format(face_width / face_height))
        # print("screen aspect ratio : {}".format(SCREEN_WIDTH / SCREEN_HEIGHT))
        
        if SCREEN_WIDTH / SCREEN_HEIGHT > face_width / face_height:
            new_width = int(SCREEN_HEIGHT * face_width / face_height)
            new_height = SCREEN_HEIGHT
            face = cv2.resize(face, (new_width, new_height))
            # print("Resized to height : {}x{}".format(new_width, new_height))
        else:
            new_width = SCREEN_WIDTH
            new_height = int(SCREEN_WIDTH * face_height / face_width)
            face = cv2.resize(face, (new_width, new_height))
            # print("Resized to width : {}x{}".format(new_width, new_height))
        
        # pad in black and put the image in the center
        background = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)
        resize_face_height, resize_face_width = face.shape[:2]
        x_offset = (SCREEN_WIDTH - resize_face_width) // 2
        y_offset = (SCREEN_HEIGHT - resize_face_height) // 2
        background[y_offset:y_offset+resize_face_height, x_offset:x_offset+resize_face_width] = face
        face = background
        
    elif args.full_screen == "resize":
        face = cv2.resize(face, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
    return face

def main(args):
    
    if args.face_type == "still":
        face_dir = os.path.join(here, ANIMATIONS_DIR, args.face_name)
        face_images = [f for f in os.listdir(face_dir) if f.endswith(".jpg")]
        face_images.sort()
        
        random_face = random.choice(face_images)
        face_path = os.path.join(face_dir, random_face)
        face = cv2.imread(face_path)

        face = get_face_resized(face, args.full_screen)
        
        display_face([face])
    
    elif args.face_type == "animated":
        face_dir = os.path.join(here, ANIMATIONS_DIR, args.face_name)
        face_images = [f for f in os.listdir(face_dir) if f.endswith(".jpg")]
        face_images.sort()
        
        face_images = [cv2.imread(os.path.join(face_dir, f)) for f in face_images]
        face_images = [get_face_resized(f, args.full_screen) for f in face_images]
        
        info_file = os.path.join(face_dir, "info.txt")
        if os.path.exists(info_file):
            duration = None
            with open(info_file, "r") as f:
                for line in f:
                    txt = line.strip()
                    if "Duration" in txt:
                        duration = float(txt.split(":")[1].strip().replace("s", ""))
            if duration is None:
                frame_rate = 30
            else:
                frame_rate = len(face_images) / duration
        else:
            print("No info file found")
            frame_rate = 30
                
        display_face(face_images, frame_rate)
    
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--face_type", "-ft", type=str, default="still")
    parser.add_argument("--face_name", "-n", type=str, default="green_square")
    parser.add_argument("--full_screen", "-fs", type=str, default="resize_pad")
    parser.add_argument("--screen_size", "-ss", type=str, default="2160,1080")
    args = parser.parse_args()
    
    available_animations = get_available_animations(ANIMATIONS_DIR)
    assert(args.face_name in available_animations), f"Invalid face name: {args.face_name} (available: {available_animations})"
    assert(args.face_type in AVAILABLE_FACE_TYPES), f"Invalid face type: {args.face_type} (available: {AVAILABLE_FACE_TYPES})"
    assert(args.full_screen in ["pad", "resize", "resize_pad"]), f"Invalid full screen mode: {args.full_screen} (available: ['pad', 'resize', 'resize_pad'])"
    
    if args.screen_size != "full":
        SCREEN_WIDTH, SCREEN_HEIGHT = map(int, args.screen_size.split(","))
    else:
        print("Using full screen")
        SCREEN_WIDTH, SCREEN_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()

    main(args)