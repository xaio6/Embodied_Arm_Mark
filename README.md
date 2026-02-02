# HorizonArm Mark 版本

欢迎使用 **HorizonArm Mark 版本**开发包。本文档是**根目录总入口**：用“学习路线”的方式，带你从 0 到 1 跑通示例，再按你的角色（控制/视觉/AI/仿真/交互）逐步深入，最终把 SDK 稳定集成进你的项目。

> 强烈建议：不要只“看文档”，要**边看边运行示例**。本仓库已经把“可复制、可运行、可扩展”的示例准备好了。

---

## 🎯 学习路线总览（按路线走，不迷路）

```text
第0步：了解项目结构（5分钟）
    ↓
第1步：环境准备与安装依赖（10分钟）
    ↓
第2步：SDK 理论学习（30分钟）
    ↓
第3步：5分钟跑通快速入门（5分钟）
    ↓
第4步：按角色选择深入学习路径（2-8小时）
    ↓
第5步：项目实践与工程化集成（持续迭代）
```

---

## 📂 第0步：了解项目结构（5分钟）

本仓库的“真正入口”在 `example/`：**示例 + 文档 + 学习路径**都在里面。

```text
Horizon_Arm_Mark/
├── example/                              ⭐ 从这里开始（示例与文档总入口）
│   ├── README.md                         - 示例总导航（第一次打开就看它）
│   ├── SDK完全介绍.md                     - SDK 架构与核心概念（强烈建议先看）
│   ├── 示例代码总导航.md                  - 更细粒度的示例索引与学习路径
│   ├── quickstart_guide.py               - 5分钟快速入门（强烈建议先跑）
│   ├── sdk_quickstart.py                 - 交互式完整示例（6轴/预设动作/夹爪等）
│   ├── control_sdk_examples/             - 控制相关教学示例（单电机/多机同步/IO/视觉/仿真/手柄）
│   ├── ai_sdk_examples/                  - AI 相关示例（LLM/ASR/TTS/多模态/智能对话）
│   ├── developer_tools/                  - 开发者工具（传感器监控/仿真滑块等）
│   ├── docs/                             - 文档中心（index.md 是总入口）
│   └── mkdocs.yml                        - 文档站点配置（如需自行构建）
│
├── Embodied_SDK/                          ⭐ 推荐开发入口（Python 源码，可直接读/改/引用）
│   ├── horizon_sdk.py                     - 顶层聚合入口（HorizonArmSDK）
│   ├── motion.py                          - 运动控制（关节/笛卡尔/预设动作/夹爪等）
│   ├── visual_grasp.py                    - 视觉抓取/跟随
│   ├── joycon.py                          - 手柄控制封装（如需）
│   ├── io.py                              - IO 控制
│   ├── digital_twin.py                    - MuJoCo 仿真接口（如需）
│   ├── ai.py                              - AI 封装（如需）
│   └── __init__.py                        - 常用导出（create_motor_controller 等）
│
├── Horizon_Core/                          🔒 核心驱动与算法（部分为二进制封装 .pyd）
│   ├── Control_SDK/                       - 控制核心与协议层
│   ├── AI_SDK/                            - AI 核心（providers/core/utils 等）
│   └── gateway.py                         - 常用网关入口（部分示例会引用）
│
├── config/                                ⚙️ 配置文件（电机/标定/URDF/AI/预设动作等）
│   ├── motor_config.json
│   ├── calibration_parameter.json
│   ├── embodied_config/preset_actions.json
│   ├── aisdk_config.yaml
│   └── urdf/mjmodel.xml                   - 仿真模型（MuJoCo）
│
├── requirements.txt                        📄 依赖清单（已按“默认必装/可选”分组）
└── README.md                               📖 你正在读的文档（Mark 版本总入口）
```

你需要记住的只有两句话：

- **想快速跑起来**：直接看并运行 `example/quickstart_guide.py`
- **想系统学/做项目**：从 `example/README.md` 与 `example/docs/index.md` 开始走路线

---

## 🔧 第1步：环境准备与安装依赖（10分钟）

### 1.1 环境要求

- **Python**：3.12+（本仓库示例与依赖分组以此为准）
- **操作系统**：Windows 10/11（也可 Ubuntu 20.04+ 纯脚本运行）
- **真实硬件（可选）**：OmniCAN（UCP 模式，电脑侧表现为串口）+ 机械臂驱动板/电机

### 1.2 安装依赖（推荐）

在项目根目录执行：

```bash
pip install -r requirements.txt
```

`requirements.txt` 的设计原则：

- **默认必装**：能跑通“控制 + 视觉”核心示例
- **可选依赖**：Joy-Con / AI / 语音 / MuJoCo / GUI / 可视化等，按需启用

> 如果你只想先控制机械臂、跑运动示例：默认安装即可；不要一上来就把所有可选功能都装齐。

### 1.3 Windows 下常见安装问题（可选项）

- **pyaudio（仅语音相关示例需要）**：部分环境需要额外步骤  
  参考 `requirements.txt` 里的说明（例如 `pipwin install pyaudio`）。

---

## 📚 第2步：SDK 理论学习（30分钟）

### 2.1 必读文档（强烈建议）

- **SDK 架构与示例索引**：`example/SDK完全介绍.md`
- **文档中心总入口**：`example/docs/index.md`

阅读目标（30 分钟内达成）：

- 知道推荐入口是 `Embodied_SDK`，顶层入口是 `HorizonArmSDK`
- 理解两套常用坐标/单位：  
  - 关节角：度（deg）  
  - 末端位置：毫米（mm）；末端姿态：度（deg）
- 知道你应该先跑哪些示例、下一步该学哪些模块文档

---

## 🚀 第3步：5分钟跑通快速入门（5分钟）

### 3.1 ⚠️ 安全第一（务必先读）

第一次上电、第一次跑控制脚本前，先看：

- `example/docs/safety.md`

其中最关键的一条（请务必理解）：

- **如果你的电机没有物理抱闸（刹车），严禁随意 `disable()` 失能**  
  正确做法通常是 **stop（停止运动）/disconnect（断开通信）**，而不是让机械臂“瞬间掉落”。

### 3.2 运行快速入门脚本

直接在根目录运行：

```bash
python example/quickstart_guide.py
```

你会做的事情（典型流程）：

- 输入/确认串口号（Windows 设备管理器里看到的 `COMx`）
- 连接电机（通常是 1-6 号关节；夹爪可能是 7 号，视你的硬件）
- 读取状态、执行小幅度运动验证链路

### 3.3 跑通后继续：完整交互示例

```bash
python example/sdk_quickstart.py
```

这个脚本更像“控制台版上位机”，适合用来：

- 复习关节运动 / 笛卡尔运动
- 测试夹爪与预设动作
- 在你写自己项目之前，先把基础能力跑顺

---

## 🎓 第4步：按角色选择深入学习路径（2-8小时）

> 更完整导航请直接看：`example/README.md` 与 `example/示例代码总导航.md`  
> 文档中心请看：`example/docs/index.md`

下面按真实开发角色给你“最短路径”，每一步都能落到仓库里**真实存在的文件**。

---

### 🔧 路径A：机械臂控制工程师（4-6小时）

**目标**：掌握电机控制、运动、同步控制、IO 联动，并具备工程化集成能力。

#### A1. 单电机与基础通信（30-60分钟）

- `example/control_sdk_examples/motor_usage_example.py`
- 完整参考（功能更多）：`example/test_interactive.py`

你需要掌握：

- 连接/断开（connect/disconnect）
- 停止（stop）与“失能（disable）”的安全区别（见 `example/docs/safety.md`）
- 位置/速度/力矩模式的基本用法（示例里都有）

#### A2. 6轴基础运动与预设动作（30-60分钟）

- `example/sdk_quickstart.py`
- 文档：`example/docs/motion.md`

你需要掌握：

- `move_joints`（关节空间）
- `move_cartesian`（笛卡尔空间）
- 预设动作的组织方式（`config/embodied_config/preset_actions.json`）

#### A3. 多电机同步（20-60分钟）

- 教学版：`example/control_sdk_examples/multi_motor_sync_example.py`
- 完整版：`example/test_multi_motor_sync.py`

你需要掌握：

- 同步控制的基本思想：一次性下发/触发/执行（示例会解释）
- 如何选择“教学版”与“完整版”（先学教学版，再看完整版）

#### A4. IO 集成（20-40分钟）

- `example/control_sdk_examples/io_control_example.py`
- 文档：`example/docs/io.md`

适用场景：

- 传感器触发（限位、光电、接近等）
- 执行器联动（继电器、气动、电磁阀、指示灯等）

#### A5. 工程化落地建议（你写项目时最常踩坑的点）

建议你在自己项目里做到：

- 把串口号、相机 ID、电机 ID 列表、速度/加速度、工作空间限制等全部做成可配置项
- 写“安全启动流程”：上电 → 自检 → 低速小幅度试动 → 正式运行
- 写“统一退出流程”：异常时 stop + disconnect（不要直接 disable）

---

### 👁️ 路径B：视觉应用开发者（3-5小时）

**目标**：掌握标定文件、像素到机械臂坐标、视觉抓取/跟随的基本流程，并能排查“抓不准”。

#### B1. 先把基础控制跑通（30分钟）

- `example/quickstart_guide.py`
- `example/control_sdk_examples/motor_usage_example.py`

#### B2. 视觉抓取示例（1-2小时）

- `example/control_sdk_examples/visual_grasp_example.py`
- 文档：`example/docs/vision.md`

你需要关注的配置与文件：

- `config/calibration_parameter.json`（标定参数）
- 视觉相关示例通常会做“自检”（是否存在标定文件等），建议先看输出再动手修改参数

#### B3. 常见问题与排查思路（很重要）

如果出现“抓取位置偏差大”，优先排查：

- 标定文件是否对应当前相机与安装位姿（换相机/换安装位置必须重标定或更新参数）
- TCP 偏移、抓取高度/接近高度是否合理（过低容易碰撞，过高会抓不到）
- 视觉输入的像素点是否来自同一分辨率/同一相机 ID

文档入口：

- `example/docs/troubleshooting.md`
- `example/docs/configuration.md`

---

### 🧠 路径C：AI 集成开发者（4-6小时）

**目标**：能跑通 AI 配置与示例，理解“AI 输出如何安全地驱动机械臂动作”，并能做基础的工程集成。

#### C1. 先理解配置（30-60分钟）

- `example/ai_sdk_examples/config_example.py`
- 配置文件：`config/aisdk_config.yaml`

#### C2. LLM / 多模态 / 语音（按需选择）

- LLM：`example/ai_sdk_examples/LLM_usage.py`
- 多模态：`example/ai_sdk_examples/multimodal_usage_example.py`
- 语音识别：`example/ai_sdk_examples/asr_usage_example.py`
- 语音合成：`example/ai_sdk_examples/tts_usage_example.py`
- 综合 Demo：
  - `example/ai_sdk_examples/smart_multimodal_chat_demo.py`
  - `example/ai_sdk_examples/smart_multimodal_voice_chat_demo.py`

#### C3. 具身智能（建议先在仿真验证，再上真机）

- 文档：`example/docs/embodied.md`

安全建议（强烈建议你遵守）：

- AI 输出必须做约束（速度、空间、姿态范围、动作类型白名单）
- 先在仿真/离线环境验证，再在真机小幅度、低速尝试

---

### 🎮 路径D：人机交互开发者（3-4小时）

**目标**：把“输入设备/交互逻辑/安全停止/状态显示”做成你能复用的交互组件。

仓库入口（按需选择）：

- 手柄文档：`example/docs/joycon.md`
- 手柄教学示例：`example/control_sdk_examples/joycon_control_example.py`
- 全功能控制台参考：`example/test_joycon_arm_control.py`
- 状态可视化：`example/test_joycon_display.py`

开发者工具（调试很有用）：

- `example/developer_tools/README.md`
- `example/developer_tools/joycon_sensor_display.py`

---

### 🎮 路径E：仿真开发者（1-2小时）

**目标**：在没有真实硬件时也能开发；在上真机前先验证轨迹/动作逻辑。

入口：

- 教学示例：`example/control_sdk_examples/digital_twin_example.py`
- 交互演示：`example/mujoco_control.py`
- 文档：`example/docs/simulation.md`

关键文件：

- `config/urdf/mjmodel.xml`

---

## 🛠️ 第5步：项目实践与工程化集成（持续）

这一部分是“从示例到你项目”的落地建议：字多但很实用，建议你在真正写业务代码前扫一遍。

---

### 5.1 推荐的项目集成方式（强烈建议照抄结构）

你可以在仓库根目录旁边新建自己的项目目录，例如：

```text
my_mark_project/
├── app/                         # 你的业务逻辑
│   ├── main.py
│   ├── robot/                   # 机械臂封装层（你自己写）
│   ├── vision/                  # 视觉封装层（你自己写）
│   └── io/                      # IO 封装层（你自己写）
├── configs/
│   └── config_local.yaml        # 你自己的部署参数（端口/相机ID/速度等）
└── README.md
```

并且把仓库里的 SDK 当作“依赖/子模块/同仓引用”，而不是把示例代码散落复制到各处。

---

### 5.2 你必须配置化的参数（不然一定会痛苦）

建议至少把这些参数全部配置化（配置文件/环境变量/命令行参数任选其一）：

- 串口号：`COMx`
- 电机 ID 列表：默认 1-6（夹爪可能是 7）
- 相机 ID：`camera_id`（默认 0）
- 最大速度、加速度、减速度（首次使用务必低速）
- 预设动作名称与对应关节角（`preset_actions.json`）
- 视觉抓取参数（抓取高度、接近高度、TCP 偏移等）
- 工作空间限制（半径/高度/禁区）

---

### 5.3 运行与部署（建议习惯性做的检查）

每次上线/每次更换环境，建议你都做一次“最小验证”：

1. 先跑 `example/quickstart_guide.py`（确认通信链路 OK）
2. 再跑 `example/sdk_quickstart.py`（确认 6 轴基本动作 OK）
3. 再跑你自己的业务脚本（逐步扩大动作范围）

为什么要这么做：

- 能快速区分是“硬件/连接问题”还是“你业务代码问题”
- 能避免“第一次就跑你的复杂业务”导致无法定位问题

---

### 5.4 故障排查的最短路径（别乱猜）

文档入口：

- `example/docs/troubleshooting.md`

最常见的 5 类问题与优先级：

1. **串口打不开**：端口号不对 / 被占用 / 设备驱动问题
2. **电机无响应**：ID 不对 / 供电问题 / 总线问题
3. **运动方向不对**：检查 `config/motor_config.json` 里的方向/减速比等
4. **视觉抓不准**：标定文件不匹配 / TCP 偏移不对 / 分辨率/相机 ID 不一致
5. **仿真起不来**：`mujoco` 未安装 / OpenGL 环境问题 / 模型文件缺失

---

## 📖 文档与资源索引（快速跳转）

### 你应该优先打开的 3 个入口

- `example/README.md`（示例总导航）
- `example/SDK完全介绍.md`（架构与核心概念）
- `example/docs/index.md`（文档中心总入口）

### 常用文档

- 安装：`example/docs/installation.md`
- 安全：`example/docs/safety.md`
- 快速入门：`example/docs/quickstart.md`
- 配置说明：`example/docs/configuration.md`
- API 参考：`example/docs/api_reference.md`
- API 详细：`example/docs/api_detailed.md`
- 故障排查：`example/docs/troubleshooting.md`

---

## 🧾 版本信息

- **版本**：Mark（Horizon_Arm2.0）
- **更新时间**：2026-02
- **维护**：HorizonArm Team


#

## 📊 学习进度自检表

根据您的学习目标，勾选已完成的项目：

### 🎯 基础掌握（所有开发者必须）

- [ ] 理解SDK架构和9个核心模块
- [ ] 成功连接一台电机
- [ ] 能够控制电机运动（速度/位置）
- [ ] 理解关节空间和笛卡尔空间
- [ ] 能够查阅示例代码并复用

### 🔧 控制工程师进阶

- [ ] 掌握单电机全部控制模式
- [ ] 实现多机同步控制
- [ ] 理解同步控制三阶段
- [ ] 集成IO传感器和执行器
- [ ] 能够调试电机参数（PID等）

### 👁️ 视觉开发者进阶

- [ ] 理解手眼标定原理
- [ ] 成功执行像素点抓取
- [ ] 实现视觉跟随功能
- [ ] 结合AI进行目标识别
- [ ] 能够独立进行相机标定

### 🤖 交互开发者进阶

- [ ] 配对并连接Joy-Con
- [ ] 实现手柄遥操作
- [ ] 配置自定义按键映射
- [ ] 实现IO联动控制
- [ ] 集成语音交互（可选）

### 🧠 AI开发者进阶

- [ ] 配置AI SDK
- [ ] 调用LLM API
- [ ] 实现多模态理解
- [ ] 集成语音识别和合成
- [ ] 实现AI驱动的机械臂控制

---

## 🆘 常见问题和解决方案

### Q1: 电机连接失败？

**检查清单：**
1. 串口号是否正确（设备管理器查看）
2. 电机ID是否正确
3. 电机是否上电
4. 没有其他程序占用串口

**参考：** `example/SDK完全介绍.md` 的"常见问题"部分或 `example/docs/troubleshooting.md`

### Q2: 多电机控制失败？

**解决方案：**
必须使用 `shared_interface=True`：
```python
for mid in [1, 2, 3, 4, 5, 6]:
    motor = create_motor_controller(motor_id=mid, shared_interface=True)
```

### Q3: 视觉抓取位置不准？

**检查：**
1. 是否完成手眼标定
2. 标定文件路径是否正确
3. 相机和机械臂位置是否改变

### Q4: 授权验证失败？

**联系技术支持获取授权文件**

---

## 📖 文档索引

### 核心文档

| 文档 | 位置 | 用途 |
|------|------|------|
| **开发者学习路线** | `开发者学习路线.md` | 本文档 - 完整学习路线 |
| **SDK完全介绍** | `example/SDK完全介绍.md` | SDK详细文档和架构说明 |
| **示例代码总导航** | `example/示例代码总导航.md` 或 `example/README.md` | 示例导航和快速开始 |
| **Control SDK指南** | `example/control_sdk_examples/README.md` | Control SDK学习路径 |
| **文档中心** | `example/docs/index.md` | 完整文档导航 |

### 示例代码

| 类型 | 位置 | 说明 |
|------|------|------|
| 快速入门 | `example/quickstart_guide.py` | 5分钟体验 |
| Control SDK | `example/control_sdk_examples/` | 7个教学示例 |
| AI SDK | `example/ai_sdk_examples/` | 10+个AI示例 |
| 完整参考 | `example/test_*.py` | 40+功能完整版 |
| 开发工具 | `example/developer_tools/` | 调试工具 |

---

## 🎓 学习建议

### 时间安排

- **兼职学习**：每天1-2小时，1周内完成基础路径
- **全职学习**：每天4-6小时，2-3天内完成基础路径
- **深入掌握**：持续2-4周，完成所有进阶内容

### 学习方法

1. **理论与实践结合**
   - 先看文档理解原理
   - 立即运行示例验证
   - 修改参数加深理解

2. **循序渐进**
   - 不要跳过基础内容
   - 按推荐顺序学习
   - 每个示例都要运行

3. **查看源码**
   - `Embodied_SDK/` 源码可以查看
   - 理解API实现逻辑
   - 学习代码组织方式

4. **动手实践**
   - 完成自检表中的所有项目
   - 尝试实现小项目
   - 遇到问题主动排查

---

## 📞 技术支持

遇到问题？按以下顺序解决：

1. **查看文档** - `example/SDK完全介绍.md` 的常见问题部分
2. **查看故障排除** - `example/docs/troubleshooting.md` 详细的故障诊断
3. **运行自检** - 相关示例的系统自检功能
4. **查看完整示例** - `example/test_interactive.py` 等完整版参考
5. **使用调试工具** - `example/developer_tools/` 下的专业工具
6. **联系技术支持** - 提供详细错误信息和日志

---

## 🎯 学习目标检验

### 基础能力（所有开发者必备）

完成基础学习后，您应该能够：

- ✅ **连接控制** - 独立连接和控制单个或多个电机
- ✅ **理解架构** - 理解SDK的模块组织和调用关系
- ✅ **查阅文档** - 能够快速查阅文档找到需要的API
- ✅ **复用代码** - 复用示例代码到自己的项目中
- ✅ **排查问题** - 能够根据错误信息初步排查问题
- ✅ **配置管理** - 理解和修改配置文件

### 进阶能力（根据专业方向）

#### 🔧 控制工程师
- ✅ 掌握三种电机控制模式（速度/位置/力矩）
- ✅ 实现多电机精确同步控制
- ✅ 集成IO传感器和执行器
- ✅ 调试和优化运动参数（PID等）
- ✅ 处理异常情况和安全保护

#### 👁️ 视觉开发者
- ✅ 理解手眼标定原理和流程
- ✅ 实现像素坐标到机械臂坐标转换
- ✅ 完成视觉引导抓取任务
- ✅ 集成AI进行目标识别和分类
- ✅ 优化视觉处理性能

#### 🤖 交互开发者
- ✅ 配置和使用Joy-Con手柄控制
- ✅ 自定义按键映射和控制参数
- ✅ 实现IO联动和传感器触发
- ✅ 集成语音识别和合成（可选）
- ✅ 设计直观的人机交互界面

#### 🧠 AI开发者
- ✅ 配置和调用LLM API
- ✅ 实现多模态理解（视觉+语言）
- ✅ 集成语音识别和语音合成
- ✅ 实现AI驱动的机械臂控制
- ✅ 设计具身智能应用

### 专家能力（高级开发者目标）

- ✅ **深入理解** - 理解SDK底层实现原理和通信协议
- ✅ **扩展开发** - 自定义扩展功能和新模块
- ✅ **性能优化** - 优化系统性能和稳定性
- ✅ **系统集成** - 集成到复杂的生产系统中
- ✅ **架构设计** - 设计大型机械臂应用的软件架构
- ✅ **问题诊断** - 快速诊断和解决复杂问题

---

## 📈 进阶学习资源

### 源码学习
- **Embodied_SDK/** - SDK源码可查看，学习实现原理
- **关键文件**:
  - `motion.py` - 运动学算法实现
  - `visual_grasp.py` - 手眼标定和坐标转换
  - `joycon.py` - 手柄控制映射逻辑
  - `digital_twin.py` - MuJoCo仿真接口

### 配置文件
- **config/** - 各种配置示例
  - `motor_config.json` - 电机参数配置
  - `calibration_parameter.json` - 标定参数
  - `aisdk_config.yaml` - AI服务配置
  - `preset_actions.json` - 预设动作定义

### 完整示例
- **test_interactive.py** - 40+功能的完整单电机工具
- **test_multi_motor_sync.py** - 26+功能的多机同步工具
- **sdk_quickstart.py** - 完整的机械臂控制框架

---

## 🎓 认证与考核（可选）

### 基础认证
完成以下任务即可认为掌握基础能力：
1. 独立编写程序连接并控制6个电机
2. 实现多电机同步运动
3. 集成一个IO传感器
4. 处理连接失败等异常情况

### 进阶认证
根据您的专业方向完成对应项目：
- **控制工程师**: 实现一个完整的自动化流程
- **视觉开发者**: 实现一个视觉引导抓取任务
- **交互开发者**: 实现一个手柄遥操作系统
- **AI开发者**: 实现一个自然语言控制的机械臂

---

## 🌟 成功案例参考

### 案例1：自动化生产线
- **应用**: 产品分拣和装配
- **技术栈**: 电机控制 + IO联动 + 视觉检测
- **学习时间**: 2周
- **关键技术**: 多机同步、IO触发、位置精度控制

### 案例2：智能服务机器人
- **应用**: 物品识别和递送
- **技术栈**: 视觉抓取 + AI识别 + 语音交互
- **学习时间**: 3周
- **关键技术**: 手眼标定、目标检测、自然语言理解

### 案例3：远程遥操作系统
- **应用**: 危险环境作业
- **技术栈**: 手柄控制 + 视觉反馈 + 力反馈
- **学习时间**: 2周
- **关键技术**: 实时控制、视频传输、安全保护

### 案例4：算法研究平台
- **应用**: 运动规划算法验证
- **技术栈**: 数字孪生 + 轨迹规划
- **学习时间**: 1周
- **关键技术**: MuJoCo仿真、逆运动学、碰撞检测

---

## 💪 持续成长建议

### 技术提升
- 📚 **阅读论文** - 了解机械臂和机器人领域前沿技术
- 💻 **开源贡献** - 参与相关开源项目
- 🎯 **实战项目** - 完成实际应用项目积累经验
- 🤝 **技术交流** - 参加技术社区和开发者交流

### 知识扩展
- **机械臂运动学** - 深入学习正逆运动学理论
- **计算机视觉** - 学习图像处理和目标识别
- **控制理论** - 学习PID控制和高级控制算法
- **AI技术** - 学习深度学习和强化学习

### 职业发展
- **机械臂应用工程师** - 负责机械臂系统集成和应用开发
- **机器人视觉工程师** - 专注于视觉引导和AI识别
- **自动化系统架构师** - 设计大型自动化系统
- **具身智能研究员** - 研究AI与机器人结合

---

**版本**: Mark  
**更新日期**: 2026-1  
**维护**: HorizonArm  

祝您学习顺利，成为优秀的机械臂开发者！🚀  
如有任何问题，欢迎查阅文档或联系技术支持。

