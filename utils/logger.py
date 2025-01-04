# -*- coding: utf-8 -*-
'''
Author: Wh_Xcjm
Date: 2025-01-04 15:15:57
LastEditor: Wh_Xcjm
LastEditTime: 2025-01-04 15:19:43
FilePath: \\大作业\\utils\\logger.py
Description: 

Copyright (c) 2025 by WhXcjm, All Rights Reserved. 
Github: https://github.com/WhXcjm
'''
import logging
import sys

def setup_logger(name="MiniRayRender", log_file="minirayrender.log", level=logging.INFO):
    """
    设置日志工具
    :param name: 日志记录器名称
    :param log_file: 日志文件路径
    :param level: 日志级别
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 格式化器：控制日志输出的格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 文件日志处理器
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # 控制台日志处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# 全局日志实例
logger = setup_logger()
