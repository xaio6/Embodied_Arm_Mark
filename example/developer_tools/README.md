# 开发者工具 (Developer Tools)

本目录包含用于调试和开发的专业工具，不作为示例教程使用。

## 工具列表

### 1. joycon_sensor_display.py (移动自test_joycon_display.py)
Joy-Con传感器深度监控工具，用于：
- 查看原始IMU数据
- 校准摇杆死区
- 调试按键映射

### 2. mujoco_slider_viewer.py
MuJoCo 滑块调试工具，用于：
- 无硬件查看模型姿态
- 手动调整关节角度
- 辅助检查仿真模型和运动范围

## 使用说明

这些工具是为有SDK开发经验的工程师准备的，普通开发者请使用 `control_sdk_examples/` 下的示例。

## 与示例的区别

| 类型 | 目的 | 受众 |
|------|------|------|
| **示例 (examples/)** | 教学、学习、快速上手 | 所有开发者 |
| **工具 (developer_tools/)** | 调试、诊断、协议验证 | 高级开发者/集成商 |

