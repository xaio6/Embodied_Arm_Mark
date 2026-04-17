"""
智能语音对话处理器

集成ASR语音识别、LLM对话和TTS语音合成的完整智能语音交互功能
"""

from typing import Dict, Any, List
import time
import logging

logger = logging.getLogger(__name__)

class SmartVoiceChatHandler:
    """
    智能语音对话处理器类
    
    管理麦克风输入、语音识别、LLM对话和语音回复的完整流程
    
    功能：
    - 支持关键词唤醒
    - 麦克风语音录入
    - 流式LLM处理
    - 实时语音合成播放
    - 上下文对话支持
    - 语音指令控制
    """
    
    def __init__(self, sdk):
        """
        初始化智能语音对话处理器
        
        Args:
            sdk: AI SDK实例
        """
        self.sdk = sdk
    
    def handle_voice_chat(self,
                          duration: int = 5,
                          llm_provider: str = "alibaba",
                          llm_model: str = "qwen-turbo",
                          tts_provider: str = "alibaba",
                          tts_model: str = "sambert-zhichu-v1",
                          use_context: bool = True,
                          session_id: str = "voice_chat",
                          continue_conversation: bool = True,
                          activation_phrase: str = "你好助手",
                          activate_once: bool = True,
                          end_phrase: str = "结束对话",
                          silence_timeout: float = 2.0,
                          verbose: bool = False,
                          **kwargs) -> Dict[str, Any]:
        """
        处理完整的语音对话流程
        
        Args:
            duration: 每次录音的最大秒数，默认5秒
            llm_provider: LLM提供商名称，默认"alibaba"
            llm_model: LLM模型名称，默认"qwen-turbo"
            tts_provider: TTS提供商名称，默认"alibaba"
            tts_model: TTS模型名称，默认"sambert-zhichu-v1"
            use_context: 是否启用上下文对话，默认True
            session_id: 会话ID，默认"voice_chat"
            continue_conversation: 是否持续对话，默认True
            activation_phrase: 激活短语，说出此短语开始对话，为None时不需要激活短语
            activate_once: 是否只需激活一次，默认True，即首次启动对话时需要激活，后续对话不需要
            end_phrase: 结束对话的短语，默认"结束对话"
            silence_timeout: 静音超时时间（秒），检测到静音这么长时间后认为语音输入结束
            verbose: 是否输出详细日志，默认False
            **kwargs: 其他参数，包括LLM和TTS的参数
            
        Returns:
            Dict[str, Any]: 对话结果信息
        """
        if verbose:
            logger.info("智能语音对话已启动...")
        print("🎙️ 智能语音对话已启动...")
        
        # 提取TTS参数
        voice = kwargs.pop('voice', None)
        
        # 从kwargs中提取静默参数，如果没有则创建新的
        tts_kwargs = kwargs.copy()
        # 设置TTS的静默参数，避免过多日志输出
        if not verbose:
            tts_kwargs['silent'] = True
        
        conversation_active = True
        waiting_for_activation = activation_phrase is not None
        # 如果需要激活且只激活一次，则第一次激活后就不再需要等待激活
        activated_once = False
        result = {"success": True, "conversations": []}
        
        try:
            while conversation_active:
                # 只有当需要激活短语且(不是只激活一次或者是第一次对话时)，才需等待激活
                if waiting_for_activation and (not activate_once or not activated_once):
                    if verbose:
                        logger.info(f"等待激活短语: '{activation_phrase}'...")
                    print(f"等待激活短语: '{activation_phrase}'...")
                    
                    # 使用关键词模式等待激活短语
                    for keyword_result in self.sdk.asr(
                        provider=llm_provider,
                        mode="keyword",
                        keywords=[activation_phrase],
                        detection_threshold=0.6,
                        silence_timeout=1.0
                    ):
                        if keyword_result.get('success') and keyword_result.get('keyword_detected'):
                            if verbose:
                                logger.info(f"已激活! 检测到: '{keyword_result['keyword_detected']}'")
                            print(f"✓ 已激活! 检测到: '{keyword_result['keyword_detected']}'")
                            waiting_for_activation = False
                            activated_once = True
                            break
                
                # 已激活，开始正常对话
                print("🎤 正在聆听...(语音停止或说出结束短语将发送对话)")
                
                # 使用麦克风模式获取语音输入
                try:
                    asr_result = self.sdk.asr(
                        provider=llm_provider,
                        mode="microphone",
                        duration=duration,
                        enable_voice_detection=True,
                        enable_punctuation_prediction=True,
                        silence_timeout=silence_timeout,
                        **kwargs
                    )
                except Exception as e:
                    if verbose:
                        logger.error(f"录音错误: {str(e)}")
                    print(f"🎤 录音错误: {str(e)}")
                    print("🔄 将在3秒后重试...")
                    time.sleep(3)
                    continue
                
                if not asr_result.get('success'):
                    error_msg = asr_result.get('error', '未知错误')
                    if verbose:
                        logger.error(f"语音识别失败: {error_msg}")
                    print(f"❌ 语音识别失败: {error_msg}")
                    print("🔄 将在3秒后重试...")
                    time.sleep(3)
                    continue
                
                user_input = asr_result.get('text', '').strip()
                
                # 检查是否为结束对话的短语
                # 使用更宽松的匹配方式，允许标点符号和大小写差异
                cleaned_input = user_input.lower().replace("。", "").replace(".", "").strip()
                cleaned_end_phrase = end_phrase.lower().replace("。", "").replace(".", "").strip() if end_phrase else ""
                
                # 使用精确匹配清理后的字符串
                if end_phrase and cleaned_input == cleaned_end_phrase:
                    if verbose:
                        logger.info("检测到结束对话指令，正在结束会话...")
                    print("👋 已检测到结束对话指令，正在结束会话...")
                    
                    conversation_active = False
                    # 直接返回结果，不继续后续的对话循环
                    return result
                
                if not user_input:
                    print("❓ 未检测到有效语音输入，请再试一次")
                    continue
                
                if verbose:
                    logger.info(f"已识别: '{user_input}'")
                print(f"🔍 已识别: '{user_input}'")
                
                # 发送到LLM获取回复
                print("🤖 AI思考中...")
                llm_response = self.sdk.chat(
                    provider=llm_provider,
                    model=llm_model,
                    prompt=user_input,
                    use_context=use_context,
                    session_id=session_id,
                    stream=True,
                    **kwargs
                )
                
                # 处理LLM响应并通过TTS播放
                ai_response = self._process_llm_response(
                    llm_response, 
                    tts_provider, 
                    tts_model, 
                    voice, 
                    tts_kwargs, 
                    verbose
                )
                
                # 记录本次对话
                conversation_record = {
                    "user_input": user_input,
                    "ai_response": ai_response
                }
                result["conversations"].append(conversation_record)
                
                print("\n✓ 回答完成")
                
                # 如果不是持续对话模式，退出循环
                if not continue_conversation:
                    conversation_active = False
                else:
                    # 如果需要激活短语，且不是只激活一次或者没有激活过，则等待激活
                    waiting_for_activation = activation_phrase is not None and (not activate_once or not activated_once)
                    if waiting_for_activation:
                        print(f"等待下一次激活...")
                    else:
                        print("准备下一轮对话...")
                        
        except KeyboardInterrupt:
            if verbose:
                logger.info("用户中断，结束对话")
            print("\n👋 用户中断，结束对话")
        except Exception as e:
            if verbose:
                logger.error(f"发生错误: {str(e)}")
            print(f"❌ 发生错误: {str(e)}")
            result = {"success": False, "error": str(e), "conversations": result.get("conversations", [])}
        
        print("🎙️ 智能语音对话已结束")
        return result

    def _process_llm_response(self,
                             llm_response,
                             tts_provider: str,
                             tts_model: str,
                             voice: str,
                             tts_kwargs: Dict[str, Any],
                             verbose: bool) -> str:
        """
        处理LLM流式响应并通过TTS播放
        
        Args:
            llm_response: LLM流式响应迭代器
            tts_provider: TTS提供商
            tts_model: TTS模型
            voice: 语音音色
            tts_kwargs: TTS参数
            verbose: 是否输出详细日志
            
        Returns:
            str: 完整的AI响应文本
        """
        # 准备收集完整回复
        full_response = ""
        response_chunks = []
        print_buffer = ""  # 用于缓存打印内容
        
        # 实时处理LLM流式回复并通过TTS播放
        for chunk in llm_response:
            if 'choices' in chunk and chunk['choices'][0].get('delta', {}).get('content'):
                content = chunk['choices'][0]['delta']['content']
                full_response += content
                response_chunks.append(content)
                print_buffer += content  # 累积打印内容
                
                # 当累积到句子结束标记或达到一定长度时处理
                # 以自然语句为单位进行分段，避免频繁播放短句
                sentence_end = ['.', '。', '!', '！', '?', '？']
                paragraph_end = ['\n']
                
                # 检查是否遇到句子或段落结束，或累积了足够长的内容
                if (content in sentence_end or content in paragraph_end or len(response_chunks) >= 50):
                    text_to_speak = ''.join(response_chunks)
                    
                    if text_to_speak.strip():
                        # 输出当前内容供用户查看，只打印一次避免频繁输出
                        print(f"🔊 {print_buffer}", end="", flush=True)
                        print_buffer = ""  # 清空打印缓存
                        
                        # 发送到TTS进行实时语音合成，使用静默模式
                        self.sdk.tts(
                            provider=tts_provider,
                            mode="speaker",
                            text=text_to_speak,
                            model=tts_model,
                            voice=voice,
                            **tts_kwargs  # 使用包含静默参数的kwargs
                        )
                    
                    # 重置累积内容
                    response_chunks = []
        
        # 处理剩余未播放的内容
        if response_chunks:
            text_to_speak = ''.join(response_chunks)
            if text_to_speak.strip():
                # 打印剩余内容
                if print_buffer:
                    print(f"🔊 {print_buffer}")
                    print_buffer = ""
                
                # 播放剩余内容
                self.sdk.tts(
                    provider=tts_provider,
                    mode="speaker",
                    text=text_to_speak,
                    model=tts_model,
                    voice=voice,
                    **tts_kwargs  # 使用包含静默参数的kwargs
                )
        
        return full_response 