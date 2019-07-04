from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import LSD2Card as l2d

digital_top_y = int(1 / 3 * 220)
digital_below_y = int(6 / 8 * 220)
digital_row = 20  # 大致号码高
digital_col = 295  # 大致号码宽


# 把像素点改为01格式，黑为1，白为0
def deal_pixel_01(img):
    img_copy = img.copy()
    img_copy[img == 0] = 1
    img_copy[img == 255] = 0
    return img_copy


# def scoop_img(pre_img, point_x, point_y, hei, wid):
# y轴投影
def picshadow_y(pre_img):
    shadow_y = np.sum(pre_img, 1)
    return shadow_y


# x轴投影
def picshadow_x(pre_img):
    shadow_x = np.sum(pre_img, 0)
    return shadow_x


# 找出连续20行黑色像素相加最大的那20行
def top_digital_y(shadow_y):   
    length_shadow = len(shadow_y) - digital_row
    max_shdaow = 0
    max_i = 0
    for i in range(length_shadow):
        sum_shadow = np.sum(shadow_y[i: i+ digital_row])
        if sum_shadow > max_shdaow:
            max_shdaow = sum_shadow
            max_i = i
    return max_i


# 根据阈值来精确划分
def set_threshold(shadow, x_y):
    sum_shadow = np.sum(shadow)
    if x_y:  # 垂直方向的阈值
        threshold = sum_shadow / (2 * digital_col)
    else:   # 水平方向的阈值
        threshold = sum_shadow / (2 * digital_row)
    return threshold


# 水平精确划分
def find_exact_y(approximately_shadow):
    app_y = picshadow_y(approximately_shadow)
    exact_top = 0
    exact_below = len(app_y)
    y_threshold = set_threshold(app_y, False)
    top_com = True  # top未找到时为true
    for i in range(exact_below):
        if app_y[i] > y_threshold:
            if top_com:
                exact_top = i
                top_com = False
            else:
                exact_below = i
    if exact_top > 2:
        exact_top = exact_top - 2
    if exact_below < len(app_y) - 2:
        exact_below = exact_below + 2
    return exact_top, exact_below


# 垂直精确划分   
def find_exact_x(approximatelx_shadow):
    app_x = picshadow_x(approximatelx_shadow)
    exact_left = 0
    exact_right = len(app_x)
    x_threshold = set_threshold(app_x, True)
    # print(approximatelx_shadow[:,20: 50])
    # print(x_threshold)
    left_com = True  # top未找到时为true
    for i in range(exact_right):
        if app_x[i] > x_threshold:
            if left_com:
                exact_left = i
                left_com = False
            else:
                exact_right = i
   
    if exact_left > 5:
        exact_left = exact_left - 5
    if exact_right < len(app_x) - 5:
        exact_right = exact_right + 5
    return exact_left, exact_right   

def processingOneT(contour_img):
    contour_img_copy = contour_img.copy()
    contour_img_copy = contour_img_copy[digital_top_y: digital_below_y,5 : digital_col]
    contour_img2gray = cv2.cvtColor(contour_img_copy, cv2.COLOR_RGB2GRAY)
#     cv2.imshow('crad_img2gray', crad_img2gray)
    # x = cv2.Sobel(contour_img2gray,cv2.CV_64F,1,0)
    # y = cv2.Sobel(contour_img2gray,cv2.CV_64F,0,1)
    # x_square = np.square(x)
    # y_square = np.square(y)
    # sobel_contour = np.sqrt(x_square + y_square)
    # sobel_contour = cv2.convertScaleAbs(sobel_contour)
    threshold = cv2.adaptiveThreshold(contour_img2gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,5,5)
    # threshold = cv2.threshold(contour_img2gray, 0, 255, cv2.THRESH_OTSU|cv2.THRESH_BINARY)[1]
# +
    # cv2.imshow('threshold', threshold)
    threshold_copy = threshold.copy()
    threshold_copy = deal_pixel_01(threshold_copy)
    top_y = top_digital_y(picshadow_y(threshold_copy))
    below_y = top_y + digital_row
    if top_y > 3:
        top_y = top_y - 3
    if below_y < digital_below_y - digital_top_y:
        below_y = below_y + 3
    contour_img_copy = contour_img_copy[top_y: below_y, 0 : digital_col]
    contour_img_threshold = threshold[top_y: below_y, 0 : digital_col]
    threshold_copy = threshold_copy[top_y: below_y, 0 : digital_col]

    # cv2.imshow('close1', contour_img_copy)
    # cv2.waitKey()
    # find_exact_x(threshold_copy)
    y_l = find_exact_y(threshold_copy)
    x_l = find_exact_x(threshold_copy)
    # print(y_l, x_l)
    contour_img_copy = contour_img_copy[y_l[0]: y_l[1], x_l[0] : x_l[1]]
    # cv2.imshow('close2', contour_img_copy)
    # cv2.waitKey()
    return contour_img_copy
    
    
num_img = processingOneT(l2d.cropped)