"""
阿里云TTS提供商
使用DashScope SDK实现语音合成功能
支持CosyVoice和Sambert模型
"""

import os
import time
import asyncio
import threading
import concurrent.futures
from typing import Dict, Any, Generator, AsyncGenerator, Optional
import pyaudio
from ..base import BaseTTSProvider

try:
    import dashscope
    from dashscope.audio.tts_v2 import SpeechSynthesizer as CosyVoiceSynthesizer
    from dashscope.audio.tts import SpeechSynthesizer as SambertSynthesizer, ResultCallback, SpeechSynthesisResult
    from dashscope.api_entities.dashscope_response import SpeechSynthesisResponse
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False


class AlibabaTTSProvider(BaseTTSProvider):
    """阿里云TTS提供商"""

    # ------------------------------
    # Global barge-in support
    # ------------------------------
    # 用于“打断说话”：当检测到用户讲话时，外部可触发该中断事件，播放回调会尽快停止写入并关闭流
    _GLOBAL_INTERRUPT_EVENT = threading.Event()
    _GLOBAL_SPEAKING_EVENT = threading.Event()

    @classmethod
    def request_interrupt(cls):
        """请求打断当前语音播放（仅影响播放，不影响LLM/动作执行）"""
        try:
            cls._GLOBAL_INTERRUPT_EVENT.set()
            # 保险：某些异常路径下回调可能无法及时触发 on_close，提前清理 speaking 标志
            cls._GLOBAL_SPEAKING_EVENT.clear()
            print("🛑 [TTS] 收到打断请求：已停止当前语音播报")
        except Exception:
            pass

    @classmethod
    def clear_interrupt(cls):
        """清除打断标志（通常在开始播放时调用）"""
        try:
            cls._GLOBAL_INTERRUPT_EVENT.clear()
        except Exception:
            pass

    @classmethod
    def is_interrupted(cls) -> bool:
        try:
            return bool(cls._GLOBAL_INTERRUPT_EVENT.is_set())
        except Exception:
            return False

    @classmethod
    def mark_speaking(cls, speaking: bool):
        """标记当前是否正在播报（用于barge-in判断）"""
        try:
            if speaking:
                cls._GLOBAL_SPEAKING_EVENT.set()
            else:
                cls._GLOBAL_SPEAKING_EVENT.clear()
        except Exception:
            pass

    @classmethod
    def is_speaking(cls) -> bool:
        try:
            return bool(cls._GLOBAL_SPEAKING_EVENT.is_set())
        except Exception:
            return False
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        
        if not DASHSCOPE_AVAILABLE:
            raise ImportError("请安装 dashscope: pip install dashscope")
        
        # 设置API Key
        dashscope.api_key = api_key
        
        # 默认参数
        self.default_model = kwargs.get('model', 'cosyvoice-v1')
        self.default_voice = kwargs.get('voice', 'longxiaochun')
        self.default_sample_rate = kwargs.get('sample_rate', 22050)
        self.default_format = kwargs.get('format', 'mp3')
        
        # 支持的模型
        self.cosyvoice_models = ['cosyvoice-v1', 'cosyvoice-v2']
        self.sambert_models = ['sambert-zhichu-v1', 'sambert-zhixiaoxia-v1', 'sambert-zhixiaoyun-v1']
        
        # 支持的音频格式
        self.supported_formats = ['mp3', 'wav', 'pcm']
    
    def _is_cosyvoice_model(self, model: str) -> bool:
        """判断是否为CosyVoice模型"""
        return model in self.cosyvoice_models
    
    def _is_sambert_model(self, model: str) -> bool:
        """判断是否为Sambert模型"""
        return model in self.sambert_models
    
    def synthesize_to_file(self, text: str, output_file: str, **kwargs) -> Dict[str, Any]:
        """合成语音并保存到文件"""
        try:
            model = kwargs.get('model', self.default_model)
            voice = kwargs.get('voice', self.default_voice)
            sample_rate = kwargs.get('sample_rate', self.default_sample_rate)
            format_type = kwargs.get('format', self.default_format)
            
            start_time = time.time()
            
            if self._is_cosyvoice_model(model):
                # 使用CosyVoice模型
                synthesizer = CosyVoiceSynthesizer(model=model, voice=voice)
                audio_data = synthesizer.call(text)
                request_id = synthesizer.get_last_request_id()
                
                # 保存音频文件
                with open(output_file, 'wb') as f:
                    f.write(audio_data)
                
            elif self._is_sambert_model(model):
                # 使用Sambert模型
                result = SambertSynthesizer.call(
                    model=model,
                    text=text,
                    sample_rate=sample_rate,
                    format=format_type
                )
                
                request_id = result.get_response()['request_id']
                audio_data = result.get_audio_data()
                
                if audio_data is not None:
                    with open(output_file, 'wb') as f:
                        f.write(audio_data)
                else:
                    return {
                        'success': False,
                        'error': '音频数据为空',
                        'request_id': request_id
                    }
            else:
                return {
                    'success': False,
                    'error': f'不支持的模型: {model}',
                    'request_id': ''
                }
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'output_file': output_file,
                'model': model,
                'voice': voice,
                'text_length': len(text),
                'processing_time': processing_time,
                'request_id': request_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"语音合成失败: {str(e)}",
                'request_id': ''
            }
    
    async def synthesize_to_file_async(self, text: str, output_file: str, **kwargs) -> Dict[str, Any]:
        """异步合成语音并保存到文件"""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, self.synthesize_to_file, text, output_file, **kwargs)
            return result
    
    def synthesize_to_speaker(self, text: str, **kwargs) -> Dict[str, Any]:
        """合成语音并通过扬声器播放"""
        try:
            model = kwargs.get('model', self.default_model)
            voice = kwargs.get('voice', self.default_voice)
            sample_rate = kwargs.get('sample_rate', 48000)  # 扬声器播放推荐48kHz
            
            start_time = time.time()
            
            if self._is_cosyvoice_model(model):
                # CosyVoice暂不支持实时播放，先合成后播放
                synthesizer = CosyVoiceSynthesizer(model=model, voice=voice)
                audio_data = synthesizer.call(text)
                request_id = synthesizer.get_last_request_id()
                
                # 播放音频
                self._play_audio_data(audio_data, sample_rate, 'mp3')
                
            elif self._is_sambert_model(model):
                # 使用Sambert的流式播放
                class SpeakerCallback(ResultCallback):
                    def __init__(self, sample_rate):
                        self.player = None
                        self.stream = None
                        self.sample_rate = sample_rate
                        self.error_message = None
                        self.request_id = None
                        self._stopped = False
                    
                    def on_open(self):
                        print('🔊 开始语音播放...')
                        AlibabaTTSProvider.clear_interrupt()
                        AlibabaTTSProvider.mark_speaking(True)
                        self.player = pyaudio.PyAudio()
                        self.stream = self.player.open(
                            format=pyaudio.paInt16,
                            channels=1,
                            rate=self.sample_rate,
                            output=True
                        )
                    
                    def on_complete(self):
                        print('✅ 语音播放完成')
                    
                    def on_error(self, response: SpeechSynthesisResponse):
                        self.error_message = f'语音合成失败: {str(response)}'
                        print(f'❌ {self.error_message}')
                    
                    def on_close(self):
                        AlibabaTTSProvider.mark_speaking(False)
                        if self.stream:
                            try:
                                self.stream.stop_stream()
                                self.stream.close()
                            except Exception as e:
                                print(f"⚠️ 关闭音频流时出错: {e}")
                        if self.player:
                            try:
                                # 安全地关闭PyAudio，避免程序退出
                                self.player = None
                            except Exception as e:
                                print(f"⚠️ 关闭音频播放器时出错: {e}")
                        print('🔇 语音播放结束')
                    
                    def on_event(self, result: SpeechSynthesisResult):
                        if result.get_audio_frame() is not None:
                            # 支持打断：一旦外部请求interrupt，尽快停止写入并关闭流
                            if self._stopped or AlibabaTTSProvider.is_interrupted():
                                self._stopped = True
                                AlibabaTTSProvider.mark_speaking(False)
                                try:
                                    print("🛑 [TTS] 语音播报被打断")
                                except Exception:
                                    pass
                                try:
                                    if self.stream:
                                        self.stream.stop_stream()
                                        self.stream.close()
                                        self.stream = None
                                except Exception:
                                    pass
                                return
                            try:
                                if self.stream:
                                    self.stream.write(result.get_audio_frame())
                            except Exception:
                                # 写入失败时终止本次播放
                                self._stopped = True
                                return
                
                callback = SpeakerCallback(sample_rate)
                result = SambertSynthesizer.call(
                    model=model,
                    text=text,
                    sample_rate=sample_rate,
                    format='pcm',
                    callback=callback
                )
                
                request_id = result.get_response()['request_id']
                
                if callback.error_message:
                    return {
                        'success': False,
                        'error': callback.error_message,
                        'request_id': request_id
                    }
            else:
                return {
                    'success': False,
                    'error': f'不支持的模型: {model}',
                    'request_id': ''
                }
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'model': model,
                'voice': voice,
                'text_length': len(text),
                'processing_time': processing_time,
                'request_id': request_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"语音播放失败: {str(e)}",
                'request_id': ''
            }
    
    def _play_audio_data(self, audio_data: bytes, sample_rate: int, format_type: str):
        """播放音频数据"""
        try:
            if format_type == 'mp3':
                # 对于MP3格式，需要先解码
                # 这里简化处理，实际应用中可能需要使用pydub等库
                print("⚠️ MP3格式播放需要额外处理，建议使用PCM格式")
                return
            
            # 对于PCM格式，直接播放
            player = pyaudio.PyAudio()
            stream = player.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True
            )
            
            print('🔊 开始播放音频...')
            stream.write(audio_data)
            print('✅ 音频播放完成')
            
            stream.stop_stream()
            stream.close()
            # 安全地关闭PyAudio，避免程序退出
            # 不调用terminate()，让垃圾回收器处理
            player = None
            
        except Exception as e:
            print(f"❌ 音频播放失败: {e}")
    
    async def synthesize_to_speaker_async(self, text: str, **kwargs) -> Dict[str, Any]:
        """异步合成语音并通过扬声器播放"""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, self.synthesize_to_speaker, text, **kwargs)
            return result
    
    def synthesize_stream(self, text_stream, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """流式文本转语音"""
        try:
            model = kwargs.get('model', self.default_model)
            voice = kwargs.get('voice', self.default_voice)
            sample_rate = kwargs.get('sample_rate', 48000)
            
            if not self._is_cosyvoice_model(model):
                yield {
                    'success': False,
                    'error': 'Sambert模型不支持流式输入，请使用CosyVoice模型',
                    'request_id': ''
                }
                return
            
            # CosyVoice流式合成（这里需要根据实际API实现）
            # 注意：当前示例代码可能需要根据最新的API文档调整
            print("🔄 开始流式语音合成...")
            
            for text_chunk in text_stream:
                if text_chunk.strip():
                    try:
                        synthesizer = CosyVoiceSynthesizer(model=model, voice=voice)
                        audio_data = synthesizer.call(text_chunk)
                        request_id = synthesizer.get_last_request_id()
                        
                        yield {
                            'success': True,
                            'audio_data': audio_data,
                            'text_chunk': text_chunk,
                            'model': model,
                            'voice': voice,
                            'request_id': request_id
                        }
                        
                    except Exception as e:
                        yield {
                            'success': False,
                            'error': f"文本块合成失败: {str(e)}",
                            'text_chunk': text_chunk,
                            'request_id': ''
                        }
            
            print("✅ 流式语音合成完成")
            
        except Exception as e:
            yield {
                'success': False,
                'error': f"流式语音合成失败: {str(e)}",
                'request_id': ''
            }
    
    async def synthesize_stream_async(self, text_stream, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """异步流式文本转语音"""
        # 在线程池中运行同步生成器
        loop = asyncio.get_event_loop()
        
        def sync_generator():
            return list(self.synthesize_stream(text_stream, **kwargs))
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = await loop.run_in_executor(None, sync_generator)
            
            for result in results:
                yield result 

    def streaming_synthesize(self, **kwargs) -> 'StreamingSynthesizer':
        """创建流式语音合成器"""
        try:
            model = kwargs.get('model', self.default_model)
            voice = kwargs.get('voice', self.default_voice)
            sample_rate = kwargs.get('sample_rate', 22050)
            
            if self._is_cosyvoice_model(model):
                # 使用CosyVoice流式合成
                return CosyVoiceStreamingSynthesizer(model, voice, sample_rate)
            elif self._is_sambert_model(model):
                # Sambert暂不支持真正的流式，使用缓冲方式
                return SambertStreamingSynthesizer(model, voice, sample_rate)
            else:
                raise ValueError(f'不支持的模型: {model}')
                
        except Exception as e:
            raise Exception(f"创建流式合成器失败: {str(e)}")


class StreamingSynthesizer:
    """流式语音合成器基类"""
    
    def __init__(self, model: str, voice: str, sample_rate: int):
        self.model = model
        self.voice = voice
        self.sample_rate = sample_rate
        self.is_active = False
        
    def start(self):
        """开始流式合成"""
        raise NotImplementedError
        
    def add_text(self, text: str):
        """添加文本进行合成"""
        raise NotImplementedError
        
    def complete(self):
        """完成流式合成"""
        raise NotImplementedError
        
    def close(self):
        """关闭合成器"""
        raise NotImplementedError


class CosyVoiceStreamingSynthesizer(StreamingSynthesizer):
    """CosyVoice流式合成器"""
    
    def __init__(self, model: str, voice: str, sample_rate: int):
        super().__init__(model, voice, sample_rate)
        self.synthesizer = None
        self.callback = None
        
    def start(self):
        """开始流式合成"""
        try:
            from dashscope.audio.tts_v2 import SpeechSynthesizer, ResultCallback, AudioFormat
            
            class StreamingCallback(ResultCallback):
                def __init__(self, sample_rate):
                    self.player = None
                    self.stream = None
                    self.sample_rate = sample_rate
                    self.error_message = None
                    self._cleanup_needed = False  # 标记是否需要清理
                
                def on_open(self):
                    print('🔊 开始流式语音播放...')
                    AlibabaTTSProvider.clear_interrupt()
                    AlibabaTTSProvider.mark_speaking(True)
                    self.player = pyaudio.PyAudio()
                    self.stream = self.player.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=self.sample_rate,
                        output=True
                    )
                
                def on_complete(self):
                    print('✅ 流式语音播放完成')
                
                def on_error(self, message: str):
                    self.error_message = f'流式语音合成失败: {message}'
                    print(f'❌ {self.error_message}')
                
                def on_close(self):
                    # 标记需要清理，但不在回调中直接执行
                    self._cleanup_needed = True
                    AlibabaTTSProvider.mark_speaking(False)
                    print('🔇 流式语音播放结束')
                
                def cleanup_resources(self):
                    """在主线程中安全清理资源"""
                    if self._cleanup_needed:
                        if self.stream:
                            try:
                                self.stream.stop_stream()
                                self.stream.close()
                            except Exception as e:
                                print(f"⚠️ 音频清理出错: {e}")
                            finally:
                                self.stream = None
                        
                        if self.player:
                            try:
                                # 给PyAudio一些时间完成内部清理
                                import time
                                time.sleep(0.1)
                                self.player = None
                            except Exception as e:
                                print(f"⚠️ 清理音频播放器时出错: {e}")
                        
                        self._cleanup_needed = False
                
                def on_event(self, message):
                    pass
                
                def on_data(self, data: bytes) -> None:
                    if not data:
                        return
                    # 支持打断：不再写入并尽快关闭流
                    if AlibabaTTSProvider.is_interrupted():
                        AlibabaTTSProvider.mark_speaking(False)
                        try:
                            print("🛑 [TTS] 语音播报被打断")
                        except Exception:
                            pass
                        try:
                            if self.stream:
                                self.stream.stop_stream()
                                self.stream.close()
                                self.stream = None
                        except Exception:
                            pass
                        return
                    if self.stream:
                        try:
                            self.stream.write(data)
                        except Exception:
                            return
            
            self.callback = StreamingCallback(self.sample_rate)
            
            # 根据采样率选择音频格式
            if self.sample_rate == 22050:
                audio_format = AudioFormat.PCM_22050HZ_MONO_16BIT
            elif self.sample_rate == 16000:
                audio_format = AudioFormat.PCM_16000HZ_MONO_16BIT
            elif self.sample_rate == 8000:
                audio_format = AudioFormat.PCM_8000HZ_MONO_16BIT
            else:
                audio_format = AudioFormat.PCM_22050HZ_MONO_16BIT
                self.sample_rate = 22050
            
            self.synthesizer = SpeechSynthesizer(
                model=self.model,
                voice=self.voice,
                format=audio_format,
                callback=self.callback
            )
            
            self.is_active = True
            
        except Exception as e:
            raise Exception(f"启动CosyVoice流式合成器失败: {str(e)}")
    
    def add_text(self, text: str):
        """添加文本进行流式合成"""
        if not self.is_active or not self.synthesizer:
            raise Exception("流式合成器未启动")
        
        try:
            if text.strip():  # 只处理非空文本
                self.synthesizer.streaming_call(text)
        except Exception as e:
            print(f"⚠️ 流式合成文本失败: {e}")
    
    def complete(self):
        """完成流式合成"""
        if self.synthesizer and self.is_active:
            try:
                # 添加保护机制，避免streaming_complete()导致程序退出
                request_id = None
                try:
                    self.synthesizer.streaming_complete()
                    request_id = self.synthesizer.get_last_request_id()
                    print(f'🎉 流式合成完成，请求ID: {request_id}')
                except Exception as complete_error:
                    print(f"⚠️ streaming_complete()调用失败: {complete_error}")
                    # 尝试获取request_id，即使complete失败
                    try:
                        request_id = self.synthesizer.get_last_request_id()
                    except:
                        pass
                
                # 强制标记为非活跃状态
                self.is_active = False
                return request_id
                
            except Exception as e:
                print(f"⚠️ 完成流式合成失败: {e}")
                self.is_active = False
                return None
        else:
            return None
    
    def close(self):
        """关闭合成器"""
        self.is_active = False
        
        try:
            if self.callback:
                # 先触发回调的on_close来标记需要清理
                self.callback.on_close()
                # 然后在主线程中安全清理资源
                self.callback.cleanup_resources()
        except Exception as callback_error:
            print(f"⚠️ 回调清理时出错: {callback_error}")
        
        try:
            # 清理合成器引用
            if self.synthesizer:
                self.synthesizer = None
        except Exception as synthesizer_error:
            print(f"⚠️ 清理合成器时出错: {synthesizer_error}")
        
        # 强制进行垃圾回收
        try:
            import gc
            gc.collect()
        except Exception as gc_error:
            print(f"⚠️ 垃圾回收时出错: {gc_error}")
        
        print("✅ 流式合成器已关闭")


class SambertStreamingSynthesizer(StreamingSynthesizer):
    """Sambert流式合成器（缓冲模式）"""
    
    def __init__(self, model: str, voice: str, sample_rate: int):
        super().__init__(model, voice, sample_rate)
        self.text_buffer = ""
        self.player = None
        self.stream = None
        
    def start(self):
        """开始流式合成"""
        try:
            print('🔊 开始Sambert流式语音播放...')
            self.player = pyaudio.PyAudio()
            self.stream = self.player.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True
            )
            self.is_active = True
            
        except Exception as e:
            raise Exception(f"启动Sambert流式合成器失败: {str(e)}")
    
    def add_text(self, text: str):
        """添加文本进行合成（缓冲模式）"""
        if not self.is_active:
            raise Exception("流式合成器未启动")
        
        self.text_buffer += text
        
        # 检查是否有完整句子可以合成
        for punct in ['。', '！', '？', '.', '!', '?']:
            if punct in self.text_buffer:
                sentence_end = self.text_buffer.find(punct) + 1
                complete_sentence = self.text_buffer[:sentence_end].strip()
                
                if complete_sentence:
                    # 合成并播放这个句子
                    self._synthesize_and_play(complete_sentence)
                
                # 更新缓冲区
                self.text_buffer = self.text_buffer[sentence_end:].strip()
                break
    
    def _synthesize_and_play(self, text: str):
        """合成并播放文本"""
        try:
            result = SambertSynthesizer.call(
                model=self.model,
                text=text,
                sample_rate=self.sample_rate,
                format='pcm'
            )
            
            audio_data = result.get_audio_data()
            if audio_data and self.stream:
                self.stream.write(audio_data)
                
        except Exception as e:
            print(f"⚠️ Sambert合成播放失败: {e}")
    
    def complete(self):
        """完成流式合成"""
        # 处理剩余的文本
        if self.text_buffer.strip():
            self._synthesize_and_play(self.text_buffer.strip())
            self.text_buffer = ""
        
        print('✅ Sambert流式语音播放完成')
    
    def close(self):
        """关闭合成器"""
        self.is_active = False
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                print(f"⚠️ 关闭音频流时出错: {e}")
        
        if self.player:
            try:
                # 安全地关闭PyAudio，避免程序退出
                # 不调用terminate()，让垃圾回收器处理
                self.player = None
            except Exception as e:
                print(f"⚠️ 关闭音频播放器时出错: {e}")
        print('🔇 Sambert流式语音播放结束') 