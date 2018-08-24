import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage.io import imread
from skimage import measure
from skimage.transform import resize
from skimage.measure import regionprops
from skimage.filters import threshold_otsu
    
    
def plate_regions(label_img, binary_img, plate_dimensions, area):
    objects = []
    coordinates = []
    min_height, max_height, min_width, max_width = plate_dimensions
    
    # Eliminate all the regions which do not satisfy min, max constraints and return cropped regions and their coordinates
    for region in regionprops(label_img):
        if (region.area < area):
            continue
    
        min_row, min_col, max_row, max_col = region.bbox
        height = max_row - min_row
        width = max_col - min_col
        if (height >= min_height and height <= max_height and width >= min_width and width <= max_width and width > height):
            objects.append(binary_img[min_row:max_row, min_col:max_col])
            coordinates.append(region)
    return objects, coordinates



def character_regions(plate, character_dimensions, r_high, r_low):
    characters = []
    char_reg = []
    plate_labels = measure.label(plate)
    
    min_height, max_height, min_width, max_width = character_dimensions
    
    # Eliminate all the regions which do not satisfy min, max constraints and return cropped regions and their coordinates
    for regions in regionprops(plate_labels):
        y0, x0, y1, x1 = regions.bbox
        region_height = y1 - y0
        region_width = x1 - x0
            
        # Constraint on the height/width ratio of character
        ratio = float(region_height)/float(region_width)    
        if (ratio > r_high or ratio < r_low):
            continue
        
        if (region_height > min_height and region_height < max_height and region_width > min_width and region_width < max_width):
            roi = plate[y0:y1, x0:x1]
    
            resized_char = resize(roi, (20, 20))
            characters.append(resized_char)
            char_reg.append(regions)
            
    return characters, char_reg
    
    
    
def char_inline(characters, char_reg, error, corner):
    f = 0
    temp1 = []
    temp2 = []
    a = (0, 0)
    new_chars = []
    char = []
    
    # Reject the candidate plate region if it has less than 4 possible characters
    if (len(characters) >= 4):
        
        # For each pair of candidate character regions calculate equation of line for a corner to check other characters aligned to it
        for j in range(len(characters)):
            for k in range(j+1, len(characters)):
                m = a[0]
                if (a == (0,0)):    
                    m = float(char_reg[j].bbox[corner] - char_reg[k].bbox[corner])/float(char_reg[j].bbox[corner+1] - char_reg[k].bbox[corner+1])
                c = -1 * m * char_reg[k].bbox[corner+1] + char_reg[k].bbox[corner]
                new_chars = []
                char = []
                for q in range(len(char_reg)):
                    l = char_reg[q]
                    y = m * l.bbox[corner+1] + c
                    
                    # If some other pair have similar equation with slight error then include it
                    if (l.bbox[corner] > int(y-error) and l.bbox[corner] < int(y+error)):
                        new_chars.append(l)
                        char.append(characters[q])
                            
                # If we can find atleast 4 characters in line they are very likely a line of characters
                if (len(char) >= 4):
                    
                    # We allow 2 different equations as some license plate have number in 2 lines of 2 font sizes
                    if (a == (0, 0)):
                        temp1 = char[:]
                        temp2 = new_chars[:]
                        a = (m, c)
                        
                    # Second equation must be considerably different
                    elif (a[1] > c+5 or a[1] < c-5):
                        temp1 = characters + char[:]
                        temp2 = char_reg + new_chars[:]
                        f = 1
                    break
                    
            if (f == 1):
                break

    return temp1, temp2, new_chars, char

                
    
def result_display(image, final_coordinates, final_plates, char_regions):
    img = imread(image)
    fig, (ax1) = plt.subplots(1)
    ax1.imshow(img);
    
    for region in final_coordinates:
        min_row, min_col, max_row, max_col = region.bbox
        height = max_row - min_row
        width = max_col - min_col
        rectBorder = patches.Rectangle((min_col, min_row), max_col-min_col, max_row-min_row, edgecolor="red", linewidth=2, fill=False)
        ax1.add_patch(rectBorder)
    plt.show()
    
    
    for i in range(len(final_plates)):
        fig, (ax1) = plt.subplots(1)
        ax1.imshow(final_plates[i], cmap="gray");
        for region in char_regions[i]:
            min_row, min_col, max_row, max_col = region.bbox
            height = max_row - min_row
            width = max_col - min_col
            rectBorder = patches.Rectangle((min_col, min_row), max_col-min_col, max_row-min_row, edgecolor="red", linewidth=2, fill=False)
            ax1.add_patch(rectBorder)
        plt.show()
                


def license_plate_localization(image, threshold=-1, h=0.05, w=0.10, area=50, char_h=0.3, char_w=0.0, r_high=5, r_low=0.5, error=10):
    # Use grayscale image of the car
    img = cv2.imread(image, 0)
    if (threshold == -1):
        threshold = threshold_otsu(img)
        
    # Convert the image into a binary image using a threshold on the grayscale image
    ret, binary_img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    
    # Label different pieces of the image 
    label_img = measure.label(binary_img)
    
    # Define the max. and min. height and width that license might have (this helps in elimination of useless regions)
    plate_dimensions = (h*label_img.shape[0], label_img.shape[0], w*label_img.shape[1], label_img.shape[1])
    
    # Find all possible regions of licenses plate
    objects, coordinates = plate_regions(label_img, binary_img, plate_dimensions, area)
    
    final_plates = []
    final_coordinates = []
    final_chars = []
    char_regions = []
    
    # For each possible region find possible characters and eliminate plates further and return final characters
    for i in range(len(objects)):
        plate = np.invert(objects[i])
        
        # Define the max. and min. height and width that character might have w.r.t dimensions of plate
        character_dimensions = (char_h*plate.shape[0], plate.shape[0], char_w*plate.shape[1], 0.25*plate.shape[1])
        
        # Find all possible regions of characters in the licenses plate
        characters, char_reg = character_regions(plate, character_dimensions, r_high, r_low)
        
        # Filter character regions based on left lower corner
        temp1, temp2, new_chars, char = char_inline(characters, char_reg, error, 0)
        
        # Narrow down the regions
        characters = temp1[:]
        char_reg = temp2[:]
    
        # Filter character regions based on top right corner
        temp1, temp2, new_chars, char = char_inline(characters, char_reg, error, 2)
    
        char = temp1[:]
        char_reg = temp2[:]
        
        # Final character regions without order
        if (len(char) >= 4):
            final_plates.append(plate)
            final_coordinates.append(coordinates[i])
            final_chars.append(char)
            char_regions.append(new_chars)
        
    # Order the characters as they are on the plate
    chars = []
    regions = []
    for j in range(len(final_chars)):
        temp = list(zip(final_chars[j], char_regions[j]))
        temp.sort(key = lambda x:x[1].bbox[1])
        temp1 = [temp[0][0]]
        temp2 = [temp[0][1]]
        
        for i in range(1, len(temp)):
            if (temp2[len(temp2)-1].bbox != temp[i][1].bbox):
                temp1.append(temp[i][0])
                temp2.append(temp[i][1])
                
        chars.append(temp1)
        regions.append(temp2)
    
    final_chars = chars[:]
    char_regions = regions[:]
    
    # Visualizing the results
    result_display(image, final_coordinates, final_plates, char_regions)    
        
    return (final_plates, final_coordinates, final_chars, char_regions)
