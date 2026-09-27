#!/usr/bin/python
import cv2
import numpy as np
import click
MIN_MATCH_COUNT=30

@click.command()
@click.argument('desktop_image', type=click.Path(exists=True))
@click.argument('target_image', type=click.Path(exists=True))
def match(desktop_image, target_image):
    # Read the images
    large_image = cv2.imread(desktop_image)
    small_image = cv2.imread(target_image)

    # Convert images to grayscale
    large_gray = cv2.cvtColor(large_image, cv2.COLOR_BGR2GRAY)
    small_gray = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)

    # Use SIFT to find keypoints and descriptors
    sift = cv2.SIFT_create()
    keypoints_1, descriptors_1 = sift.detectAndCompute(large_gray, None)
    keypoints_2, descriptors_2 = sift.detectAndCompute(small_gray, None)

    # Feature matching
    matcher = cv2.BFMatcher()
    matches = matcher.knnMatch(descriptors_1, descriptors_2, k=2)

    # Apply ratio test
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    if len(good) > MIN_MATCH_COUNT:
        # Extract location of good matches
        points1 = np.float32([ keypoints_1[m.queryIdx].pt for m in good ]).reshape(-1, 1, 2)
        points2 = np.float32([ keypoints_2[m.trainIdx].pt for m in good ]).reshape(-1, 1, 2)

        # Find homography
        matrix, mask = cv2.findHomography(points2, points1, cv2.RANSAC, 5.0)

        # Use homography to transform the corners of the small image to the large image


        h, w = small_image.shape[:2]
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, matrix)

        # Draw bounding box in the large image
        large_image_with_box = large_image.copy()
        large_image_with_box = cv2.polylines(large_image_with_box, [np.int32(dst)], True, (255, 0, 0), 3, cv2.LINE_AA)

        # Show or save the image
        #cv2.imshow('Detected Box', large_image_with_box)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        #print("Coordinates in large image:", dst)

        # Coordinates of the small image in the large image
        center_x = int((dst[0][0][0] + dst[1][0][0] + dst[2][0][0] + dst[3][0][0]) / 4)
        center_y = int((dst[0][0][1] + dst[1][0][1] + dst[2][0][1] + dst[3][0][1]) / 4)
        #center = (int(center_x), int(center_y))

            # Get dimensions of the large image
        #height_large, width_large = large_image.shape[:2]

        ## Convert center coordinates to percentages
        #center_x_percent = (center_x / width_large) * 950 
        #center_y_percent = (center_y / height_large) * 540

        print("-x {x} -y {y} -a".format(x=center_x,y=center_y))
    else:
        print("Not enough matches found - %d/%d" % (len(good), MIN_MATCH_COUNT))

if __name__ == "__main__":
    match()
