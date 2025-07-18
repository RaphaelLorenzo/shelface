# import torch
import argparse
import os
import cv2
import random
import numpy as np
import tkinter # just to get the height and width of the screen

root = tkinter.Tk()
root.withdraw()
SCREEN_WIDTH, SCREEN_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()

AVAILABLE_FACE_TYPES = ["still", "animated"]
here = os.path.dirname(__file__)
ANIMATIONS_DIR = os.path.join(here, "assets", "animations")


def write_centered_text(background_image, text, text_height_proportion=0.5):
    text_size = int(background_image.shape[0] * text_height_proportion / 20)
    text_height = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, text_size, text_size*2)[0][1]
    text_width = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, text_size, text_size*2)[0][0]
    text_x = (background_image.shape[1] - text_width) // 2
    text_y = text_height + (background_image.shape[0] - text_height) // 2
    cv2.putText(background_image, text, (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, text_size, (255, 255, 255), text_size*2)
    
    return background_image

def get_available_animations(animations_dir):
    # list all subdirectories in animations_dir
    return [d for d in os.listdir(animations_dir) if os.path.isdir(os.path.join(animations_dir, d))]


def display_face(face_list, frame_rate=30, args=None, bottom_text=None, bottom_text_height=150):
    counter = 0
    if args.screen_size == "full":
        cv2.namedWindow("Face", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Face", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
        cv2.namedWindow("Face", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Face", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        
    while True:
        if bottom_text is not None:
            face = face_list[counter]
            bg_image = np.zeros((bottom_text_height, SCREEN_WIDTH, 3), dtype=np.uint8)
            bg_image = write_centered_text(bg_image, bottom_text, text_height_proportion=0.5)
            face[-bg_image.shape[0]:, :] = bg_image
        else:
            face = face_list[counter]
        cv2.imshow("Face", face)
        key = cv2.waitKey(int(1000 / frame_rate))
        counter += 1
        counter %= len(face_list)
        if key == ord('q') or key == 27:
            break

def get_face_resized(face, mode, text_height=150):
    if args.resize_method == "pad":
        # pad in black and put the image in the center
        background = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)
        
        assert(SCREEN_HEIGHT > text_height*2), "Screen height is too small to reserve {} pixels for text".format(text_height)
        FACE_HEIGHT = SCREEN_HEIGHT - text_height
        
        face_height, face_width = face.shape[:2]
        x_offset = (SCREEN_WIDTH - face_width) // 2
        y_offset = (FACE_HEIGHT - face_height) // 2
        background[y_offset:y_offset+face_height, x_offset:x_offset+face_width] = face
        face = background
    
    elif args.resize_method == "resize_pad":
        # reserve 150 pixels at the bottom of the screen for text
        assert(SCREEN_HEIGHT > text_height*2), "Screen height is too small to reserve {} pixels for text".format(text_height)
        FACE_HEIGHT = SCREEN_HEIGHT - text_height
        
        # resize either to screen width or height, keeping aspect ratio
        face_height, face_width = face.shape[:2]
        
        # print("face aspect ratio : {}".format(face_width / face_height))
        # print("screen aspect ratio : {}".format(SCREEN_WIDTH / SCREEN_HEIGHT))
        
        if SCREEN_WIDTH / FACE_HEIGHT > face_width / face_height:
            new_width = int(FACE_HEIGHT * face_width / face_height)
            new_height = FACE_HEIGHT
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
        y_offset = (FACE_HEIGHT - resize_face_height) // 2
        background[y_offset:y_offset+resize_face_height, x_offset:x_offset+resize_face_width] = face
        face = background
        
    elif args.resize_method == "resize":
        assert(SCREEN_HEIGHT > text_height*2), "Screen height is too small to reserve {} pixels for text".format(text_height)
        FACE_HEIGHT = SCREEN_HEIGHT - text_height
        face = cv2.resize(face, (SCREEN_WIDTH, FACE_HEIGHT))
        
    return face

def main(args):
    
    if args.face_type == "still":
        face_dir = os.path.join(here, ANIMATIONS_DIR, args.face_name)
        face_images = [f for f in os.listdir(face_dir) if f.endswith(".jpg")]
        face_images.sort()
        
        random_face = random.choice(face_images)
        face_path = os.path.join(face_dir, random_face)
        face = cv2.imread(face_path)

        face = get_face_resized(face, args.resize_method)
        
        display_face([face], args=args, bottom_text=args.bottom_text, bottom_text_height=args.bottom_text_height)
    
    elif args.face_type == "animated":
        face_dir = os.path.join(here, ANIMATIONS_DIR, args.face_name)
        face_images = [f for f in os.listdir(face_dir) if f.endswith(".jpg")]
        face_images.sort()
        
        face_images = [cv2.imread(os.path.join(face_dir, f)) for f in face_images]
        face_images = [get_face_resized(f, args.resize_method) for f in face_images]
        
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
                
        display_face(face_images, frame_rate, args, bottom_text=args.bottom_text, bottom_text_height=args.bottom_text_height)
    
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--face_type", "-ft", type=str, default="animated")
    parser.add_argument("--face_name", "-n", type=str, default="random")
    parser.add_argument("--resize_method", "-r", type=str, default="resize_pad")
    parser.add_argument("--screen_size", "-ss", type=str, default="full")
    parser.add_argument("--bottom_text", "-bt", type=str, default=None)
    parser.add_argument("--bottom_text_height", "-bth", type=int, default=150)
    args = parser.parse_args()
    
    available_animations = get_available_animations(ANIMATIONS_DIR)
    if args.face_name == "random":
        args.face_name = random.choice(available_animations)
    
    print(f"Using face: {args.face_name}")
    
    assert(args.face_name in available_animations), f"Invalid face name: {args.face_name} (available: {available_animations})"
    assert(args.face_type in AVAILABLE_FACE_TYPES), f"Invalid face type: {args.face_type} (available: {AVAILABLE_FACE_TYPES})"
    assert(args.resize_method in ["pad", "resize", "resize_pad"]), f"Invalid full screen mode: {args.resize_method} (available: ['pad', 'resize', 'resize_pad'])"
    
    if args.screen_size != "full":
        SCREEN_WIDTH, SCREEN_HEIGHT = map(int, args.screen_size.split(","))
    else:
        SCREEN_WIDTH, SCREEN_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()
        print("Using full screen : {}x{}".format(SCREEN_WIDTH, SCREEN_HEIGHT))
        
    main(args)