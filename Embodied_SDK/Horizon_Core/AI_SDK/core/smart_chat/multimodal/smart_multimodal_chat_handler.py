"""
Smart Multimodal Chat 处理器
负责处理多模态智能对话的内部逻辑
"""

from typing import Dict, Any, List
import asyncio
import concurrent.futures
import traceback
import base64
import os


class SmartMultiModalChatHandler:
    """多模态智能对话功能处理器"""
    
    def __init__(self, sdk_instance):
        """
        初始化多模态智能对话处理器
        
        Args:
            sdk_instance: AISDK实例
        """
        self.sdk = sdk_instance
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """将图像文件编码为Base64格式"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            raise Exception(f"图像编码失败: {str(e)}")
    
    def _get_image_content_type(self, image_path: str) -> str:
        """根据文件扩展名获取Content Type"""
        ext = os.path.splitext(image_path)[1].lower()
        content_type_map = {
            '.bmp': 'image/bmp', '.dib': 'image/bmp', '.icns': 'image/icns',
            '.ico': 'image/x-icon', '.jfif': 'image/jpeg', '.jpe': 'image/jpeg',
            '.jpeg': 'image/jpeg', '.jpg': 'image/jpeg', '.j2c': 'image/jp2',
            '.j2k': 'image/jp2', '.jp2': 'image/jp2', '.jpc': 'image/jp2',
            '.jpf': 'image/jp2', '.jpx': 'image/jp2', '.apng': 'image/png',
            '.png': 'image/png', '.bw': 'image/sgi', '.rgb': 'image/sgi',
            '.rgba': 'image/sgi', '.sgi': 'image/sgi', '.tif': 'image/tiff',
            '.tiff': 'image/tiff', '.webp': 'image/webp'
        }
        return content_type_map.get(ext, 'image/jpeg')
    
    def _prepare_image_content(self, image_path: str) -> Dict[str, Any]:
        """准备图像内容，支持本地文件和URL"""
        if image_path.startswith(('http://', 'https://')):
            # URL
            return {
                "type": "image_url",
                "image_url": {"url": image_path}
            }
        else:
            # 本地文件路径
            base64_image = self._encode_image_to_base64(image_path)
            content_type = self._get_image_content_type(image_path)
            return {
                "type": "image_url",
                "image_url": {"url": f"data:{content_type};base64,{base64_image}"}
            }
    
    def _prepare_video_content(self, video_path: str) -> Dict[str, Any]:
        """准备视频内容，支持本地文件和URL"""
        if video_path.startswith(('http://', 'https://')):
            # URL
            return {
                "type": "video_url",
                "video_url": {"url": video_path}
            }
        else:
            # 本地文件路径
            with open(video_path, "rb") as video_file:
                base64_video = base64.b64encode(video_file.read()).decode("utf-8")
            return {
                "type": "video_url",
                "video_url": {"url": f"data:video/mp4;base64,{base64_video}"}
            }

    def handle_sync(self, prompt: str, image_path: str, video_path: str, 
                   image_paths: List[str], multimodal_provider: str,
                   tts_provider: str, tts_mode: str, stream_output: bool,
                   realtime_tts: bool, multimodal_kwargs: dict, 
                   tts_kwargs: dict) -> Dict[str, Any]:
        """同步多模态智能对话实现"""
        try:
            # 确定多模态模式
            if image_paths:
                mode = "multiple_images"
                media_info = f"{len(image_paths)}张图片"
            elif video_path:
                mode = "video"
                media_info = f"视频: {video_path}"
            elif image_path:
                mode = "image"
                media_info = f"图片: {image_path}"
            else:
                raise ValueError("必须提供 image_path、video_path 或 image_paths 中的至少一个参数")
            
            if stream_output and tts_mode == "speaker" and realtime_tts:
                # 🚀 流式输出 + 实时语音播放
                # 准备消息格式
                messages = self._prepare_multimodal_messages(
                    prompt, image_path, video_path, image_paths
                )
                
                answer_parts = []
                
                # 创建流式TTS合成器
                try:
                    streaming_synthesizer = self.sdk.tts_handler.create_streaming_synthesizer(
                        provider=tts_provider,
                        **tts_kwargs
                    )
                    streaming_synthesizer.start()
                except Exception as tts_init_error:
                    # 回退到非实时模式
                    return self._handle_non_realtime(
                        prompt, image_path, video_path, image_paths,
                        multimodal_provider, tts_provider, tts_mode,
                        stream_output, multimodal_kwargs, tts_kwargs
                    )
                
                try:
                    # 流式多模态对话
                    for chunk in self.sdk.multimodal_handler.chat_with_image_stream(
                        multimodal_provider, messages, **multimodal_kwargs
                    ):
                        if 'choices' in chunk and chunk['choices']:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                print(content, end='', flush=True)
                                answer_parts.append(content)
                                
                                # 🎵 实时将每个字符/词发送给TTS合成器
                                streaming_synthesizer.add_text(content)
                    
                    # 完成流式合成
                    request_id = streaming_synthesizer.complete()
                    answer = ''.join(answer_parts)
                    print()  # 换行
                    
                    return {
                        'success': True,
                        'answer': answer,
                        'mode': mode,
                        'media_info': media_info,
                        'multimodal_provider': multimodal_provider,
                        'multimodal_model': multimodal_kwargs.get('model'),
                        'tts_provider': tts_provider,
                        'tts_model': tts_kwargs.get('model'),
                        'tts_mode': 'realtime_speaker',
                        'tts_result': {'success': True, 'mode': 'realtime', 'request_id': request_id}
                    }
                    
                except Exception as e:
                    return {
                        'success': False,
                        'error': f"流式多模态对话过程出错: {str(e)}"
                    }
                finally:
                    # 确保关闭合成器
                    try:
                        streaming_synthesizer.close()
                    except Exception as close_error:
                        print(f"⚠️ 关闭流式合成器时出错: {close_error}")
                        # 不再抛出异常，避免影响主流程
            
            else:
                # 非实时模式
                return self._handle_non_realtime(
                    prompt, image_path, video_path, image_paths,
                    multimodal_provider, tts_provider, tts_mode,
                    stream_output, multimodal_kwargs, tts_kwargs
                )
                
        except Exception as e:
            print(f"❌ 多模态智能对话出错: {str(e)}")
            print(traceback.format_exc())  # 打印完整堆栈
            return {
                'success': False,
                'error': f"多模态智能对话过程出错: {str(e)}"
            }

    def _handle_non_realtime(self, prompt: str, image_path: str, video_path: str,
                           image_paths: List[str], multimodal_provider: str,
                           tts_provider: str, tts_mode: str, stream_output: bool,
                           multimodal_kwargs: dict, tts_kwargs: dict) -> Dict[str, Any]:
        """非实时多模态智能对话实现"""
        try:
            print(f"🔄 使用非实时模式处理多模态内容")
            # 确定多模态模式
            if image_paths:
                mode = "multiple_images"
                media_info = f"{len(image_paths)}张图片"
            elif video_path:
                mode = "video"
                media_info = f"视频: {video_path}"
            elif image_path:
                mode = "image"
                media_info = f"图片: {image_path}"
            else:
                raise ValueError("必须提供 image_path、video_path 或 image_paths 中的至少一个参数")
            
            if stream_output:
                # 流式输出但不实时播放
                messages = self._prepare_multimodal_messages(
                    prompt, image_path, video_path, image_paths
                )
                
                answer_parts = []
                for chunk in self.sdk.multimodal_handler.chat_with_image_stream(
                    multimodal_provider, messages, **multimodal_kwargs
                ):
                    if 'choices' in chunk and chunk['choices']:
                        delta = chunk['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            print(content, end='', flush=True)
                            answer_parts.append(content)
                
                answer = ''.join(answer_parts)
                print()  # 换行
            else:
                # 普通输出
                print(f"🖼️ 调用多模态处理: {multimodal_provider}")
                if image_paths:
                    result = self.sdk.multimodal(
                        multimodal_provider, "multiple_images", prompt,
                        image_paths=image_paths, **multimodal_kwargs
                    )
                elif video_path:
                    result = self.sdk.multimodal(
                        multimodal_provider, "video", prompt,
                        video_path=video_path, **multimodal_kwargs
                    )
                else:
                    print(f"🖼️ 处理图片: {image_path}")
                    result = self.sdk.multimodal(
                        multimodal_provider, "image", prompt,
                        image_path=image_path, **multimodal_kwargs
                    )
                
                if result.get('success', True) and 'response' in result:
                    answer = result['response']['choices'][0]['message']['content']
                    print(f"✓ 获取到多模态回答: {answer[:50]}...")
                else:
                    print(f"❌ 未获取到有效的多模态回答，结果: {result}")
                    return {
                        'success': False,
                        'error': '未获取到有效的多模态回答',
                        'multimodal_response': result
                    }
            
            # 语音合成
            if answer.strip():
                print(f"🔊 开始语音合成: {tts_mode} 模式")
                tts_result = self.sdk.tts(
                    provider=tts_provider,
                    mode=tts_mode,
                    text=answer,
                    **tts_kwargs
                )
                
                return {
                    'success': True,
                    'answer': answer,
                    'mode': mode,
                    'media_info': media_info,
                    'multimodal_provider': multimodal_provider,
                    'multimodal_model': multimodal_kwargs.get('model'),
                    'tts_provider': tts_provider,
                    'tts_model': tts_kwargs.get('model'),
                    'tts_mode': tts_mode,
                    'tts_result': tts_result
                }
            else:
                print("❌ 回答为空，跳过语音合成")
                return {
                    'success': False,
                    'error': '获取到空回答'
                }
                
        except Exception as e:
            print(f"❌ 非实时多模态处理错误: {str(e)}")
            print(traceback.format_exc())  # 打印完整堆栈
            return {
                'success': False,
                'error': f"非实时多模态对话过程出错: {str(e)}"
            }

    def _prepare_multimodal_messages(self, prompt: str, image_path: str, video_path: str,
                                    image_paths: List[str]) -> List[Dict[str, Any]]:
        """准备多模态消息格式，支持本地文件和URL"""
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}]
            }
        ]
        
        # 准备用户消息内容
        content = []
        
        # 添加媒体内容
        if image_paths:
            # 多张图片
            for img_path in image_paths:
                content.append(self._prepare_image_content(img_path))
        elif video_path:
            # 视频
            content.append(self._prepare_video_content(video_path))
        elif image_path:
            # 单张图片
            content.append(self._prepare_image_content(image_path))
        
        # 添加文本提示
        content.append({"type": "text", "text": prompt})
        
        messages.append({
            "role": "user",
            "content": content
        })
        
        return messages

    async def handle_async(self, prompt: str, image_path: str, video_path: str,
                          image_paths: List[str], multimodal_provider: str,
                          tts_provider: str, tts_mode: str, stream_output: bool,
                          realtime_tts: bool, multimodal_kwargs: dict,
                          tts_kwargs: dict) -> Dict[str, Any]:
        """异步多模态智能对话实现"""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                self.handle_sync,
                prompt, image_path, video_path, image_paths,
                multimodal_provider, tts_provider, tts_mode,
                stream_output, realtime_tts, multimodal_kwargs, tts_kwargs
            )
            return result 