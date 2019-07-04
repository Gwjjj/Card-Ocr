import identification_flat_num as etp
import ocr_findnum_position as fn
import cv2
import numpy as np


thre = 12  # 字符大致宽度
num_img = etp.num_img
num_img2gray = etp.num_img2gray
width = np.shape(num_img)[1]
height = np.shape(num_img)[0]
# cv2.imshow('num_img', num_img)


def merge_nums(numslist, single):
    if single < len(numslist):
        single = merge_iter(single, numslist)
        merge_nums(nums_list, single)
    return numslist


def merge_iter(single_i, numslist):
    nums = numslist[single_i]
    nums_width = nums[1] - nums[0]
    number_num = (nums_width / thre) - int(nums_width / thre) 
    if 0.25 < number_num < 0.75:
        a = True
        if single_i > 0:
            pre_nums = numslist[single_i - 1]
            if nums[0] - pre_nums[1] < 3:  # 与前一个合并
                numslist[single_i-1] = [pre_nums[0], nums[1]]
                numslist.remove(numslist[single_i])
                single_i = single_i - 1
                a = False
        if single_i < len(numslist) - 1 and a:
            atf_nums = numslist[single_i + 1]
            if atf_nums[0] - nums[1] < 3:
                numslist[single_i]= [nums[0], atf_nums[1]]
                numslist.remove(numslist[single_i + 1])
    single_i = single_i + 1
    return single_i


def split_single(nums_img, i):
    spilt_num_list = []
    nums_width = nums_img[1] - nums_img[0]
    except_num = int(nums_width / thre)
    minus = (nums_width / thre) - except_num
    if minus < 0.3 or minus > 0.7:
        number_num = int(nums_width / thre + 0.3)
        if 0.1 < minus < 0.25:
            nums_img[0] = nums_img[0] + 1
            nums_img[1] = nums_img[1] - 1
        elif 0.7 < minus <= 0.84:
            if nums_img[0] > 1:
                nums_img[0] = nums_img[0] - 2
            if nums_img[1] < width - 2:
                nums_img[1] = nums_img[1] + 2
        elif  minus > 0.84:
               if nums_img[0] > 0:
                    nums_img[0] = nums_img[0] - 1
               if nums_img[1] < width - 1:
                    nums_img[1] = nums_img[1] + 1
        if number_num == 1:
            spilt_num_list.append([nums_img[0], nums_img[1]])
        else:
            for i in range(number_num):
                spilt_num_list.append([nums_img[0] + thre * i, nums_img[0] + thre * (i+1) - 1])
    else:
        picc = num_img2gray[0: height, nums_img[0]: nums_img[1]]
        canny_num = cv2.Canny(picc, 40, 145)
        # cv2.imshow('canny_num' + str(i), canny_num)
        judge = drop_over(canny_num, nums_width % thre)
        print('judge', judge, nums_img)
        if judge != 0:
            if judge == 1:
                nums_img = [nums_img[0], nums_img[1] - (nums_width % thre)]
                spilt_aga_list = split_single(nums_img, i)
                if spilt_aga_list != []:
                    spilt_num_list.extend(spilt_aga_list)
                # picm = num_img[0: height, nums_img[0]: nums_img[1]]
                # cv2.imshow('picm' + str(i), picm)
            elif judge == 2:
                nums_img = [nums_img[0] + (nums_width % thre), nums_img[1]]
                spilt_aga_list = split_single(nums_img, i)
                if spilt_aga_list != []:
                    spilt_num_list.extend(spilt_aga_list)
                # picm = num_img[0: height, nums_img[0]: nums_img[1]]
                # cv2.imshow('picm' + str(i), picm)
            elif judge == 3:
                # print('nums_img',  nums_img)
                # picm = num_img[0: height, nums_img[0]: nums_img[1]]
                # cv2.imshow('picm' + str(i), picm)
                if nums_img[0] > 0:
                    nums_img[0] = nums_img[0] - 1
                if nums_img[1] < width - 1:
                    nums_img[1] = nums_img[1] + 1   
                spilt_num_list.append([nums_img[0], nums_img[1]]) 
            else:
                aga_list = judge
                for s in range(len(aga_list)):
                    aga_list[s][0] = aga_list[s][0] + nums_img[0]
                    aga_list[s][1] = aga_list[s][1] + nums_img[0]
                for aga in aga_list:
                    spilt_aga_list = split_single(aga, i)
                    if spilt_aga_list != []:
                        spilt_num_list.extend(spilt_aga_list)
    return spilt_num_list


def drop_over(over_canny, over_width):
    over_canny_width = np.shape(over_canny)[1]
    over_left = over_width / 2
    over_right = over_width - over_left
    eliminate_pic_01 = fn.deal_pixel_01(over_canny)
    shadow_x = fn.picshadow_x(eliminate_pic_01)
    shadow_y = fn.picshadow_y(eliminate_pic_01)
    # cv2.imshow('canny' + str(over_left), over_canny)
    for i in range(over_canny_width):
        if shadow_x[i] > height - 4:
            over_canny[:, i] = 0
    for i in range(height):
        if shadow_y[i] > over_canny_width - 1:
            over_canny[i, :] = 0
    eliminate_pic_01 = fn.deal_pixel_01(over_canny)
    shadow_x = fn.picshadow_x(eliminate_pic_01)      
   
    # print(int(np.sum(shadow_x[: over_width])), int(np.sum(shadow_x[-over_width :])))
    # print((height - 1) * over_width)
    if np.sum(shadow_x) > (height - 1.5) * over_canny_width:  # 去除线段后接近黑图
         return 0
    if int(np.sum(shadow_x[: over_width])) < (height - 1) * over_width and int(np.sum(shadow_x[-over_width :])) > (height - 2) * over_width:  # 右边黑色像素远大出左边
            return 1
    if int(np.sum(shadow_x[-over_width :])) < (height - 1) * over_width and int(np.sum(shadow_x[: over_width])) > (height - 2) * over_width:  # 左边黑色像素远大出右边
            return 2
    if over_canny_width > 1.5 * thre:
        eliminate_pic_01 = fn.deal_pixel_01(over_canny)
        again_list = etp.find_singledigital(shadow_x, over_canny_width)
        return again_list
    else:
        return 3
    # if np.sum(shadow_x) > 19
    # print(shadow_x)
    # if shadow_x[]


nums_list = etp.digital_list
nums_list = merge_nums(nums_list, 0)
print(nums_list)
single_digital_list = []
len(nums_list)
for i in range(1):
    nums = nums_list[i]
    single_digital_list.extend(split_single(nums, i))
   
    pic = num_img[0: height, nums[0]: nums[1]]
    # cv2.imshow('pic' + str(i), pic)
# print(single_digital_list)
# print(single_digital_list)
for i in range(len(single_digital_list)):
    digital = single_digital_list[i]
    digital_pic = num_img[0: height, digital[0]: digital[1]]
    cv2.imshow('digital_pic' + str(i), digital_pic)
# cv2.imshow('close_v', close_v)
cv2.waitKey()    