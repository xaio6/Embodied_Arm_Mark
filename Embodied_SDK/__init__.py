#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Embodied_SDK package exports.

核心导出点:
 - Visual/Follow grasp
 - Motion / JoyCon / IO / DigitalTwin
 - HorizonArmSDK / AI
 - create_configured_kinematics / load_kinematics_config
"""

from __future__ import annotations

import json
import math
import os
import sys
from typing import Any, Dict, List, Tuple


def _configure_console_encoding() -> None:
    """Keep Windows GBK consoles from crashing on SDK/example status icons."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


_configure_console_encoding()


_SDK_DIR = os.path.dirname(os.path.abspath(__file__))
if _SDK_DIR not in sys.path:
    sys.path.insert(0, _SDK_DIR)

from .visual_grasp import VisualGraspSDK, FollowGraspSDK
from .motion import MotionSDK
from .embodied import EmbodiedSDK
from .joycon import JoyconSDK
from .io import IOSDK
from .digital_twin import DigitalTwinSDK
from .horizon_sdk import HorizonArmSDK
from .ai import AISDK, DepthEstimationSDK
from .motion import (
    MotionSDK,
    create_motor_controller,
    setup_logging,
    close_all_shared_interfaces,
    get_shared_interface_info,
    get_function_codes,
)
from .gripper_sdk import ZDTGripperSDK
from Horizon_Core.core.arm_core.kinematics_factory import create_configured_kinematics as _kf_create_configured_kinematics
from Horizon_Core.core.arm_core.kinematics_factory import load_kinematics_config as _kf_load_kinematics_config
from Horizon_Core.core.arm_core.kinematics import RobotKinematics


def _load_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def _resolve_config_dir() -> str:
    if not getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(_SDK_DIR), "config")

    env_config = os.environ.get("HORIZONARM_CONFIG_DIR", "").strip()
    if env_config and os.path.isdir(env_config):
        return env_config

    env_data = os.environ.get("HORIZON_DATA_DIR", "").strip()
    if env_data:
        cand = os.path.join(env_data, "config")
        if os.path.isdir(cand):
            return cand

    return os.path.join(os.path.dirname(_SDK_DIR), "config")


def _normalize_joint_limits(raw_limits: Any) -> List[Tuple[float, float]]:
    if raw_limits is None:
        return [(-180.0, 180.0)] * 6

    if isinstance(raw_limits, list) and len(raw_limits) == 6:
        out: List[Tuple[float, float]] = []
        for it in raw_limits:
            if not isinstance(it, (list, tuple)) or len(it) != 2:
                return [(-180.0, 180.0)] * 6
            lo, hi = it
            out.append((float(lo), float(hi)))
        return out

    if isinstance(raw_limits, dict):
        out: List[Tuple[float, float]] = []
        for i in range(1, 7):
            it = raw_limits.get(str(i), raw_limits.get(i))
            if not isinstance(it, (list, tuple)) or len(it) != 2:
                return [(-180.0, 180.0)] * 6
            out.append((float(it[0]), float(it[1])))
        if len(out) == 6:
            return out

    return [(-180.0, 180.0)] * 6


def load_kinematics_config(force_reload: bool = False) -> Dict[str, Any]:
    """
    加载运动学配置。优先使用二进制接口返回值，若未加载成功则回退到本地配置文件。
    """
    cfg = _kf_load_kinematics_config(force_reload=force_reload)

    if cfg.get("loaded") and cfg.get("d") and cfg.get("a"):
        return cfg

    config_dir = _resolve_config_dir()
    config_path = os.path.join(config_dir, "dh_parameters_config.json")
    raw = _load_json(config_path)
    if not raw:
        return cfg

    dh = raw.get("dh_parameters", {}) or {}
    d = dh.get("d")
    a = dh.get("a")
    alpha_deg = dh.get("alpha_deg")
    if d is None or a is None or alpha_deg is None:
        return cfg

    return {
        "loaded": True,
        "source": config_path,
        "d": [float(v) for v in d],
        "a": [float(v) for v in a],
        "alpha": [math.radians(float(v)) for v in alpha_deg],
        "alpha_deg": [float(v) for v in alpha_deg],
        "joint_offsets": [float(v) for v in raw.get("joint_offsets", [0.0] * 6)],
        "joint_limits": _normalize_joint_limits(raw.get("joint_limits")),
        "angle_unit": raw.get("angle_unit", "deg") or "deg",
        "enable_offset": bool(raw.get("enable_offset", True)),
    }


def create_configured_kinematics():
    """
    创建运动学对象；若底层接口回退参数失效，则用本地 dh 配置文件强制对齐。
    """
    cfg = load_kinematics_config(force_reload=True)

    if cfg.get("loaded") and isinstance(cfg.get("d"), (list, tuple)) and isinstance(cfg.get("a"), (list, tuple)):
        try:
            d = [float(v) for v in cfg["d"]]
            a = [float(v) for v in cfg["a"]]
            angle_unit = cfg.get("angle_unit", "deg") or "deg"

            alpha = cfg.get("alpha")
            if not alpha:
                alpha_deg = cfg.get("alpha_deg", [])
                alpha = [math.radians(float(v)) for v in alpha_deg] if angle_unit == "deg" else [float(v) for v in alpha_deg]
            else:
                alpha = [float(v) for v in alpha]

            joint_limits = cfg.get("joint_limits", [(-180.0, 180.0)] * 6)
            if not isinstance(joint_limits, (list, tuple)):
                joint_limits = _normalize_joint_limits(joint_limits)
            if isinstance(joint_limits, list):
                joint_limits = [(float(a0), float(a1)) for a0, a1 in joint_limits]

            kin = RobotKinematics(
                d=d,
                a=a,
                alpha=alpha,
                joint_limits=joint_limits,
                angle_unit=angle_unit,
                joint_offsets=[float(v) for v in cfg.get("joint_offsets", [0.0] * 6)],
            )
            if bool(cfg.get("enable_offset", True)):
                kin.set_angle_offset([float(v) for v in cfg.get("joint_offsets", [0.0] * 6)])
            return kin
        except Exception:
            pass

    return _kf_create_configured_kinematics()


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
