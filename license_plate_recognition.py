import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage.io import imread
from skimage import measure
from skimage.transform import resize
from skimage.measure import regionprops
from skimage.filters import threshold_otsu
    
    
def license_plate_localization(image, threshold=-1, h=0.05, w=0.10, area=50, char_h=0.3, char_w=0.0, r_high=5, r_low=0.5, error=10):
    img = cv2.imread(image, 0)
    if (threshold == -1):
        threshold = threshold_otsu(img)
    ret, binary_img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    
    
    label_img = measure.label(binary_img)
    plate_dimensions = (h*label_img.shape[0], label_img.shape[0], w*label_img.shape[1], label_img.shape[1])
    min_height, max_height, min_width, max_width = plate_dimensions
    objects = []
    coordinates = []
    for region in regionprops(label_img):
        if (region.area < area):
            continue
    
        min_row, min_col, max_row, max_col = region.bbox
        height = max_row - min_row
        width = max_col - min_col
        if (height >= min_height and height <= max_height and width >= min_width and width <= max_width and width > height):
            objects.append(binary_img[min_row:max_row, min_col:max_col])
            coordinates.append(region)
    
    
    final_plates = []
    final_coordinates = []
    final_chars = []
    char_regions = []
    
    for i in range(len(objects)):
        plate = np.invert(objects[i])
        plate_labels = measure.label(plate)
        
        character_dimensions = (char_h*plate.shape[0], plate.shape[0], char_w*plate.shape[1], 0.25*plate.shape[1])
        min_height, max_height, min_width, max_width = character_dimensions
        
        characters = []
        char_reg = []
        
        for regions in regionprops(plate_labels):
            y0, x0, y1, x1 = regions.bbox
            region_height = y1 - y0
            region_width = x1 - x0
            
            ratio = float(region_height)/float(region_width)
            
            if (ratio > r_high or ratio < r_low):
                continue
        
            if (region_height > min_height and region_height < max_height and region_width > min_width and region_width < max_width):
                roi = plate[y0:y1, x0:x1]
        
                resized_char = resize(roi, (20, 20))
                characters.append(resized_char)
                char_reg.append(regions)
        f = 0
        new_chars = []
        char = []
        temp1 = []
        temp2 = []
        a = (0, 0)
        if (len(characters) >= 4):
            for j in range(len(characters)):
                for k in range(j+1, len(characters)):
    
                    m = a[0]
                    if (a == (0,0)):    
                        m = float(char_reg[j].bbox[0] - char_reg[k].bbox[0])/float(char_reg[j].bbox[1] - char_reg[k].bbox[1])
                    c = -1 * m * char_reg[k].bbox[1] + char_reg[k].bbox[0]
                    new_chars = []
                    char = []
                    for q in range(len(char_reg)):
                        l = char_reg[q]
                        y = m * l.bbox[1] + c
                        if (l.bbox[0] > int(y-error) and l.bbox[0] < int(y+error)):
                            new_chars.append(l)
                            char.append(characters[q])
                            
                    
                    if (len(char) >= 4):
                        if (a == (0, 0)):
                            temp1 = char[:]
                            temp2 = new_chars[:]
                            a = (m, c)
                        elif (a[1] > c+5 or a[1] < c-5):
                            temp1 = characters + char[:]
                            temp2 = char_reg + new_chars[:]
                            f = 1
                        break
                
                if (f == 1):
                    break
                
        characters = temp1[:]
        char_reg = temp2[:]
    
        temp1 = []
        temp2 = []
        a = (0, 0)
        f = 0
        if (len(characters) >= 4):
            for j in range(len(characters)):
                for k in range(j+1, len(characters)):
                    if (a == (0,0)):    
                        m = float(char_reg[j].bbox[2] - char_reg[k].bbox[2])/float(char_reg[j].bbox[3] - char_reg[k].bbox[3])
                    c = -1 * m * char_reg[k].bbox[3] + char_reg[k].bbox[2]
                    new_chars = []
                    char = []
                    for q in range(len(char_reg)):
                        l = char_reg[q]
                        y = m * l.bbox[3] + c
                        if (l.bbox[2] > int(y-error) and l.bbox[2] < int(y+error)):
                            new_chars.append(l)
                            char.append(characters[q])
                    if (len(char) >= 4):
                        if (a == (0, 0)):
                            temp1 = char[:]
                            temp2 = new_chars[:]
    
                            a = (m, c)
                        elif (a[1] > c+5 or a[1] < c-5):
                            temp1 = characters + char[:]
                            temp2 = char_reg + new_chars[:]
                            f = 1
                        break
                
                if (f == 1):
                    break
            
            
        char = temp1[:]
        char_reg = temp2[:]
        
        if (len(char) >= 4):
            final_plates.append(plate)
            final_coordinates.append(coordinates[i])
            final_chars.append(char)
            char_regions.append(new_chars)
        
        
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
        
        
    return (final_plates, final_coordinates, final_chars, char_regions)
