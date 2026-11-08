# ScreenPen for Windows (윈도우용)

강의 및 발표 시 윈도우 화면 위에 바로 필기하고 주석을 남길 수 있는 가벼운 투명 오버레이 펜 도구입니다.

---

## ⚡ 빠른 실행 (Quick Start)

윈도우에는 기본적으로 Python 3 환경만 있으면 별도의 무거운 프레임워크 설치 없이 즉시 실행됩니다.

1. **저장소 다운로드 또는 클론**
   ```cmd
   git clone https://github.com/hyun2xyz/screenpen.git
   cd screenpen\windows
   ```

2. **실행**
   - `run_windows.bat` 파일을 더블클릭하거나,
   - 명령 프롬프트(CMD) / PowerShell에서 다음 명령어 실행:
     ```cmd
     py -3 screenpen_windows.py
     ```

---

## 🛠 단축키 및 사용법

앱을 실행하면 **ScreenPen 도구**와 **단축키 안내**가 나타납니다. 패널의 제목을 드래그해 옮기거나 `?` 버튼으로 단축키 안내를 접고 펼칠 수 있습니다. 펜과 형광펜을 선택한 뒤 아래의 색상 원을 클릭하면 다음 획부터 해당 색상이 적용됩니다.

아래 ScreenPen 단축키는 앱에 포커스가 있을 때 작동합니다. 마우스 모드에서는 툴바의 버튼으로 다시 필기를 시작할 수 있습니다.

| 기능 | 단축키 / 마우스 동작 | 설명 |
|---|---|---|
| **펜 (Pen)** | `Ctrl` + `Alt` + `1` | 선택한 색으로 화면에 필기 |
| **형광펜 (Highlighter)** | `Ctrl` + `Alt` + `2` | 선택한 색으로 굵게 강조 |
| **스포트라이트 (Spotlight)**| `Ctrl` + `Alt` + `3` | 마우스 주변 원형 하이라이트 포커스 |
| **지우개 (Eraser)** | `Ctrl` + `Alt` + `5` | 마우스 드래그 반경 내의 필기 삭제 |
| **되돌리기 (Undo)** | `Ctrl` + `Z` | 마지막 획 취소 |
| **전체 삭제 (Clear)** | `` Ctrl + Alt + ` `` | 화면의 모든 필기 즉시 삭제 |
| **단축키 안내** | `Ctrl` + `Alt` + `O` 또는 `?` | 단축키 패널 접기와 펼치기 |
| **화면 확대** | **화면 확대** 버튼 | Windows 돋보기 열기. `Win` + `Esc`로 돋보기 종료 |
| **확대 설정** | **확대 설정** 버튼 | Windows 돋보기 설정 열기 |
| **필기 모드 해제** | `Esc` 또는 **우클릭** | 화면 필기를 멈추고 일반 윈도우 클릭 모드로 복귀 |
| **앱 종료** | 툴바 우측 `✕` 버튼 | 오버레이 및 툴바 완전 종료 |

---

## 📦 단일 exe 실행 파일로 패키징하기 (선택 사항)

Python 설치가 없는 PC에서도 실행되도록 단일 실행 파일(`.exe`)을 만들고 싶다면 `PyInstaller`를 사용하세요:

```cmd
pip install pyinstaller
pyinstaller --noconsole --onefile windows/screenpen_windows.py -n ScreenPen
```
빌드가 완료되면 `dist/ScreenPen.exe` 파일 하나만 배포하여 더블클릭으로 바로 사용할 수 있습니다.
