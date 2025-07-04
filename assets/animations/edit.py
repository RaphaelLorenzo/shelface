import cv2
import os
import argparse


def main(args):
    # Ensure input directory exists
    if not os.path.exists(args.input_dir):
        print(f"Input directory {args.input_dir} does not exist")
        return

    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(args.input_dir), "output")
    os.makedirs(output_dir, exist_ok=True)

    mask = cv2.imread(args.mask_path, cv2.IMREAD_GRAYSCALE)

    # Process each image in input directory
    for filename in os.listdir(args.input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Read image and mask
            img_path = os.path.join(args.input_dir, filename)

            # Read image and mask
            img = cv2.imread(img_path)

            # Ensure mask and image have same dimensions
            if img.shape[:2] != mask.shape[:2]:
                mask = cv2.resize(mask, (img.shape[1], img.shape[0]))

            # Apply mask - set pixels to black (0) where mask is white (255)
            img[mask == 255] = 0

            # Save result
            output_path = os.path.join(output_dir, f"{filename}")
            cv2.imwrite(output_path, img)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", "-i", type=str, default="data/input")
    parser.add_argument("--mask_path", "-m", type=str, default="data/mask.png")
    args = parser.parse_args()

    main(args)