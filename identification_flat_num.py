import ocr_findnum_position as fn
import cv2
import numpy as np

num_img= fn.num_img
width = np.shape(num_img)[1]
height = np.shape(num_img)[0]


def eliminate_pattern(num_ther_img, pattern_img):
    num_ther_copy = num_ther_img.copy()
    width = np.shape(num_img)[1]
    height = np.shape(num_img)[0] 
    for wid in range(width):
        for hei in range(height):
            if pattern_img[hei, wid] == 255 and num_ther_img[hei, wid] == 255:
                num_ther_copy[hei, wid] = 0
    return num_ther_copy


def get_sobel(contour_img2gray):
    x = cv2.Sobel(contour_img2gray,cv2.CV_64F,1,0)
    y = cv2.Sobel(contour_img2gray,cv2.CV_64F,0,1)
    x_square = np.square(x)
    y_square = np.square(y)
    sobel_contour = np.sqrt(x_square + y_square)
    sobel_contour = cv2.convertScaleAbs(sobel_contour)
    threshold = cv2.adaptiveThreshold(sobel_contour,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,3,5)
    return threshold


def drop_little(eliminate_pic):
    eliminate_pic_01 = fn.deal_pixel_01(eliminate_pic)
    shadow_x = fn.picshadow_x(eliminate_pic_01)
    thre = height - 3
    for i in range(width):
        if shadow_x[i] > thre:
            eliminate_pic[:,i] = 0
    return eliminate_pic


def find_singledigital(shadow_pic):
    single_digital_list = []
    single_start = 0
    single_end = 0
    is_start = True  # True表示再寻找下一个数字的开头
    thre = width / 55
    for i in range(width):
        if is_start:
            if shadow_pic[i] < height:
                single_start = i
                is_start = False
        else:
            if shadow_pic[i] == height:
                single_end = i
                is_start = True
                if single_end - single_start > thre:
                    single_digital_list.append([single_start, single_end])
    return single_digital_list



num_img2gray = cv2.cvtColor(num_img, cv2.COLOR_RGB2GRAY)
threshold = cv2.adaptiveThreshold(num_img2gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,5,5)

for i in range(np.shape(threshold)[1]):
    for j in range(np.shape(threshold)[0]):
        if threshold[j, i] == 0:
             threshold[j, i] = 255
        else:
           threshold[j, i] = 0 
cv2.imshow('threshold', threshold)

drop_num = drop_little(threshold)
cv2.imshow('drop_num', drop_num)
eliminate_pic_01 = fn.deal_pixel_01(drop_num)
shadow_x = fn.picshadow_x(eliminate_pic_01)
digital_list = find_singledigital(shadow_x)
cv2.waitKey()    