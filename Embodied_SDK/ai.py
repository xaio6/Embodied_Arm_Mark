#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI SDK 封装
==========

提供对 AI 能力的访问，底层通过 Embodied_SDK.Horizon_Core.gateway 进行统一入口转发。
"""

from Embodied_SDK.Horizon_Core import gateway

class AISDK:
    """
    AI SDK 封装类。
    
    所有调用都会转发给底层的 Embodied_SDK.Horizon_Core.AI_SDK.AISDK 实例。
    实例化时会自动进行核心可用性检查。
    """
    def __init__(self, *args, **kwargs):
        self._internal_sdk = gateway.create_aisdk(*args, **kwargs)

    def chat(self, prompt: str, provider: str = "alibaba", model: str = "qwen-turbo", **kwargs):
        """
        🤖 统一聊天接口
        Args:
            prompt: 提示词
            provider: 提供商名称，默认 "alibaba"
            model: 模型名称，默认 "qwen-turbo"
            **kwargs: 其他参数 (stream, use_context 等)
        """
        return self._internal_sdk.chat(provider=provider, model=model, prompt=prompt, **kwargs)

    def asr(self, mode: str, provider: str = "alibaba", **kwargs):
        """
        🎤 统一语音识别接口
        Args:
            mode: 识别模式 ("file", "microphone", "stream", "keyword")
            provider: 提供商名称，默认 "alibaba"
            **kwargs: 其他参数 (audio_file, duration 等)
        """
        return self._internal_sdk.asr(provider=provider, mode=mode, **kwargs)

    def tts(self, text: str, mode: str = "speaker", provider: str = "alibaba", **kwargs):
        """
        🔊 统一语音合成接口
        Args:
            text: 要合成的文本
            mode: 合成模式 ("file", "speaker", "stream")，默认 "speaker"
            provider: 提供商名称，默认 "alibaba"
            **kwargs: 其他参数 (output_file, model, voice 等)
        """
        return self._internal_sdk.tts(provider=provider, mode=mode, text=text, **kwargs)

    def multimodal(self, prompt: str, mode: str, provider: str = "alibaba", **kwargs):
        """
        🤖🎥 统一多模态接口
        Args:
            prompt: 提示词
            mode: 模式 ("image", "video", "multiple_images")
            provider: 提供商名称，默认 "alibaba"
            **kwargs: 其他参数 (image_path, video_path 等)
        """
        return self._internal_sdk.multimodal(provider=provider, mode=mode, prompt=prompt, **kwargs)

    def smart_chat(self, prompt: str, llm_provider: str = "alibaba", tts_provider: str = "alibaba", **kwargs):
        """
        🤖🔊 LLM + TTS 智能对话
        Args:
            prompt: 用户问题
            llm_provider: LLM提供商，默认 "alibaba"
            tts_provider: TTS提供商，默认 "alibaba"
            **kwargs: 其他参数 (llm_model, tts_model, stream_chat 等)
        """
        return self._internal_sdk.smart_chat(prompt=prompt, llm_provider=llm_provider, tts_provider=tts_provider, **kwargs)

    def smart_multimodal_chat(self, prompt: str, multimodal_provider: str = "alibaba", tts_provider: str = "alibaba", **kwargs):
        """
        🤖🎥🔊 多模态智能对话
        Args:
            prompt: 用户问题
            multimodal_provider: 多模态提供商，默认 "alibaba"
            tts_provider: TTS提供商，默认 "alibaba"
            **kwargs: 其他参数 (image_path, video_path, stream_output 等)
        """
        return self._internal_sdk.smart_multimodal_chat(prompt=prompt, multimodal_provider=multimodal_provider, tts_provider=tts_provider, **kwargs)

    def smart_voice_chat(self, llm_provider: str = "alibaba", tts_provider: str = "alibaba", **kwargs):
        """
        🎙️🤖🔊 智能语音对话
        Args:
            llm_provider: LLM提供商，默认 "alibaba"
            tts_provider: TTS提供商，默认 "alibaba"
            **kwargs: 其他参数 (duration, llm_model, tts_model 等)
        """
        return self._internal_sdk.smart_voice_chat(llm_provider=llm_provider, tts_provider=tts_provider, **kwargs)

    def smart_multimodal_voice_chat(self, llm_provider: str = "alibaba", tts_provider: str = "alibaba", **kwargs):
        """
        🎙️🖼️🔊 智能多模态语音对话
        Args:
            llm_provider: LLM提供商，默认 "alibaba"
            tts_provider: TTS提供商，默认 "alibaba"
            **kwargs: 其他参数 (image_path, video_path, duration 等)
        """
        return self._internal_sdk.smart_multimodal_voice_chat(llm_provider=llm_provider, tts_provider=tts_provider, **kwargs)

    def __getattr__(self, name):
        # 将其他属性访问转发给内部实例
        return getattr(self._internal_sdk, name)

class DepthEstimationSDK:
    """
    深度估计 SDK 封装类。
    
    所有调用都会转发给底层的 DepthEstimationSDK 实例。
    实例化时会自动进行核心可用性检查。
    """
    def __init__(self, *args, **kwargs):
        self._internal_sdk = gateway.create_depth_estimation_sdk(*args, **kwargs)

    def __getattr__(self, name):
        # 将所有属性访问转发给内部实例
        return getattr(self._internal_sdk, name)
