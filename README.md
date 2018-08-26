# License-Plate-Recognition
This project is focused on license plate localization and recognition. Given an image of front or rear of the car the algorithm tries to localize the license plate and then carefully segments each character for predicting.

## Prerequisites
* Python 3.7 (lower versions also work correctly)
* OpenCV
* Numpy
* Matplotlib
* Skimage

## Getting Started
The main function in this project which user has to use is **license_plate_localization()**. The functions takes in the image of the front or rear of the car and outputs license plate and characters in order according to their position on the license plate.

## Arguments
* image - location/name of the image of front or rear of car from which the license plate is to be recognized
* threshold - the threshold which is used to create a binary image from the original image
* h - minimum height that the license plate can have with respect to the height of the image (fraction)
* w - minimum weight that the license plate can have with respect to the weight of the image (fraction)
* area - minimum area that the license plate can have in pixel<sup>2</sup>
* char_h - minimum height that the individual characters can have with respect to the height of the license plate (fraction)
* char_w - minimum weight that the individual characters can have with respect to the weight of the license plate (fraction)
* r_high - maximum height-by-width an individual character can have (fraction)
* r_low - minimum height-by-width an individual character can have (fraction)
* error - amount of error acceptable for the character to be in line

## Return Values
* final_plates - the image of the final accepted license plates in a list
* final_coordinates - a list of measure.regionprop object corresponding to each license plate is in final_plates which has all the possible information of the accepted plate
* final_chars - the image of the final accepted characters in a list for a particular accepted license plate. All such lists are in the a list
* char_regions - a list of measure.regionprop object corresponding to each character. All such lists for each accepted license plate is in a list which is char_regions

## Result
