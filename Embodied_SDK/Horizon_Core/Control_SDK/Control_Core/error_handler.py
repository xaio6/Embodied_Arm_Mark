# -*- coding: utf-8 -*-
"""
电机控制错误处理和日志规范化模块

提供统一的错误处理、日志记录和用户提示功能
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime


class MotorError:
    """电机错误定义"""
    
    # UCP状态码错误
    UCP_STATUS_ERRORS = {
        0: "成功",
        1: "未知错误",
        2: "超时",
        3: "CAN超时",
        4: "CAN错误",
        5: "参数错误",
        6: "不支持的操作",
        7: "设备忙",
        8: "设备未就绪",
    }
    
    # 连接错误类型
    CONNECTION_ERRORS = {
        "port_not_found": {
            "user_msg": "串口未找到",
            "detail": "指定的串口设备不存在或无法访问",
            "solutions": [
                "检查串口号是否正确（如COM31）",
                "检查USB设备是否已连接",
                "检查设备驱动是否已安装",
                "尝试拔插USB设备后重试"
            ]
        },
        "port_in_use": {
            "user_msg": "串口被占用",
            "detail": "串口已被其他程序占用",
            "solutions": [
                "关闭其他可能使用该串口的程序",
                "检查是否有多个上位机实例运行",
                "重启电脑后重试"
            ]
        },
        "permission_denied": {
            "user_msg": "串口权限不足",
            "detail": "没有访问串口的权限",
            "solutions": [
                "以管理员身份运行程序",
                "检查串口设备的访问权限"
            ]
        },
        "communication_timeout": {
            "user_msg": "通信超时",
            "detail": "ESP32硬件板未响应",
            "solutions": [
                "检查ESP32硬件板电源是否正常",
                "检查USB连接是否稳定",
                "尝试更换USB线缆",
                "检查波特率是否匹配（推荐115200）"
            ]
        },
        "motor_not_found": {
            "user_msg": "电机未找到",
            "detail": "CAN总线上找不到指定ID的电机",
            "solutions": [
                "检查电机电源是否开启",
                "检查电机ID配置（DIP开关或软件设置）",
                "检查CAN总线连接是否正常",
                "尝试使用探测功能扫描可用电机ID"
            ]
        },
        "can_communication_error": {
            "user_msg": "CAN通信失败",
            "detail": "ESP32与电机之间的CAN通信失败",
            "solutions": [
                "检查CAN_H和CAN_L线连接",
                "检查CAN总线终端电阻（120Ω）",
                "检查电机驱动板是否正常",
                "确认电机固件版本兼容"
            ]
        },
        "firmware_version_mismatch": {
            "user_msg": "固件版本不匹配",
            "detail": "ESP32固件版本与SDK不兼容",
            "solutions": [
                "更新ESP32固件到最新版本",
                "更新上位机SDK到最新版本",
                "联系技术支持获取兼容固件"
            ]
        }
    }
    
    @classmethod
    def parse_ucp_status(cls, status_code: int, err_code: int = 0) -> Dict[str, Any]:
        """
        解析UCP状态码
        
        Args:
            status_code: UCP状态码
            err_code: 扩展错误码
            
        Returns:
            包含错误信息的字典
        """
        status_name = cls.UCP_STATUS_ERRORS.get(status_code, f"未知状态码({status_code})")
        
        error_info = {
            "status_code": status_code,
            "err_code": err_code,
            "status_name": status_name,
            "is_error": status_code != 0
        }
        
        # 根据状态码提供详细信息
        if status_code == 4:  # CAN错误
            error_info.update({
                "user_msg": "CAN通信失败",
                "detail": "ESP32无法与电机进行CAN通信",
                "possible_causes": [
                    "电机未上电或电源故障",
                    "电机ID配置错误",
                    "CAN总线连接问题（H/L线）",
                    "CAN总线终端电阻缺失或错误",
                    "电机驱动板故障"
                ],
                "error_type": "can_communication_error"
            })
        elif status_code == 2 or status_code == 3:  # 超时
            error_info.update({
                "user_msg": "通信超时",
                "detail": "设备未在规定时间内响应",
                "possible_causes": [
                    "设备处理速度慢",
                    "设备繁忙",
                    "通信干扰"
                ],
                "error_type": "communication_timeout"
            })
        elif status_code == 5:  # 参数错误
            error_info.update({
                "user_msg": "参数错误",
                "detail": f"命令参数不正确 (err_code=0x{err_code:04X})",
                "possible_causes": [
                    "参数超出范围",
                    "参数类型不匹配",
                    "缺少必需参数"
                ]
            })
        
        return error_info
    
    @classmethod
    def format_connection_error(cls, error_type: str, exception: Exception = None) -> Dict[str, Any]:
        """
        格式化连接错误信息
        
        Args:
            error_type: 错误类型键
            exception: 原始异常对象
            
        Returns:
            格式化的错误信息字典
        """
        error_info = cls.CONNECTION_ERRORS.get(error_type, {
            "user_msg": "连接失败",
            "detail": "未知错误",
            "solutions": ["请联系技术支持"]
        })
        
        result = {
            "error_type": error_type,
            "user_msg": error_info["user_msg"],
            "detail": error_info["detail"],
            "solutions": error_info["solutions"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if exception:
            result["exception_type"] = type(exception).__name__
            result["exception_msg"] = str(exception)
        
        return result


class MotorLogger:
    """电机控制日志记录器"""
    
    def __init__(self, name: str = "MotorControl"):
        self.logger = logging.getLogger(name)
        
    def log_connection_attempt(self, port: str, motor_id: int, baudrate: int):
        """记录连接尝试"""
        # 连接细节默认不刷屏；需要排查连接问题时再开 DEBUG。
        self.logger.debug(f"🔌 尝试连接电机{motor_id} [{port}@{baudrate}]")
    
    def log_connection_success(self, motor_id: int, version: str = None):
        """记录连接成功"""
        if version:
            # 如果version是字典，提取firmware版本
            if isinstance(version, dict):
                fw = version.get('firmware', version)
                self.logger.info(f"✅ 电机{motor_id}连接成功 [版本:{fw}]")
            else:
                self.logger.info(f"✅ 电机{motor_id}连接成功 [版本:{version}]")
        else:
            self.logger.info(f"✅ 电机{motor_id}连接成功")
    
    def log_connection_failure(self, motor_id: int, error_info: Dict[str, Any]):
        """记录连接失败（简洁格式）"""
        # 提取关键信息
        error_type = error_info.get('error_type', 'unknown')
        user_msg = error_info.get('user_msg', '未知错误')
        
        # 构建简洁的错误消息
        error_msg = f"❌ 电机{motor_id}连接失败: {user_msg}"
        
        # 添加关键详情
        if "status_code" in error_info:
            status = error_info['status_code']
            status_name = error_info.get('status_name', '未知')
            error_msg += f" [UCP status={status}:{status_name}]"
        
        if "exception_msg" in error_info:
            # 简化异常信息（只显示关键部分）
            exc_msg = str(error_info['exception_msg'])
            if "PermissionError" in exc_msg:
                error_msg += " [串口被占用]"
            elif "FileNotFoundError" in exc_msg:
                error_msg += " [串口不存在]"
            elif "timeout" in exc_msg.lower():
                error_msg += " [通信超时]"
        
        # 添加第一条解决方案
        solutions = error_info.get('solutions', [])
        if solutions:
            error_msg += f" → {solutions[0]}"
        
        self.logger.error(error_msg)
    
    def log_ucp_error(self, motor_id: int, operation: str, status: int, err_code: int = 0):
        """记录UCP协议错误（简洁格式）"""
        error_info = MotorError.parse_ucp_status(status, err_code)
        status_name = error_info.get('status_name', '未知')
        
        # 简洁的单行错误
        msg = f"❌ 电机{motor_id} {operation}失败: status={status}({status_name})"
        if err_code:
            msg += f" err=0x{err_code:04X}"
        
        # 添加第一个可能原因
        if "possible_causes" in error_info and error_info["possible_causes"]:
            msg += f" → {error_info['possible_causes'][0]}"
        
        self.logger.error(msg)


def analyze_serial_exception(exception: Exception) -> str:
    """
    分析串口异常并返回错误类型
    
    Args:
        exception: 原始异常对象
        
    Returns:
        错误类型键
    """
    error_msg = str(exception).lower()
    
    if "filenotfounderror" in str(type(exception)).lower() or "could not open port" in error_msg:
        if "系统找不到指定的文件" in str(exception) or "no such file" in error_msg:
            return "port_not_found"
    
    if "permissionerror" in str(type(exception)).lower() or "access is denied" in error_msg:
        return "permission_denied"
    
    if "could not open port" in error_msg and "in use" in error_msg:
        return "port_in_use"
    
    if "timeout" in error_msg or "timed out" in error_msg:
        return "communication_timeout"
    
    return "unknown"


def format_error_for_ui(error_info: Dict[str, Any]) -> str:
    """
    格式化错误信息用于UI显示（简洁版）
    
    Args:
        error_info: 错误信息字典
        
    Returns:
        格式化的用户友好错误信息
    """
    msg = f"{error_info.get('user_msg', '未知错误')}\n\n"
    
    if "detail" in error_info:
        msg += f"详细: {error_info['detail']}\n\n"
    
    solutions = error_info.get('solutions', [])
    if solutions:
        msg += "解决方案:\n"
        for i, solution in enumerate(solutions[:3], 1):  # 最多显示3条
            msg += f"{i}. {solution}\n"
    
    return msg.strip()

