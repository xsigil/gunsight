#!/usr/bin/env python3
import sys
import cv2
import numpy as np
import click

MIN_MATCH_COUNT = 30

@click.command()
@click.argument('desktop_image', type=click.Path(exists=True))
@click.argument('target_image', type=click.Path(exists=True))
@click.option('--min-matches', default=MIN_MATCH_COUNT, help='Minimum feature matches required.')
@click.option('--raw', is_flag=True, help='Output only "X Y" coordinate pair instead of click flags.')
def main(desktop_image, target_image, min_matches, raw):
    """Robust, scale-invariant GUI target locator using SIFT and Homography."""
    large_image = cv2.imread(desktop_image)
    small_image = cv2.imread(target_image)

    if large_image is None or small_image is None:
        click.echo("Error: Unable to load one or both images.", err=True)
        sys.exit(2)

    large_gray = cv2.cvtColor(large_image, cv2.COLOR_BGR2GRAY)
    small_gray = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()
    keypoints_1, descriptors_1 = sift.detectAndCompute(large_gray, None)
    keypoints_2, descriptors_2 = sift.detectAndCompute(small_gray, None)

    if descriptors_1 is None or descriptors_2 is None:
        click.echo("Error: Insufficient features found.", err=True)
        sys.exit(1)

    matcher = cv2.BFMatcher()
    matches = matcher.knnMatch(descriptors_1, descriptors_2, k=2)

    # Lowe's ratio test
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    if len(good) >= min_matches:
        points1 = np.float32([keypoints_1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        points2 = np.float32([keypoints_2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        matrix, _ = cv2.findHomography(points2, points1, cv2.RANSAC, 5.0)
        if matrix is None:
            click.echo("Error: Homography computation failed.", err=True)
            sys.exit(1)

        h, w = small_image.shape[:2]
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, matrix)

        center_x = int((dst[0][0][0] + dst[1][0][0] + dst[2][0][0] + dst[3][0][0]) / 4)
        center_y = int((dst[0][0][1] + dst[1][0][1] + dst[2][0][1] + dst[3][0][1]) / 4)

        if raw:
            click.echo(f"{center_x} {center_y}")
        else:
            # Default: cliclick style flags
            click.echo(f"-x {center_x} -y {center_y} -a")
        sys.exit(0)
    else:
        click.echo(f"Not enough matches found - {len(good)}/{min_matches}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
