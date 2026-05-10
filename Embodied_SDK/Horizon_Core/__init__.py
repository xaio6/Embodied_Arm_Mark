#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Embodied_SDK.Horizon_Core 核心包
===================

说明：
- 将原来的 `core` / `Control_SDK` / `AI_SDK` 统一封装到一个命名空间包下；
- 上层通过本包提供的公开 API 访问各项功能；
- 目前阶段保持源码结构不变，仅调整导入路径，方便逐步迁移。
"""

from __future__ import annotations

# 作为命名空间导出三个子包，方便外层使用：
# - Embodied_SDK.Horizon_Core.core
# - Embodied_SDK.Horizon_Core.Control_SDK
# - Embodied_SDK.Horizon_Core.AI_SDK

# 网关模块（推荐所有上层代码通过此模块访问核心能力）

__all__ = [
    "core",
    "Control_SDK",
    "AI_SDK",
    "gateway",
]


