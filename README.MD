### 환경 설정
```
pip install -r requirements.txt
```

## AWS EC2 Ubuntu 서버 설정 방법
### 업비트 API 허용 IP 설정
[업비트 API 홈페이지](https://upbit.com/mypage/open_api_management)

### 기본 세팅
- 한국 기준으로 서버 시간 설정
```
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
```
- 패키지 목록 업데이트
```
sudo apt update
```
- 패키지 목록 업그레이드
```
sudo apt upgrade
```
- python 버전 확인하기
```
python3 --version
```
- pip3 설치
```
sudo apt install python3-pip
```
### 레포지토리 가져오기
```
git clone https://github.com/youtube-jocoding/gpt-bitcoin.git
```
### 서버에서 라이브러리 설치
```
pip3 install -r requirements.txt
```
```
pip3 install --break-system-packages -r requirements.txt
```
### .env 파일 만들고 API KEY 넣기
```
vim .env
```
### 명령어
- 현재 경로 상세 출력
```
ls -al
```
- 경로 이동
```
cd 경로
```
- vim 에디터로 파일 열기
```
vim autotrade.py
```
- vim 에디터 입력: i
- vim 에디터 저장: ESC + wq!
### 실행하기
- 그냥 실행
```
python3 autotrade.py
```
만약 numpy관련 에러가 난다면 아래 명령을 실행한다.
```
pip3 install --break-system-packages numpy==1.26.4
```
- 백그라운드 실행
```
nohup python3 -u autotrade.py > output.log 2>&1 &
```
- 로그 보기
```
cat output.log
tail -f output.log
```
- 실행 확인
```
ps ax | grep .py
```
- 종료하기
```
kill -9 PID
ex. kill -9 13586
```