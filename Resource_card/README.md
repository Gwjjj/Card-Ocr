**# bankCard-identification**

**==============================================**

***\*一、银行卡号识别系统： \****

**----------------------------------**



功能介绍

•     采用文字识别（OCR）技术，自动识别银行卡卡号



系统功能

•     对原图像进行倾斜矫正、抠图银行卡区域。

•     通过形态学和目前检测思路。对字符进行区域定位和单个字符分割。

•     对单个字符进行识别



***\*二、Bank Card Rec 主要功能说明：\****

**---------------------------------------------**

**基于LSD找到银行卡位置**

/* 在图片边缘挑选线段*/

selected_lines(line_length, points, per_lines)

/* 线段合并并找出4个方向最长线段*/

merge_line()

/* 围绕点旋转后的坐标*/

getRotatePoint(angle, valuex, valuey, pointx, pointy)

**基于YUV消除背景花纹并进行粗分割**

/* 消除花纹*/

eliminate_pattern(num_ther_img, pattern_img)

/* 去除小的线段*/

drop_little(eliminate_pic)

/* 粗分割*/

find_singledigital(shadow_pic)

**对粗分割中不合理的分割进行改进**

/* 对长度连续的长度不符合要求的进行合并*/

merge_iter(single_i, numslist)

/* 分成多种类别进行细分割*/

split_single(nums_img, i)

​	