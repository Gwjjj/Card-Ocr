"""
LSD 识别出银行卡卡的位置
"""
import imutils
import cv2
import numpy as np
import math

# 银行卡目录
PIC_DIR = './Resource_card/test_images/'
# 确定图片四周的宽度内做筛选银行卡边框，这个宽度定为50
tempWidth = 70
# 图片Resize大小
pic_width = 500
pic_height = 360
l_list = []
r_list = []
t_list = []
b_list = []


# 判断点在矩形内,把贴边的去掉
def in_rect_bool(cv_point_x, cv_point_y, cv_rect):
    if ((cv_point_x > cv_rect[0]) and (cv_point_x < (cv_rect[0] + cv_rect[2]))) and (
            (cv_point_y > cv_rect[1]) and (cv_point_y < (cv_rect[1] + cv_rect[3]))):
        return True
    else:
        return False


# 计算两点之间的距离
def lenght_of_2point(cv_point1_x, cv_point1_y, cv_point2_x, cv_point2_y):
    return math.sqrt(math.pow(cv_point1_x - cv_point2_x, 2) + math.pow(cv_point1_y - cv_point2_y, 2))


def get_angle(start_x, start_y, end_x, end_y):
    if abs(start_x - end_x) > 0:
        angle = math.atan((start_y - end_y) / (start_x - end_x)) * 180 / 3.1416
    else:
        angle = 90.0
    return angle


# 在图片边缘挑选线段
def selected_lines(line_length, points, per_lines):
    b_anglelist = []
    rect_l = [0, 0, tempWidth, pic_height]  # 图片左边部分
    rect_r = [pic_width - tempWidth, 0, tempWidth, pic_height]  # 图片右边部分
    rect_t = [0, 0, pic_width, tempWidth]  # 图片上边部分
    rect_b = [0, pic_height - tempWidth, pic_width, tempWidth]  # 图片下边部分
    for i in range(line_length):
        point = points[i][0]
        start_x = point[0]
        start_y = point[1]
        end_x = point[2]
        end_y = point[3]
        angle = get_angle(start_x, start_y, end_x, end_y)
        if lenght_of_2point(start_x, start_y, end_x, end_y) > 20:
            if ((in_rect_bool(start_x, start_y, rect_l) or in_rect_bool(end_x, end_y, rect_l)) and (
                    (angle < -70) or (angle > 70))):
                l_list.append(per_lines[0][i])
                # l_anglelist.append(angle)
            if ((in_rect_bool(start_x, start_y, rect_r) or in_rect_bool(end_x, end_y, rect_r)) and (
                    (angle < -70) or (angle > 70))):
                r_list.append(per_lines[0][i])
                # r_anglelist.append(angle)
            if ((in_rect_bool(start_x, start_y, rect_t) or in_rect_bool(end_x, end_y, rect_t)) and (
                    (angle > -20) and (angle < 20))):
                t_list.append(per_lines[0][i])
                # t_anglelist.append(angle)
            if (in_rect_bool(start_x, start_y, rect_b or in_rect_bool(end_x, end_y, rect_b)) and (
                    (angle > -20) and (angle < 20))):
                b_list.append(per_lines[0][i])
                b_anglelist.append(angle)
    return b_anglelist


# 线段合并并找出个方向最长线段
def merge_line():
    horizontal_merge(t_list)
    horizontal_merge(b_list)
    vertical_merge(l_list)
    vertical_merge(r_list)
    return [choose_max_line(t_list), choose_max_line(b_list), choose_max_line(l_list), choose_max_line(r_list)]


# 线段列表中选择最长的线段
def choose_max_line(choose_line):
    max_line_length = 0
    max_line = choose_line[0]
    for choo_line in choose_line:
        choo_line_in = choo_line[0]
        length_l = lenght_of_2point(choo_line_in[0], choo_line_in[1], choo_line_in[2], choo_line_in[3])
        if length_l > max_line_length:
            max_line_length = length_l
            max_line = choo_line
    return max_line


# 纵向合并  [start_x, start_y, end_x, end_y]
def vertical_merge(ver_lines_list):
    # 确定所有线段都是首高于尾部(以y轴为参考计算)
    for ver_lines in ver_lines_list:
        ver_lines = ver_lines[0]
        if ver_lines[1] > ver_lines[3]:
            temp = ver_lines[2]
            ver_lines[2] = ver_lines[0]
            ver_lines[0] = temp
            temp = ver_lines[3]
            ver_lines[3] = ver_lines[1]
            ver_lines[1] = temp
    # 符合条件合并
    for ver_lines1 in ver_lines_list:
        ver_lines1 = ver_lines1[0]
        for ver_lines2 in ver_lines_list:
            ver_lines2 = ver_lines2[0]
            if (ver_lines1[1] - ver_lines2[1] < 0) and abs(ver_lines1[0] - ver_lines2[2]) < 10 and abs(
                    ver_lines1[2] - ver_lines2[0]) < 10 and abs(
                ver_lines1[3] - ver_lines2[1]) < 10:
                new_merge_line = np.array([[ver_lines1[0], ver_lines1[1], ver_lines2[2], ver_lines2[3]]])
                ver_lines_list.append(new_merge_line)


# 横向合并  [start_x, start_y, end_x, end_y]
def horizontal_merge(hor_lines_list):
    # 确定所有线段都是首小于尾部(以X轴为参考计算)
    for hor_lines in hor_lines_list:
        hor_lines = hor_lines[0]
        if hor_lines[0] > hor_lines[2]:
            temp = hor_lines[2]
            hor_lines[2] = hor_lines[0]
            hor_lines[0] = temp
            temp = hor_lines[3]
            hor_lines[3] = hor_lines[1]
            hor_lines[1] = temp
    # 符合条件合并
    for hor_lines1 in hor_lines_list:
        hor_lines1 = hor_lines1[0]
        for hor_lines2 in hor_lines_list:
            hor_lines2 = hor_lines2[0]
            if (hor_lines1[0] - hor_lines2[0] < 0) and abs(hor_lines1[3] - hor_lines2[1]) < 10 and abs(
                    hor_lines1[1] - hor_lines2[3]) < 10 and abs(
                hor_lines1[2] - hor_lines2[0]) < 10:
                new_merge_line = np.array([[hor_lines1[0], hor_lines1[1], hor_lines2[2], hor_lines2[3]]])
                hor_lines_list.append(new_merge_line)
                # print('success', newmerge_line, hor_lines1, hor_lines2)


# 两线交点
def get_cross_point(line_a, line_b):
    line_a = line_a[0]
    line_b = line_b[0]
    ka = (line_a[3] - line_a[1]) / (line_a[2] - line_a[0])  # 求出LineA斜率
    kb = (line_b[3] - line_b[1]) / (line_b[2] - line_b[0])  # 求出LineB斜率
    ka_kb = ka - kb
    cross_point_x = (ka * line_a[0] - line_a[1] - kb * line_b[0] + line_b[1]) / (ka - kb)
    cross_point_y = (ka * kb * (line_a[0] - line_b[0]) + ka * line_b[1] - kb * line_a[1]) / (ka - kb)
    return_tupe = (cross_point_x, cross_point_y)
    return return_tupe


# 一点围绕点旋转后的坐标
def getRotatePoint(angle, valuex, valuey, pointx, pointy):
    angle = math.radians(angle)
    nRotatex = (valuex - pointx) * math.cos(angle) - (valuey - pointy) * math.sin(angle) + pointx
    nRotatey = (valuex - pointx) * math.sin(angle) + (valuey - pointy) * math.cos(angle) + pointy
    return np.float32(nRotatex), np.float32(nRotatey)


# 找出点中横竖坐标中的最大值
def find_max(points):
    max_x = 0
    max_y = 0
    min_x = pic_width
    min_y = pic_height
    for point in points:
        if point[0] > max_x:
            max_x = point[0]
        if point[0] < min_x:
            min_x = point[0]
        if point[1] > max_y:
            max_y = point[1]
        if point[1] < min_y:
            min_y = point[1]
    return min_x, min_y, max_x, max_y


# 读取图片
crad_img = cv2.imread(PIC_DIR + '6.jpeg')
crad_img = imutils.resize(crad_img, width=pic_width, height=pic_height)
# msf_image = cv2.pyrMeanShiftFiltering(crad_img, 30, 20)  # 均值偏移滤波降噪
msf_image = cv2.GaussianBlur(crad_img, (3, 3), 1)
crad_img2gray = cv2.cvtColor(msf_image, cv2.COLOR_RGB2GRAY)  # 灰度处理
canny_img = cv2.Canny(crad_img2gray, 50, 100)
threshold = cv2.threshold(canny_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
lsd = cv2.createLineSegmentDetector(0)
lines = lsd.detect(threshold)  # lines[point, width, precision, null]的point
points_list = lines[0]  # [start_x, start_y, end_x, end_y] 起始点
# draw_pre = lsd.drawSegments(crad_img, np.array(points_list))
# cv2.imshow('draw_pre', draw_pre)
len_line = len(points_list)  # 线段个数
point_list = []
b_anglelist = selected_lines(len_line, points_list, lines)
point_list.extend(l_list)
point_list.extend(l_list)
point_list.extend(t_list)
point_list.extend(b_list)

final_line = merge_line()
lt = get_cross_point(final_line[0], final_line[2])  # 左上角的点
rt = get_cross_point(final_line[0], final_line[3])  # 右上角的点
lb = get_cross_point(final_line[1], final_line[2])  # 左下角的点
rb = get_cross_point(final_line[1], final_line[3])  # 右下角的点

# tran_angle = (get_angle(lt[0], lt[1], rt[0], rt[1]) + get_angle(lb[0], lb[1], rb[0], rb[1])) / 2
# M = cv2.getRotationMatrix2D((pic_width / 2, pic_height / 2), tran_angle, 1.0)
# img_ro = cv2.warpAffine(crad_img, M, (pic_width, pic_height))
# tran_lt = getRotatePoint(-tran_angle, lt[0], lt[1], pic_width / 2, pic_height / 2)
# tran_rt = getRotatePoint(-tran_angle, rt[0], rt[1], pic_width / 2, pic_height / 2)
# tran_lb = getRotatePoint(-tran_angle, lb[0], lb[1], pic_width / 2, pic_height / 2)
# tran_rb = getRotatePoint(-tran_angle, rb[0], rb[1], pic_width / 2, pic_height / 2)
# cv2.circle(img_ro, tran_lt, 10, (255, 200, 255))
# cv2.circle(img_ro, tran_rt, 10, (255, 200, 255))
# cv2.circle(img_ro, tran_lb, 10, (255, 200, 255))                
# cv2.circle(img_ro, tran_rb, 10, (255, 200, 255))
# draw_pre = lsd.drawSegments(crad_img, np.array(final_line))
# cv2.imshow('draw_pre', draw_pre)
# max_point = find_max([tran_lt, tran_rt, tran_lb, tran_rb])
# # print(max_point)
# cropped = img_ro[int(max_point[1]) + 10:int(max_point[3]) - 10,
#           int(max_point[0]) + 16:int(max_point[2]) - 16]  # 裁剪坐标为[y0:y1, x0:x1] 
pts1 = np.float32([lt, rt, lb, rb])
pts2 = np.float32([[0, 0],[300,0],[0, 220],[300,220]])

# # 生成透视变换矩阵；进行透视变换
tran_m = cv2.getPerspectiveTransform(pts1, pts2)
cropped = cv2.warpPerspective(crad_img, tran_m, (300,220))
# cv2.imshow('cropped', cropped)
# cv2.waitKey()