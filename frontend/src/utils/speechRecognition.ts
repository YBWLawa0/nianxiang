/**
 * 语音识别工具类
 * 使用浏览器原生 Web Speech API
 */

export interface SpeechRecognitionOptions {
  lang?: string
  continuous?: boolean
  interimResults?: boolean
  maxAlternatives?: number
}

export interface SpeechRecognitionEvents {
  onResult: (transcript: string, isFinal: boolean) => void
  onError: (error: string) => void
  onStart: () => void
  onEnd: () => void
}

export class SpeechRecognitionManager {
  private recognition: any = null
  private isSupported: boolean = false
  private events: SpeechRecognitionEvents
  private timer: number | null = null
  private maxDuration: number = 60000 // 60秒

  constructor(events: SpeechRecognitionEvents, options?: SpeechRecognitionOptions) {
    this.events = events

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

    if (!SpeechRecognition) {
      this.isSupported = false
      return
    }

    this.isSupported = true
    this.recognition = new SpeechRecognition()

    this.recognition.continuous = options?.continuous ?? true
    this.recognition.interimResults = options?.interimResults ?? true
    this.recognition.maxAlternatives = options?.maxAlternatives ?? 1

    this.setupEventHandlers()
  }

  private setupEventHandlers(): void {
    if (!this.recognition) return

    this.recognition.onresult = (event: any) => {
      let transcript = ''
      let isFinal = false

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        transcript += result[0].transcript
        if (result.isFinal) {
          isFinal = true
        }
      }

      this.events.onResult(transcript, isFinal)

      if (isFinal) {
        ;(this as any).finalTranscript = transcript
      }
    }

    this.recognition.onerror = (event: any) => {
      let errorMessage = '识别失败，请重试'

      switch (event.error) {
        case 'no-speech':
          errorMessage = '未检测到语音，请重试'
          break
        case 'audio-capture':
          errorMessage = '未找到麦克风设备'
          break
        case 'not-allowed':
          errorMessage = '请允许麦克风权限'
          break
        case 'network':
          errorMessage = '网络连接失败'
          break
        case 'aborted':
          return
      }

      this.events.onError(errorMessage)
    }

    this.recognition.onstart = () => {
      this.events.onStart()
    }

    this.recognition.onend = () => {
      this.stopTimer()
      this.events.onEnd()
    }
  }

  private startTimer(): void {
    this.stopTimer()
    this.timer = window.setTimeout(() => {
      this.stop()
      this.events.onError('说话时间过长，已自动停止')
    }, this.maxDuration)
  }

  private stopTimer(): void {
    if (this.timer) {
      clearTimeout(this.timer)
      this.timer = null
    }
  }

  start(): void {
    if (!this.isSupported) {
      this.events.onError('当前浏览器不支持语音输入')
      return
    }

    this.stopTimer()

    try {
      this.recognition.start()
      this.startTimer()
    } catch (error: any) {
      if (error.message?.includes('already started')) {
        // ignore
      } else {
        this.events.onError('启动语音识别失败')
      }
    }
  }

  stop(): void {
    this.stopTimer()

    if (this.recognition) {
      try {
        this.recognition.stop()
      } catch {
        // ignore
      }
    }
  }

  abort(): void {
    this.stopTimer()

    if (this.recognition) {
      try {
        this.recognition.abort()
      } catch {
        // ignore
      }
    }
  }

  get supported(): boolean {
    return this.isSupported
  }
}

export function isSpeechRecognitionSupported(): boolean {
  return !!(window as any).SpeechRecognition || !!(window as any).webkitSpeechRecognition
}

export async function requestMicrophonePermission(): Promise<boolean> {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    stream.getTracks().forEach((track) => track.stop())
    return true
  } catch {
    return false
  }
}
