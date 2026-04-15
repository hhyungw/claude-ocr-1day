# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 1. 언어 및 소통 원칙

- 기본 언어: 모든 응답은 한국어로 작성합니다.
- 전문 용어: 널리 통용되는 IT 전문 용어는 그대로 사용하되, 필요한 경우 괄호 안에 영문을 병기합니다.
  예: "생성형 AI(Generative AI)"
- 어조: 명확하고 간결하며 전문적인 어조를 유지합니다. 장황한 서술은 지양하고 핵심만 전달합니다.

## 2. 응답 형식

- 터미널 가독성을 위해 마크다운 문법을 적극 활용합니다.
- 코드나 명령어는 반드시 언어 태그가 포함된 코드 블록으로 제공합니다.
- 단계별 절차는 번호 목록으로 명확히 구분합니다.
- "요약해줘" 요청에는 핵심 정보만 글머리 기호로 정리합니다.

## 3. 작업 처리 지침

- 모호한 질문은 가장 가능성 높은 의도로 답변하고, 필요 시 추가 정보를 요청합니다.
- 작업 전 영향 범위(수정될 파일, 실행될 명령 등)를 먼저 설명합니다.

## 4. 위험 작업 처리

아래 작업은 반드시 실행 전 사용자에게 확인을 요청합니다.

- 파일 또는 디렉토리 삭제
- git force push / reset / rebase
- 환경 변수 또는 설정 파일 수정
- 패키지 전역 설치 또는 제거
- 데이터베이스 관련 작업

## 5. 코드 작업 원칙

- 파일 수정 전 현재 내용을 먼저 파악합니다.
- 변경 범위는 요청된 것에 한정하며, 불필요한 수정은 하지 않습니다.
- 수정 후 변경된 내용을 간략히 요약합니다.
- 테스트가 존재하면 수정 후 실행을 제안합니다.

---

## 6. 프로젝트 개요

영수증(이미지/PDF)을 업로드하면 **Upstage Vision LLM**이 자동으로 내용을 인식하여 구조화된 지출 데이터로 변환하고, 지출 내역을 조회·관리할 수 있는 경량 웹 애플리케이션입니다. DB 없이 JSON 파일 기반으로 운영합니다.

## 7. 기술 스택

| 구분 | 기술 |
|------|------|
| 프론트엔드 | React 18 + Vite 5 + TailwindCSS 3 + Axios |
| 백엔드 | Python FastAPI + LangChain + Upstage Vision LLM |
| OCR 모델 | `document-digitization-vision` (Upstage) |
| 데이터 저장 | `backend/data/expenses.json` (DB 미사용) |
| 배포 | Vercel (프론트 Static Build + 백엔드 Serverless) |

## 8. 디렉토리 구조

```
receipt-tracker/
├── frontend/
│   ├── src/
│   │   ├── pages/          # Dashboard, UploadPage, ExpenseDetail
│   │   ├── components/     # Header, Badge, Modal, Toast 등 공통 컴포넌트
│   │   └── api/            # Axios 인스턴스 및 API 호출 함수
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── main.py             # FastAPI 진입점
│   ├── routers/            # 라우터별 엔드포인트 분리
│   ├── services/           # LangChain + Upstage OCR 처리 로직
│   ├── data/
│   │   └── expenses.json   # 지출 데이터 영속 저장소
│   └── requirements.txt
├── components/             # (현재) 공통 컴포넌트 초기 작업 위치
├── vercel.json             # 프론트/백엔드 라우팅 설정
└── images/                 # 테스트용 영수증 샘플 이미지
```

## 9. 개발 명령어

### 프론트엔드 (frontend/)

```bash
npm install          # 의존성 설치
npm run dev          # 개발 서버 실행 (Vite, 기본 포트 5173)
npm run build        # 프로덕션 빌드
npm run preview      # 빌드 결과 로컬 미리보기
```

### 백엔드 (backend/)

```bash
pip install -r requirements.txt    # 의존성 설치
uvicorn main:app --reload          # 개발 서버 실행 (기본 포트 8000)
```

### 환경변수 설정

`.env` 파일에 아래 키를 설정합니다 (`.gitignore`에 포함됨):

```
UPSTAGE_API_KEY=<Upstage API 키>
VITE_API_BASE_URL=http://localhost:8000
DATA_FILE_PATH=./data/expenses.json
```

## 10. 시스템 아키텍처

```
브라우저 (React + Vite)
    │  HTTP REST
    ▼
FastAPI 백엔드
    ├── POST /api/upload  → LangChain → Upstage Vision LLM → expenses.json 저장
    ├── GET  /api/expenses?from=&to=  → expenses.json 읽기
    ├── DELETE /api/expenses/{id}
    ├── PUT    /api/expenses/{id}
    └── GET  /api/summary?month=
```

### LangChain OCR 처리 흐름

1. 업로드된 파일을 PIL(이미지) 또는 pdf2image(PDF)로 전처리 → Base64 인코딩
2. `ChatUpstage` Vision LLM 호출 (System Prompt: "JSON 형식으로만 응답")
3. LangChain Output Parser로 구조화 JSON 파싱
4. `expenses.json`에 append 저장

### expenses.json 스키마

```json
{
  "id": "uuid-v4",
  "created_at": "ISO8601",
  "store_name": "이마트 강남점",
  "receipt_date": "YYYY-MM-DD",
  "receipt_time": "HH:MM",
  "category": "식료품",
  "items": [{ "name": "", "quantity": 1, "unit_price": 0, "total_price": 0 }],
  "subtotal": 0,
  "discount": 0,
  "tax": 0,
  "total_amount": 0,
  "payment_method": "신용카드",
  "raw_image_path": "uploads/..."
}
```

## 11. Vercel 배포

```json
// vercel.json
{
  "builds": [
    { "src": "frontend/package.json", "use": "@vercel/static-build" },
    { "src": "backend/main.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "backend/main.py" },
    { "src": "/(.*)", "dest": "frontend/dist/$1" }
  ]
}
```

> **주의**: Vercel 서버리스는 요청마다 새 컨테이너로 실행되어 파일 시스템이 유지되지 않습니다.
> 데이터 영속성이 필요하면 `localStorage` 병행 저장, Railway/Render 배포, 또는 Vercel KV 사용을 검토하세요.
