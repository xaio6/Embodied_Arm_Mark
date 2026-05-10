#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Embodied_SDK
============

面向网页 / ROS2 / 脚本调用的高层具身智能机械臂 SDK。

设计目标：
- **统一入口**：将项目中已有的视觉抓取、具身智能决策、IO 作业等高级能力，以纯 Python 接口方式暴露出来；
- **与 GUI 解耦**：SDK 不依赖 PyQt5 界面，可在 Ubuntu + ROS2、后端 Web 服务等环境中直接调用；
- **可渐进扩展**：当前优先封装视觉抓取相关能力，后续可以逐步把示教器、数字孪生、IO 作业等模块迁移进来。

当前已提供的模块：
- `visual_grasp.VisualGraspSDK`：基于现有标定 / 像素坐标转换的基础视觉抓取（点/框中心）高层封装；
- `visual_grasp.FollowGraspSDK`：基于 YOLOv8 + CSRT/跟踪器的连续视觉伺服/跟随抓取高层封装；
- `motion.MotionSDK`：基于 `c_a_j` / `e_p_a` / IK选解等的机械臂基础运动控制封装；
- `embodied.EmbodiedSDK`：基于 `HierarchicalDecisionSystem` 的具身智能高层封装（自然语言任务 -> 动作序列）；
- `joycon.JoyconSDK`：基于 `JoyConArmController` 的手柄控制封装；
- `io.IOSDK`：基于 `ESP32IOController` 的 IO / 外设控制封装；
- `digital_twin.DigitalTwinSDK`：基于 MuJoCo 的数字孪生运动控制封装（仿真端）；
- `horizon_sdk.HorizonArmSDK`：顶层聚合 SDK，一次性绑定电机/相机，对外统一暴露各类功能入口（vision/follow/motion/embodied/joycon/io/digital_twin/...）。
- `Embodied_SDK.Horizon_Core.core.arm_core.kinematics_factory.create_configured_kinematics`：统一运动学创建入口，默认按 `config/dh_parameters_config.json` 创建 FK/IK 模型。

运动学口径说明：
- `MotionSDK.move_cartesian`
- `VisualGraspSDK` 的位姿 IK
- `JoyconSDK` 默认绑定运动学
- `HorizonArmSDK` 聚合后的默认运动学

以上默认都统一走 `config/dh_parameters_config.json`。
如需在外部脚本中手动复用同一套 FK/IK，请直接使用：
- `create_configured_kinematics()`
- `load_kinematics_config()`

后续规划（示例）：
- `motion`：关节/末端运动基础封装
- `tasks`：具身智能任务规划封装
- `io`：IO 作业与外部设备交互封装
"""

_EXPORTS = {
    "VisualGraspSDK": (".visual_grasp", "VisualGraspSDK"),
    "FollowGraspSDK": (".visual_grasp", "FollowGraspSDK"),
    "MotionSDK": (".motion", "MotionSDK"),
    "EmbodiedSDK": (".embodied", "EmbodiedSDK"),
    "JoyconSDK": (".joycon", "JoyconSDK"),
    "IOSDK": (".io", "IOSDK"),
    "DigitalTwinSDK": (".digital_twin", "DigitalTwinSDK"),
    "HorizonArmSDK": (".horizon_sdk", "HorizonArmSDK"),
    "AISDK": (".ai", "AISDK"),
    "DepthEstimationSDK": (".ai", "DepthEstimationSDK"),
    "ZDTGripperSDK": (".gripper_sdk", "ZDTGripperSDK"),
    "create_motor_controller": (".motion", "create_motor_controller"),
    "setup_logging": (".motion", "setup_logging"),
    "close_all_shared_interfaces": (".motion", "close_all_shared_interfaces"),
    "get_shared_interface_info": (".motion", "get_shared_interface_info"),
    "get_function_codes": (".motion", "get_function_codes"),
    "create_configured_kinematics": ("Embodied_SDK.Horizon_Core.core.arm_core.kinematics_factory", "create_configured_kinematics"),
    "load_kinematics_config": ("Embodied_SDK.Horizon_Core.core.arm_core.kinematics_factory", "load_kinematics_config"),
}


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    module_name, attr_name = _EXPORTS[name]
    if module_name.startswith("."):
        module = importlib.import_module(module_name, __name__)
    else:
        module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value

__all__ = [
    "VisualGraspSDK",
    "FollowGraspSDK",
    "MotionSDK",
    "EmbodiedSDK",
    "JoyconSDK",
    "IOSDK",
    "DigitalTwinSDK",
    "HorizonArmSDK",
    "AISDK",
    "DepthEstimationSDK",
    "ZDTGripperSDK",
    "create_motor_controller",
    "setup_logging",
    "close_all_shared_interfaces",
    "get_shared_interface_info",
    "get_function_codes",
    "create_configured_kinematics",
    "load_kinematics_config",
]
