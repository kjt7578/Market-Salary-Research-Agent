# Market Salary Agent v2 (Perplexity API 기반)

## 🧭 개요
- Perplexity AI API를 활용해 직무/경력/지역별 연봉 정보를 실시간으로 수집/정제/저장하는 CLI 툴입니다.
- 신뢰할 수 있는 출처(ZipRecruiter, Salary.com, Indeed, Levels.fyi)만 기반으로 결과를 요청합니다.
- 결과는 JSON으로 저장되며, 추후 Azure 업로드, AI 시스템 연동 등 확장 가능합니다.

## ⚙️ 설치 방법
1. Python 3.12 이상 설치
2. 프로젝트 디렉터리에서 아래 명령 실행
   ```bash
   pip install -r requirements.txt
   ```
3. `.env` 파일에 Perplexity API Key 입력
   ```env
   PERPLEXITY_API_KEY=여기에_발급받은_API_키_입력
   ```

## 🚀 실행 방법
```bash
python main.py
```
- 실행 후 직무/경력/지역을 입력하면, Perplexity API를 통해 연봉 정보를 받아와 data/ 폴더에 JSON으로 저장합니다.
- 결과는 콘솔에도 출력됩니다.

## 🗂️ 주요 파일 구조
```
Market_Salary_Agent_v2/
├── main.py                # CLI 진입점
├── config.py              # 신뢰 출처, 프롬프트 템플릿
├── models.py              # 데이터 모델
├── perplexity_api.py      # Perplexity API 호출/프롬프트 생성
├── parser.py              # 응답 파싱/예외처리
├── requirements.txt       # 의존성 패키지
├── .env                   # (직접 생성) API Key 저장
├── data/                  # 결과 JSON 저장 폴더
└── README.md              # 설명서
```

## 🔑 Perplexity API Key 발급/설정법
1. [perplexity.ai](https://www.perplexity.ai) 회원가입/로그인
2. Settings → API 탭에서 API Key 생성/복사
3. `.env` 파일에 아래처럼 입력
   ```env
   PERPLEXITY_API_KEY=발급받은_키
   ```

## 🧠 모델 설정법
- 기본값은 `sonar` 모델입니다.
- 필요시 `perplexity_api.py`의 `call_perplexity_api(prompt, model="sonar")`에서 모델명을 변경할 수 있습니다.
  - 예시: `sonar`, `sonar-reasoning`, `sonar-deep-research`

## 💡 확장성
- JD(직무기술서) 파싱, Azure Blob 업로드, AI 시스템 연동 등 손쉽게 확장 가능
- Perplexity API Key만 있으면 바로 실전 적용 가능

## 📝 참고/문의
- Perplexity API 공식 문서: https://docs.perplexity.ai
- 추가 문의/확장 요청은 언제든 환영합니다! 