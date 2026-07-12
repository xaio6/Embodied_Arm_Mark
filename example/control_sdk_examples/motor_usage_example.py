#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单电机控制完全指南
==========================================

本示例是 test_interactive.py 的**教学优化版**，专注于帮助开发者理解和学习。
相比原版，本版本增强了：
✨ 每个功能都有详细的原理说明
✨ 参数含义和取值范围的解释
✨ 常见错误和解决方案
✨ 快捷键和默认值提示
✨ 学习建议和代码示例

适合人群：
- 刚接触ZDT电机协议的开发者
- 需要深入了解单电机控制的工程师
- 需要参考代码示例的集成商

完整功能覆盖：
1. 基础控制 (enable/disable/stop)
2. 运动控制 (速度/位置/力矩)
3. 回零功能 (homing)
4. 参数读取 (monitoring)
5. 参数修改 (configuration)

前置学习：
请先完成 `quickstart_guide.py` 了解基础概念。
"""

import os
import sys
import time
import logging
from typing import Optional, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Embodied_SDK import create_motor_controller, setup_logging

class MotorUsageGuide:
    """单电机控制教学工具"""
    
    def __init__(self):
        self.motor: Optional[Any] = None
        self.connected = False
        self.motor_id = None
        self.port = None
        
        # 设置日志（默认INFO级别）
        setup_logging(logging.INFO)
        
        print("=" * 70)
        print(" 🎓 单电机控制完全指南")
        print("=" * 70)
        print("本程序将系统性地介绍ZDT电机的所有控制功能。")
        print("每个功能都配有详细说明和参数解释。\n")
    
    def connect_motor(self) -> bool:
        """连接电机 - 带详细引导"""
        if self.connected:
            print("✅ 电机已连接")
            return True
        
        print("\n" + "=" * 70)
        print(" 📡 连接电机")
        print("=" * 70)
        
        print("\n💡 连接参数说明：")
        print("  串口号: Windows为COMx，Linux为/dev/ttyUSBx")
        print("  波特率: 默认115200（UCP硬件保护模式，OmniCAN串口）")
        print("  电机ID: 1-255，通过电机上的拨码开关或上位机设置")
        
        # 使用默认值简化输入
        use_default = input("\n使用默认配置? (COM14, ID=1) [Y/n]: ").strip().lower()
        
        if use_default in ['', 'y', 'yes']:
            self.port = 'COM14'
            self.motor_id = 1
        else:
            self.port = input("串口号 (例如: COM18): ").strip() or 'COM14'
            self.motor_id = int(input("电机ID (1-255): ").strip() or '1')
        
        try:
            print(f"\n正在连接 ID={self.motor_id} @ {self.port}...")
            
            self.motor = create_motor_controller(
                motor_id=self.motor_id,
                port=self.port,
                baudrate=115200
            )
            
            self.motor.connect()
            self.connected = True
            print(f"✅ 电机连接成功！")
            
            # 读取并显示基本信息
            version = self.motor.read_parameters.get_version()
            print(f"\n📋 电机信息:")
            print(f"  固件版本: {version['firmware']}")
            print(f"  硬件版本: {version['hardware']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print("\n🔧 故障排除：")
            print("  1. 检查串口号（设备管理器）")
            print("  2. 确认电机ID正确")
            print("  3. 验证电机已上电")
            print("  4. 关闭其他占用串口的程序")
            return False
    
    def disconnect_motor(self):
        """断开电机连接"""
        if self.motor and self.connected:
            try:
                self.motor.disconnect()
                self.connected = False
                print("✅ 电机已断开连接")
            except Exception as e:
                print(f"⚠️  断开连接时出现警告: {e}")
        else:
            print("电机未连接")
    
    def ensure_connected(self) -> bool:
        """确保电机已连接"""
        if not self.connected:
            print("❌ 电机未连接，请先连接电机")
            return False
        return True
    
    # ========== 第1章: 基础控制 ==========
    
    def chapter1_enable(self):
        """1.1 电机使能"""
        if not self.ensure_connected():
            return
        
        print("\n" + "=" * 70)
        print(" ⚡ 1.1 电机使能 (Enable)")
        print("=" * 70)
        
        print("\n📚 功能说明：")
        print("  使能后，电机将：")
        print("  ✓ 能够响应运动指令（位置/速度/力矩）")
        print("  ✓ 产生保持力矩，维持当前位置")
        print("  ✓ 激活位置环、速度环等控制算法")
        
        print("\n⚠️  注意事项：")
        print("  • 使能瞬间可能有轻微抖动（正常现象）")
        print("  • 使能后电机会发热（即使不运动）")
        print("  • 长时间不用建议失能以节能和延长寿命")
        
        input("\n按 Enter 执行使能...")
        
        try:
            self.motor.control_actions.enable()
            time.sleep(0.5)
            
            # 验证状态
            status = self.motor.read_parameters.get_motor_status()
            print(f"\n✅ 使能成功")
            print(f"  状态确认: 使能={status.enabled}, 到位={status.in_position}")
            
            print("\n💡 代码示例：")
            print("```python")
            print("motor.control_actions.enable()")
            print("status = motor.read_parameters.get_motor_status()")
            print("if status.enabled:")
            print("    print('电机已使能')")
            print("```")
            
        except Exception as e:
            print(f"❌ 使能失败: {e}")
    
    def chapter1_disable(self):
        """1.2 电机失能 - 理论介绍（不实际操作）"""
        if not self.ensure_connected():
            return
        
        print("\n" + "=" * 70)
        print(" 💤 1.2 电机失能 (Disable) - 理论介绍")
        print("=" * 70)
        
        print("\n🚨 【危险警告】🚨")
        print("  ⚠️  如果您的机械臂电机没有机械刹车（抱闸）：")
        print("  ⚠️  失能后机械臂会在重力作用下立即掉落！")
        print("  ⚠️  会造成机械臂部件损坏或砸坏桌面！")
        print("  ⚠️  严禁在代码中随意调用 disable() 接口！")
        print("  💡 请先确认您的机械臂是否配备机械刹车功能")
        
        print("\n📚 功能说明（仅供理解，不要实际使用）：")
        print("  失能 (Disable) 会切断电机驱动电流，导致：")
        print("  ✗ 电机失去保持力矩")
        print("  ✗ 机械臂在重力作用下掉落")
        print("  ✗ 可能砸坏机械臂和桌面")
        print("  ✗ 停止响应所有运动指令")
        
        print("\n❌ 错误的使用场景（千万不要做）：")
        print("  ✗ 程序退出时自动失能")
        print("  ✗ 紧急停止时失能")
        print("  ✗ 长时间不用时失能")
        print("  ✗ 任何机械臂悬空状态下失能")
        
        print("\n✅ 正确的做法：")
        print("  1. 紧急停止：使用 stop() 而不是 disable()")
        print("  2. 程序退出：保持使能状态，手动断电")
        print("  3. 长时间不用：使用 stop() 停止运动，保持使能")
        print("  4. 需要调整位置：先运动到安全姿态（趴下），再考虑断电")
        
        print("\n💡 替代方案：")
        print("  • 停止运动：motor.control_actions.stop()")
        print("  • 保持位置：电机保持使能状态")
        print("  • 断电：使用物理电源开关")
        print("  • 急停：使用急停按钮或切断电源")
        
        print("\n" + "="*70)
        print("📖 本示例不提供 disable() 的实际调用示例")
        print("如需了解技术细节，请查阅完整版: test_interactive.py")
        print("但请记住：除非绝对必要，永远不要在代码中调用 disable()")
        print("="*70)
    
    def chapter1_stop(self):
        """1.3 电机停止"""
        if not self.ensure_connected():
            return
        
        print("\n" + "=" * 70)
        print(" 🛑 1.3 电机停止 (Stop)")
        print("=" * 70)
        
        print("\n📚 功能说明：")
        print("  stop() 命令的作用：")
        print("  ✓ 中断当前正在执行的运动指令")
        print("  ✓ 按照预设的减速度进行制动")
        print("  ✓ 停止后保持使能状态和位置")
        
        print("\n🔑 关键区别：")
        print("  stop()    → 停止运动但保持使能")
        print("  disable() → 失能并失去保持力")
        print("  断电      → 完全切断电源")
        
        input("\n按 Enter 执行停止...")
        
        try:
            self.motor.control_actions.stop()
            print("✅ 停止命令已发送")
            
            # 等待并读取速度
            time.sleep(0.5)
            speed = self.motor.read_parameters.get_speed()
            print(f"  当前速度: {speed:.2f} RPM")
            
        except Exception as e:
            print(f"❌ 停止失败: {e}")
    
    # ========== 第2章: 运动控制 ==========
    
    def chapter2_speed_mode(self):
        """2.1 速度模式"""
        if not self.ensure_connected():
            return
        
        print("\n" + "=" * 70)
        print(" 🏃 2.1 速度模式 (Speed Mode)")
        print("=" * 70)
        
        print("\n📚 功能说明：")
        print("  速度模式: 控制电机以恒定速度旋转")
        print("  特点:")
        print("  ✓ 不限制转动圈数")
        print("  ✓ 需要手动发送停止命令")
        print("  ✓ 适合传送带、风扇等持续旋转场景")
        
        print("\n📊 参数说明：")
        print("  speed (RPM)")
        print("    - 范围: -6000 ~ +6000")
        print("    - 正值=正转，负值=反转")
        print("    - 建议测试值: 100-500 RPM")
        print("  ")
        print("  acceleration (RPM/s)")
        print("    - 加速度，影响启动和变速的平滑性")
        print("    - 范围: 100 ~ 5000")
        print("    - 建议值: 1000 (平衡速度和平滑性)")
        
        try:
            speed = float(input("\n目标速度 (RPM, 默认100): ").strip() or "100")
            acceleration = int(input("加速度 (RPM/s, 默认1000): ").strip() or "1000")
            run_time = float(input("运行时间 (秒, 默认3): ").strip() or "3")
            
            print(f"\n🚀 开始运行: {speed}RPM, 加速度{acceleration}RPM/s")
            
            self.motor.control_actions.set_speed(
                speed=speed,
                acceleration=acceleration
            )
            
            print(f"运行 {run_time} 秒后自动停止...")
            for i in range(int(run_time)):
                time.sleep(1)
                try:
                    current_speed = self.motor.read_parameters.get_speed()
                    print(f"  {i+1}s - 当前速度: {current_speed:.1f} RPM")
                except:
                    pass
            
            self.motor.control_actions.stop()
            print("✅ 已停止")
            
            print("\n💡 代码示例：")
            print("```python")
            print(f"motor.control_actions.set_speed(speed={speed}, acceleration={acceleration})")
            print("time.sleep(3)  # 运行3秒")
            print("motor.control_actions.stop()")
            print("```")
            
        except ValueError:
            print("❌ 输入格式错误")
        except Exception as e:
            print(f"❌ 执行失败: {e}")
    
    def chapter2_position_mode(self):
        """2.2 位置模式"""
        if not self.ensure_connected():
            return
        
        print("\n" + "=" * 70)
        print(" 🎯 2.2 位置模式 (Position Mode)")
        print("=" * 70)
        
        print("\n📚 功能说明：")
        print("  位置模式: 控制电机移动到指定角度")
        print("  特点:")
        print("  ✓ 到位后自动停止")
        print("  ✓ 支持绝对/相对定位")
        print("  ✓ 适合精确定位场景")
        
        print("\n📊 参数说明：")
        print("  position (度)")
        print("    - 目标角度")
        print("    - 无限制范围（支持多圈）")
        print("    - 示例: 90, 360, -180")
        print("  ")
        print("  speed (RPM)")
        print("    - 运动速度")
        print("    - 建议: 300-800 RPM")
        print("  ")
        print("  is_absolute (布尔)")
        print("    - True:  移动到绝对角度X")
        print("    - False: 在当前位置基础上移动X度")
        
        print("\n🔑 绝对vs相对示例：")
        print("  假设当前位置=50°")
        print("  绝对模式,目标=90°  → 移动到90°（转动40°）")
        print("  相对模式,目标=90°  → 移动到140°（50+90）")
        
        try:
            current_pos = self.motor.read_parameters.get_position()
            print(f"\n当前位置: {current_pos:.2f}°")
            
            position = float(input("目标位置 (度, 默认90): ").strip() or "90")
            speed = float(input("运动速度 (RPM, 默认500): ").strip() or "500")
            is_absolute = input("绝对位置模式? (Y/n): ").strip().lower() in ['', 'y', 'yes']
            
            print(f"\n🚀 开始运动到 {position}° ({'绝对' if is_absolute else '相对'}模式)")
            
            self.motor.control_actions.move_to_position(
                position=position,
                speed=speed,
                is_absolute=is_absolute
            )
            
            # 等待到位
            print("等待到位...", end='', flush=True)
            if self.motor.control_actions.wait_for_position(timeout=10.0):
                final_pos = self.motor.read_parameters.get_position()
                print(f"\n✅ 已到位: {final_pos:.2f}°")
            else:
                print("\n⚠️  超时")
            
        except ValueError:
            print("❌ 输入格式错误")
        except Exception as e:
            print(f"❌ 执行失败: {e}")
    
    def chapter2_trapezoid_mode(self):
        """2.3 梯形曲线位置模式"""
        if not self.ensure_connected():
            return
        
        print("\n" + "=" * 70)
        print(" 📈 2.3 梯形曲线位置模式 (Trapezoid Position)")
        print("=" * 70)
        
        print("\n📚 功能说明：")
        print("  梯形曲线: 更精细的运动控制")
        print("  运动过程分为三个阶段:")
        print("  ")
        print("     速度")
        print("      ^")
        print("      |     ___________  ← 匀速段")
        print("      |    /           \\")
        print("      |   /             \\")
        print("      |__/_______________\\___ 时间")
        print("        ↑                ↑")
        print("       加速              减速")
        
        print("\n📊 参数说明：")
        print("  max_speed (RPM)      - 匀速段速度")
        print("  acceleration (RPM/s) - 加速度")
        print("  deceleration (RPM/s) - 减速度")
        
        print("\n💡 应用场景：")
        print("  • 需要精确控制加减速过程")
        print("  • 避免冲击和振动")
        print("  • 同步多轴运动时保持速度曲线一致")
        
        try:
            current_pos = self.motor.read_parameters.get_position()
            print(f"\n当前位置: {current_pos:.2f}°")
            
            position = float(input("目标位置 (度, 默认90): ").strip() or "90")
            max_speed = float(input("最大速度 (RPM, 默认500): ").strip() or "500")
            acceleration = int(input("加速度 (RPM/s, 默认1000): ").strip() or "1000")
            deceleration = int(input("减速度 (RPM/s, 默认1000): ").strip() or "1000")
            is_absolute = input("绝对位置? (Y/n): ").strip().lower() in ['', 'y', 'yes']
            
            print(f"\n🚀 开始梯形曲线运动")
            
            self.motor.control_actions.move_to_position_trapezoid(
                position=position,
                max_speed=max_speed,
                acceleration=acceleration,
                deceleration=deceleration,
                is_absolute=is_absolute
            )
            
            # 等待到位
            if self.motor.control_actions.wait_for_position(timeout=15.0):
                print("✅ 运动完成")
            else:
                print("⚠️  超时")
            
        except Exception as e:
            print(f"❌ 执行失败: {e}")
    
    def chapter2_torque_mode(self):
        """2.4 力矩模式"""
        if not self.ensure_connected():
            return
        
        print("\n" + "=" * 70)
        print(" 💪 2.4 力矩模式 (Torque Mode)")
        print("=" * 70)
        
        print("\n📚 功能说明：")
        print("  力矩模式: 通过控制电流来控制输出力矩")
        print("  特点:")
        print("  ✓ 不控制位置和速度")
        print("  ✓ 适合柔顺控制、力控场景")
        print("  ✓ 需要上层算法闭环控制位置")
        
        print("\n📊 参数说明：")
        print("  current (mA)")
        print("    - 电机相电流，正比于输出力矩")
        print("    - 范围: 0-3000 mA（取决于电机额定）")
        print("    - 建议测试: 500 mA（小力矩）")
        print("  ")
        print("  current_slope (mA/s)")
        print("    - 电流变化率，影响力矩变化平滑性")
        print("    - 建议值: 1000")
        
        print("\n⚠️  安全警告：")
        print("  • 力矩模式下电机会持续输出力")
        print("  • 可能导致电机持续转动（如无负载）")
        print("  • 请准备好随时停止")
        
        choice = input("\n是否继续? (y/N): ").strip().lower()
        if choice != 'y':
            print("已取消")
            return
        
        try:
            current = int(input("目标电流 (mA, 默认500): ").strip() or "500")
            current_slope = int(input("电流斜率 (mA/s, 默认1000): ").strip() or "1000")
            run_time = float(input("运行时间 (秒, 默认3): ").strip() or "3")
            
            print(f"\n🚀 设置力矩: {current}mA")
            
            self.motor.control_actions.set_torque(
                current=current,
                current_slope=current_slope
            )
            
            print(f"运行 {run_time} 秒后停止...")
            time.sleep(run_time)
            
            self.motor.control_actions.stop()
            print("✅ 已停止")
            
        except Exception as e:
            print(f"❌ 执行失败: {e}")
    
    # ========== 主菜单 ==========
    
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "=" * 70)
        print(" 📚 单电机控制完全指南 - 主菜单")
        print("=" * 70)
        
        if self.connected:
            print(f"✅ 已连接: ID={self.motor_id} @ {self.port}")
        else:
            print("❌ 未连接")
        
        print("\n【第0章 - 连接管理】")
        print("  0. 连接电机")
        print("  00. 断开电机")
        
        print("\n【第1章 - 基础控制】")
        print("  1. 电机使能 (Enable)")
        print("  2. 电机失能 (Disable)")
        print("  3. 电机停止 (Stop)")
        
        print("\n【第2章 - 运动控制】")
        print("  4. 速度模式 (Speed Mode)")
        print("  5. 位置模式 (Position Mode)")
        print("  6. 梯形曲线位置模式 (Trapezoid)")
        print("  7. 力矩模式 (Torque Mode)")
        
        print("\n【更多功能】")
        print("  💡 完整功能请参考: test_interactive.py")
        print("     (回零、参数读取、参数修改等40+功能)")
        
        print("\n  Q. 退出")
        print("=" * 70)
    
    def run(self):
        """运行主循环"""
        print("\n欢迎使用单电机控制完全指南！")
        print("本程序将引导您学习ZDT电机的核心控制功能。\n")
        
        while True:
            self.show_menu()
            choice = input("\n请选择功能: ").strip().lower()
            
            if choice in ['q', 'quit', 'exit']:
                break
            elif choice == '0':
                self.connect_motor()
            elif choice == '00':
                self.disconnect_motor()
            elif choice == '1':
                self.chapter1_enable()
            elif choice == '2':
                self.chapter1_disable()
            elif choice == '3':
                self.chapter1_stop()
            elif choice == '4':
                self.chapter2_speed_mode()
            elif choice == '5':
                self.chapter2_position_mode()
            elif choice == '6':
                self.chapter2_trapezoid_mode()
            elif choice == '7':
                self.chapter2_torque_mode()
            else:
                print("❌ 无效选择")
            
            input("\n按 Enter 继续...")
        
        # 清理
        self.disconnect_motor()
        print("\n👋 感谢使用！")

if __name__ == "__main__":
    try:
        guide = MotorUsageGuide()
        guide.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  程序被中断")

