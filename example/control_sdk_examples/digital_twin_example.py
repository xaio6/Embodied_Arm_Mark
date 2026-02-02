#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DigitalTwinSDK（MuJoCo 仿真）- 教学版最短示例
============================================

定位：
- 本脚本属于 `control_sdk_examples/`：建议“快速跑通核心 API”，不做复杂交互；
- 更完整的交互式演示（菜单/波形/随机姿态/预设动作）见：`example/mujoco_control.py`

前置条件：
- 可选依赖：`pip install mujoco`
"""

from __future__ import annotations

import os
import sys
import time

# 添加项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Embodied_SDK.digital_twin import DigitalTwinSDK


def main() -> None:
    print("🦾 [DigitalTwinSDK] 教学版示例启动")
    print("说明：会弹出 MuJoCo Viewer 窗口（若未安装 mujoco，会提示并退出）。")

    dt = DigitalTwinSDK()
    if not dt.start_simulation():
        print("❌ 启动仿真失败：请确认已安装 `mujoco` 且模型文件存在。")
        return

    print("✅ 仿真已启动，准备执行 3 段演示动作")
    dt.set_motion_params(max_speed=200, acceleration=100, deceleration=100)

    # 1) 关节空间运动
    print("\n[1/3] 关节空间：move_joints")
    dt.move_joints([0, 30, -45, 0, 15, 0], duration=2.0)
    time.sleep(2.2)

    # 2) 笛卡尔运动（内部 IK）
    print("\n[2/3] 笛卡尔空间：move_cartesian")
    dt.move_cartesian([300, 0, 200], orientation=[0, 0, 180], duration=2.0)
    time.sleep(2.2)

    # 3) 预设动作（名称取决于 preset_actions.json；这里做兼容尝试）
    print("\n[3/3] 预设动作：execute_preset_action")
    for name in ("初始位置", "home_position", "home"):
        ok = dt.execute_preset_action(name)
        if ok:
            print(f"✅ 执行成功：{name}")
            break
    else:
        print("⚠️ 未能执行预设动作：请检查 `config/embodied_config/preset_actions.json` 的动作名。")
    time.sleep(2.0)

    dt.stop_simulation()
    print("\n✅ 仿真已停止，示例结束。")


if __name__ == "__main__":
    main()

