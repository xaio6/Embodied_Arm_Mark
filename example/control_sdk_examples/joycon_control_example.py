#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Joy-Con 手柄控制完全指南
====================================

本示例合并了三个原始示例的功能:
- sdk_joycon_demo.py (基础连接测试)
- test_joycon_display.py (传感器数据监控)
- test_joycon_arm_control.py (完整机械臂控制)

提供分级学习路径:
📍 Level 1: 连接测试 - 验证手柄连接是否正常
📊 Level 2: 数据监控 - 了解手柄的原始传感器数据  
🤖 Level 3: 机械臂控制 - 使用手柄遥操作机械臂（关节/笛卡尔模式）
🎯 Level 4: 姿态模式 - 使用IMU控制末端姿态（TCP模式/关节模式）
⚙️ Level 5: 参数配置 - 自定义速度、死区、按键映射

核心映射逻辑：
【基础模式 - 左手柄 (L)】- 位移 / 基础关节
  🕹️  摇杆:   XY平面移动 (笛卡尔) / J1-J2 (关节)
  🔼 L/ZL:   Z轴升降 (笛卡尔) / J3 (关节)
  ➖ 减号:   减速

【基础模式 - 右手柄 (R)】- 旋转 / 末端关节 / 夹爪
  🕹️  摇杆:   俯仰/翻滚 (笛卡尔) / J4-J5 (关节)
  🔼 R/ZR:   偏航旋转 (笛卡尔) / J6 (关节)
  🅰️ A:      闭合夹爪
  🅱️ B:      打开夹爪
  ✖️ X:      切换控制模式 (关节 ↔ 笛卡尔)
  🏠 HOME:   紧急停止

【姿态模式 - 两种子模式（右手柄 R）】

【TCP模式（原 Mode1）】
  🧭 IMU:     控制末端姿态 (Yaw/Pitch/Roll)
  🕹️  右摇杆: X/Y 平移（世界坐标系）
  🔼 R/ZR:    Z 轴升降（世界坐标系）
  ✖️ X:       暂停/恢复 IMU（平移仍可用）
  🏠 HOME:    短按=姿态对齐，长按=回安全位+对齐

【关节模式（原 Mode2）】
  🧭 IMU:     轴对轴映射到关节（Yaw→J1，Pitch→J5，Roll→J6）
  🕹️  右摇杆: 第一人称平移（沿末端前向/右向，需 IK）
  🔼 R/ZR:    Z 轴升降（世界坐标系）
  ✖️ X:       暂停/恢复 IMU（平移仍可用）
  🏠 HOME:    短按=姿态对齐，长按=回安全位+对齐

方向说明（可调）：
  - TCP模式左右手柄镜像翻转：`attitude_left_flip_roll/pitch/yaw`
  - 关节模式映射符号：`attitude_mode2_*_sign_right/left`（以及 arm2 的 *_mult）

前置条件：
- Joy-Con (L) 和 (R) 已通过蓝牙连接到电脑
- 已安装 joycon-python 和 hidapi 库
"""

import sys
import os
import time

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Embodied_SDK.joycon import JoyconSDK
from Horizon_Core import gateway as horizon_gateway

def _fmt_num(v) -> str:
    """兼容 int/float 的打印格式（避免 gyro 为 float 时崩溃）。"""
    try:
        if isinstance(v, bool):
            return f"{int(v):6d}"
        if isinstance(v, int):
            return f"{v:6d}"
        fv = float(v)
        return f"{fv:8.2f}"
    except Exception:
        return f"{0:6d}"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("=" * 80)
    print(" 🎮 Joy-Con 手柄控制完全指南")
    print("=" * 80)
    print("本程序提供分级学习路径，帮助您掌握手柄遥操作。")
    print("=" * 80)

class JoyconControlGuide:
    """Joy-Con控制教学工具"""
    
    def __init__(self):
        self.sdk = None
        self.motors = {}
        self.left_connected = False
        self.right_connected = False
    
    def level1_connection_test(self):
        """Level 1: 连接测试"""
        clear_screen()
        print("=" * 80)
        print(" 📍 Level 1: 连接测试")
        print("=" * 80)
        
        print("\n💡 学习目标：")
        print("  - 验证手柄是否正确配对")
        print("  - 了解手柄连接流程")
        print("  - 排查连接问题")
        
        print("\n⚙️ 配对步骤：")
        print("  1. 打开电脑蓝牙设置")
        print("  2. 按住 Joy-Con 侧面的同步按钮（小圆按钮）")
        print("  3. 等待手柄出现在可用设备列表中")
        print("  4. 点击配对")
        print("  5. 配对完成后运行本程序")
        
        input("\n准备好后按 Enter 开始扫描...")
        
        try:
            if not self.sdk:
                self.sdk = JoyconSDK()
            
            print("\n正在扫描 Joy-Con...")
            self.left_connected, self.right_connected = self.sdk.connect_joycon()
            
            print("-" * 50)
            print(f"  左手柄 (Left):  {'✅ 已连接' if self.left_connected else '❌ 未找到'}")
            print(f"  右手柄 (Right): {'✅ 已连接' if self.right_connected else '❌ 未找到'}")
            print("-" * 50)

            if not (self.left_connected or self.right_connected):
                print("\n❌ 未检测到任何手柄。")
                print("\n🔧 故障排除：")
                print("  1. 检查手柄电池是否充足")
                print("  2. 在系统蓝牙设置中删除手柄并重新配对")
                print("  3. 确保没有其他程序占用手柄 (如 Steam, Yuzu)")
                print("  4. 尝试重启电脑蓝牙服务")
                return False
            
            print("\n✅ 连接测试通过！")
            print("可以继续 Level 2 (数据监控) 或 Level 3 (机械臂控制)")
            return True
            
        except Exception as e:
            print(f"\n❌ 连接失败: {e}")
            return False
    
    def level2_data_monitor(self):
        """Level 2: 数据监控"""
        clear_screen()
        print("=" * 80)
        print(" 📊 Level 2: 传感器数据监控")
        print("=" * 80)
        
        print("\n💡 学习目标：")
        print("  - 了解手柄的原始传感器数据")
        print("  - 理解摇杆死区的必要性")
        print("  - 观察IMU数据用于姿态控制")
        
        if not (self.left_connected or self.right_connected):
            print("\n❌ 请先完成 Level 1 连接测试")
            input("\n按 Enter 继续...")
            return
        
        print("\n数据说明：")
        print("  🎮 摇杆 (Analog Stick):")
        print("     - 水平(H): -32768 ~ 32767 (中心约0)")
        print("     - 垂直(V): -32768 ~ 32767 (中心约0)")
        print("     - 死区: ±2000 (消除漂移)")
        print("  ")
        print("  🧭 陀螺仪 (Gyro):")
        print("     - 测量手柄的旋转角速度")
        print("     - X/Y/Z轴，单位：原始ADC值")
        print("  ")
        print("  🔘 按键状态:")
        print("     - 按下时显示按键名称")
        
        input("\n按 Enter 开始监控（Ctrl+C 退出）...")
        
        try:
            frame_count = 0
            while True:
                clear_screen()
                print("=" * 70)
                print(" Joy-Con 传感器深度监控")
                print("=" * 70)
                print(f"Frame: {frame_count}  |  Ctrl+C 退出")
                print()
                
                # 左Joy-Con状态
                if self.left_connected:
                    left_status = self.sdk.get_left_joycon_status()
                    if left_status:
                        print("【左 Joy-Con (L)】")
                        print(f"  🔋 电池: {left_status.get('battery', 'Unknown')}")
                        
                        print("  🎮 摇杆 (Analog):")
                        stick = left_status.get('analog_stick', {})
                        h, v = stick.get('horizontal', 0), stick.get('vertical', 0)
                        print(f"    H: {h:6d} | V: {v:6d}")
                        
                        print("  🧭 陀螺仪 (IMU):")
                        gyro = left_status.get('gyro', {})
                        if gyro:
                            print(f"    X: {_fmt_num(gyro.get('x', 0))}  Y: {_fmt_num(gyro.get('y', 0))}  Z: {_fmt_num(gyro.get('z', 0))}")
                        
                        print("  🔘 按键:")
                        buttons = left_status.get('buttons', {})
                        active_btns = [k for k, v in buttons.items() if v]
                        print(f"    {' '.join(active_btns) if active_btns else '(无)'}")
                
                print("-" * 70)
                
                # 右Joy-Con状态
                if self.right_connected:
                    right_status = self.sdk.get_right_joycon_status()
                    if right_status:
                        print("【右 Joy-Con (R)】")
                        print(f"  🔋 电池: {right_status.get('battery', 'Unknown')}")
                        
                        print("  🎮 摇杆 (Analog):")
                        stick = right_status.get('analog_stick', {})
                        h, v = stick.get('horizontal', 0), stick.get('vertical', 0)
                        print(f"    H: {h:6d} | V: {v:6d}")
                        
                        print("  🧭 陀螺仪 (IMU):")
                        gyro = right_status.get('gyro', {})
                        if gyro:
                            print(f"    X: {_fmt_num(gyro.get('x', 0))}  Y: {_fmt_num(gyro.get('y', 0))}  Z: {_fmt_num(gyro.get('z', 0))}")
                        
                        print("  🔘 按键:")
                        buttons = right_status.get('buttons', {})
                        active_btns = [k for k, v in buttons.items() if v]
                        print(f"    {' '.join(active_btns) if active_btns else '(无)'}")
                
                print("=" * 70)
                
                frame_count += 1
                time.sleep(0.1)  # 10Hz 刷新
                
        except KeyboardInterrupt:
            print("\n\n退出数据监控")
    
    def level3_arm_control(self):
        """Level 3: 机械臂控制"""
        clear_screen()
        print("=" * 80)
        print(" 🤖 Level 3: 机械臂遥操作")
        print("=" * 80)
        
        print("\n💡 学习目标：")
        print("  - 使用手柄控制机械臂运动")
        print("  - 理解关节空间和笛卡尔空间的区别")
        print("  - 掌握速度倍率和模式切换")
        
        if not (self.left_connected or self.right_connected):
            print("\n❌ 请先完成 Level 1 连接测试")
            input("\n按 Enter 继续...")
            return
        
        print("\n🎮 控制映射：")
        print("  【左手柄】 - 位移控制")
        print("    🕹️  摇杆:   XY平面移动 / J1-J2转动")
        print("    🔼 L/ZL:   Z轴升降 / J3转动")
        print("    ➖ 减号:   降低速度")
        print("  ")
        print("  【右手柄】 - 姿态控制")
        print("    🕹️  摇杆:   俯仰/翻滚 / J4-J5转动")
        print("    🔼 R/ZR:   偏航 / J6转动")
        print("    🅰️ A:      闭合夹爪")
        print("    🅱️ B:      打开夹爪")
        print("    ✖️ X:      切换模式 (关节 ↔ 笛卡尔)")
        print("    ➕ 加号:   提高速度")
        print("    🏠 HOME:   紧急停止")
        
        print("\n⚠️  安全警告：")
        print("  1. 机械臂将跟随手柄动作运动")
        print("  2. 请确保周围无人员和障碍物")
        print("  3. 请时刻准备按下急停 (Home键 或 Ctrl+C)")
        
        # 连接电机
        choice = input("\n是否连接机械臂? (y/N): ").strip().lower()
        if choice != 'y':
            print("已取消")
            return
        
        port = input("请输入串口号 (默认 COM14): ").strip() or "COM14"
        motor_ids = [1, 2, 3, 4, 5, 6]
        
        print(f"\n正在连接电机...")
        self.motors = {}
        for mid in motor_ids:
            try:
                print(f"  连接电机 {mid}...", end='', flush=True)
                m = horizon_gateway.create_motor_controller(motor_id=mid, port=port, baudrate=115200)
                m.connect()
                self.motors[mid] = m
                print(" ✅")
            except Exception as e:
                print(f" ❌ ({e})")
        
        if not self.motors:
            print("❌ 未连接任何电机")
            return
        
        # 绑定电机到SDK
        self.sdk.bind_arm(self.motors)
        print(f"✅ 已连接 {len(self.motors)} 个电机")
        
        input("\n按 Enter 开始控制循环...")
        
        # 启动控制
        self.sdk.start_control()
        
        try:
            while True:
                # 显示状态
                clear_screen()
                print("=" * 80)
                print(" 🤖 机械臂遥操作控制中...")
                print("=" * 80)
                
                status = self.sdk.get_status()
                print(f"\n系统状态: {'🟢 运行中' if status.get('running', False) else '🔴 已停止'}")
                print(f"控制模式: {status.get('control_mode', 'Unknown')}")
                print(f"速度倍率: {status.get('speed_multiplier', 1.0):.1f}x")
                
                # 显示当前位置
                pos = status.get('current_position', [0,0,0])
                print(f"\n末端位置: X={pos[0]:6.1f}  Y={pos[1]:6.1f}  Z={pos[2]:6.1f}")
                
                joints = status.get('current_joints', [0]*6)
                if len(joints) >= 6:
                    print(f"关节角度: J1={joints[0]:5.1f}  J2={joints[1]:5.1f}  J3={joints[2]:5.1f}")
                    print(f"          J4={joints[3]:5.1f}  J5={joints[4]:5.1f}  J6={joints[5]:5.1f}")
                
                print("\n按 Ctrl+C 退出控制")
                print("=" * 80)
                
                time.sleep(0.2)
                
        except KeyboardInterrupt:
            print("\n\n检测到 Ctrl+C，正在停止...")
        finally:
            self.sdk.stop_control()
            print("✅ 已停止控制")
    
    def level4_attitude_mode(self):
        """Level 4: 姿态模式"""
        clear_screen()
        print("=" * 80)
        print(" 🎯 Level 4: 姿态模式 (ATTITUDE Mode)")
        print("=" * 80)
        
        print("\n💡 学习目标：")
        print("  - 使用右手柄IMU控制末端姿态")
        print("  - 理解姿态模式与笛卡尔模式的区别")
        print("  - 掌握姿态对齐和暂停功能")
        
        if not (self.left_connected or self.right_connected):
            print("\n❌ 请先完成 Level 1 连接测试")
            input("\n按 Enter 继续...")
            return
        
        if not self.right_connected:
            print("\n⚠️  姿态模式需要右手柄（用于IMU控制）")
            input("\n按 Enter 继续...")
            return
        
        print("\n🎯 姿态模式说明：")
        print("  姿态模式是一种特殊的控制模式，使用右手柄的IMU（陀螺仪）")
        print("  来控制机械臂末端的姿态，实现更直观的操作。")
        print("  ")
        print("  【TCP模式（原 Mode1）】")
        print("    - IMU: 控制末端姿态（Yaw/Pitch/Roll）")
        print("    - 右摇杆: X/Y平移（世界坐标系）")
        print("    - R/ZR: Z轴升降（世界坐标系）")
        print("  ")
        print("  【关节模式（原 Mode2，默认/主推）】")
        print("    - IMU: 轴对轴映射到关节（Yaw→J1，Pitch→J5，Roll→J6）")
        print("    - 右摇杆: 第一人称平移（沿末端前向/右向）")
        print("    - R/ZR: Z轴升降（世界坐标系）")
        
        print("\n🎮 按键映射：")
        print("  【右手柄】")
        print("    🧭 IMU:     控制末端姿态（摇晃手柄）")
        print("    🕹️  摇杆:   控制X/Y平移")
        print("    🔼 R/ZR:   控制Z轴升降")
        print("    ✖️ X:      暂停/恢复IMU（摇杆平移仍可用）")
        print("    🏠 HOME:   短按=姿态对齐，长按=回安全位+对齐")
        print("    🅰️ A:      闭合夹爪")
        print("    🅱️ B:      打开夹爪")
        
        print("\n⚠️  安全警告：")
        print("  1. 姿态模式会实时响应手柄的旋转动作")
        print("  2. 首次使用建议先进行姿态对齐（按HOME键）")
        print("  3. 请确保周围无人员和障碍物")
        print("  4. 可以随时按X键暂停IMU控制")
        
        # 检查是否已连接机械臂
        if not self.motors:
            choice = input("\n是否连接机械臂? (y/N): ").strip().lower()
            if choice != 'y':
                print("已取消")
                return
            
            port = input("请输入串口号 (默认 COM14): ").strip() or "COM14"
            motor_ids = [1, 2, 3, 4, 5, 6]
            
            print(f"\n正在连接电机...")
            self.motors = {}
            for mid in motor_ids:
                try:
                    print(f"  连接电机 {mid}...", end='', flush=True)
                    m = horizon_gateway.create_motor_controller(motor_id=mid, port=port, baudrate=115200)
                    m.connect()
                    self.motors[mid] = m
                    print(" ✅")
                except Exception as e:
                    print(f" ❌ ({e})")
            
            if not self.motors:
                print("❌ 未连接任何电机")
                return
            
            # 绑定电机到SDK
            self.sdk.bind_arm(self.motors)
            print(f"✅ 已连接 {len(self.motors)} 个电机")
        
        # 选择子模式
        print("\n请选择姿态模式子模式：")
        print("  2. 关节模式（默认/主推）")
        print("  1. TCP模式（兼容）")
        mode_choice = input("请选择 (1/2，默认2): ").strip() or "2"

        # 统一走上层SDK接口（新版本）；旧版本自动回退
        if mode_choice == "1":
            if hasattr(self.sdk, "set_attitude_mode"):
                self.sdk.set_attitude_mode("tcp")
            elif hasattr(self.sdk, "set_attitude_mode2_enabled"):
                self.sdk.set_attitude_mode2_enabled(False)
            print("✅ 使用 TCP模式")
        else:
            if hasattr(self.sdk, "set_attitude_mode"):
                self.sdk.set_attitude_mode("joint")
            elif hasattr(self.sdk, "set_attitude_mode2_enabled"):
                self.sdk.set_attitude_mode2_enabled(True)
            print("✅ 已启用 关节模式")
        
        input("\n按 Enter 启动控制循环...")
        
        # 启动控制
        if not self.sdk.running:
            self.sdk.start_control()
        
        # 启用姿态模式
        print("\n正在启用姿态模式...")
        if hasattr(self.sdk, "enable_attitude"):
            # 若上面选了 tcp/joint，这里不再强制覆盖选择
            success = self.sdk.enable_attitude(mode=("tcp" if mode_choice == "1" else "joint"))
        elif hasattr(self.sdk, "enable_attitude_mode"):
            success = self.sdk.enable_attitude_mode()
            if success:
                print("✅ 姿态模式已启用")
                print("💡 提示：按HOME键进行姿态对齐")
            else:
                print("⚠️  姿态模式启用失败，请检查机械臂状态")
                input("\n按 Enter 继续...")
                return
        else:
            print("⚠️  SDK版本不支持姿态模式")
            input("\n按 Enter 继续...")
            return
        
        try:
            while True:
                # 显示状态
                clear_screen()
                print("=" * 80)
                print(" 🎯 姿态模式控制中...")
                print("=" * 80)
                
                status = self.sdk.get_status()
                print(f"\n系统状态: {'🟢 运行中' if status.get('running', False) else '🔴 已停止'}")
                print(f"控制模式: {status.get('control_mode', 'Unknown')}")
                
                # 显示当前位置和姿态
                pos = status.get('current_position', [0,0,0])
                print(f"\n末端位置: X={pos[0]:6.1f}  Y={pos[1]:6.1f}  Z={pos[2]:6.1f}")
                
                orientation = status.get('current_orientation', [0,0,0])
                if len(orientation) >= 3:
                    print(f"末端姿态: Roll={orientation[2]:5.1f}°  Pitch={orientation[1]:5.1f}°  Yaw={orientation[0]:5.1f}°")
                
                joints = status.get('current_joints', [0]*6)
                if len(joints) >= 6:
                    print(f"关节角度: J1={joints[0]:5.1f}  J2={joints[1]:5.1f}  J3={joints[2]:5.1f}")
                    print(f"          J4={joints[3]:5.1f}  J5={joints[4]:5.1f}  J6={joints[5]:5.1f}")
                
                # 显示输入状态
                input_status = self.sdk.get_input_status() if hasattr(self.sdk, "get_input_status") else {}
                right_input = input_status.get("right", {})
                if right_input:
                    imu_status = "🟢 活跃" if right_input.get("has_imu_input", False) else "⚪ 静止"
                    print(f"\nIMU状态: {imu_status}")
                
                print("\n操作提示：")
                print("  - 摇晃右手柄控制末端姿态")
                print("  - 使用右摇杆控制X/Y平移")
                print("  - 按X键暂停/恢复IMU")
                print("  - 按HOME键进行姿态对齐")
                print("  - 按 Ctrl+C 退出")
                print("=" * 80)
                
                time.sleep(0.2)
                
        except KeyboardInterrupt:
            print("\n\n检测到 Ctrl+C，正在停止...")
        finally:
            if hasattr(self.sdk, "disable_attitude_mode"):
                self.sdk.disable_attitude_mode()
            if self.sdk.running:
                self.sdk.stop_control()
            print("✅ 已停止控制")
    
    def level5_config(self):
        """Level 5: 参数配置"""
        clear_screen()
        print("=" * 80)
        print(" ⚙️  Level 5: 参数配置")
        print("=" * 80)
        
        print("\n💡 可配置参数：")
        print("  1. 速度倍率 (0.1x ~ 2.0x)")
        print("  2. 摇杆死区 (消除漂移)")
        print("  3. 按键映射 (自定义功能)")
        print("  4. 控制灵敏度")
        print("  5. 姿态模式参数（旋转增益、死区等）")
        
        print("\n⚠️  注意：")
        print("  参数配置需要修改SDK内部设置")
        print("  建议先熟悉默认配置再进行调整")
        
        print("\n当前配置（默认值）：")
        print("  速度倍率: 1.0x")
        print("  摇杆死区: ±700")
        print("  灵敏度: 中")
        print("  姿态旋转增益: 0.5")
        
        input("\n按 Enter 继续...")
    
    def show_menu(self):
        """显示主菜单"""
        clear_screen()
        print_banner()
        
        status = ""
        if self.left_connected:
            status += "✅ 左手柄  "
        if self.right_connected:
            status += "✅ 右手柄"
        if status:
            print(f"\n当前连接: {status}")
        else:
            print(f"\n当前连接: ❌ 未连接")
        
        print("\n📚 分级学习菜单：")
        print("  1. Level 1: 连接测试 (必须)")
        print("  2. Level 2: 数据监控 (可选)")
        print("  3. Level 3: 机械臂控制 (核心)")
        print("  4. Level 4: 姿态模式 (新功能)")
        print("  5. Level 5: 参数配置 (进阶)")
        print("  ")
        print("  0. 退出")
        print("=" * 80)
    
    def run(self):
        """主循环"""
        while True:
            self.show_menu()
            choice = input("\n请选择 (0-5): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.level1_connection_test()
                input("\n按 Enter 继续...")
            elif choice == '2':
                self.level2_data_monitor()
            elif choice == '3':
                self.level3_arm_control()
                input("\n按 Enter 继续...")
            elif choice == '4':
                self.level4_attitude_mode()
                input("\n按 Enter 继续...")
            elif choice == '5':
                self.level5_config()
            else:
                print("❌ 无效选择")
                input("\n按 Enter 继续...")
        
        # 清理
        if self.sdk:
            try:
                self.sdk.stop_control()
                self.sdk.disconnect_joycon()
            except:
                pass
        
        if self.motors:
            for m in self.motors.values():
                try:
                    m.disconnect()
                except:
                    pass
        
        print("\n👋 感谢使用！")

if __name__ == "__main__":
    try:
        guide = JoyconControlGuide()
        guide.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  程序被中断")

