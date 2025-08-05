# EC2 Shutdown AMI Automation

## 개요

이 프로젝트는 EC2 인스턴스가 중지(stop) 상태가 되었을 때 자동으로 해당 인스턴스로부터 AMI를 생성하고, SNS를 통해 알림을 발송하려 한다. AWS Lambda와 EventBridge를 기반으로 구현된 자동화 솔루션이다.

## 배경 및 목적

EC2 인스턴스는 특정 가용영역(AZ)에 종속되는 리소스다. 반면 AMI는 리전 레벨에서 관리되므로, 동일한 리전 내 어떤 AZ에서든 동일한 환경의 인스턴스를 재생성할 수 있다.

Auto Scaling이나 예약 인스턴스 스케줄링 과정에서 인스턴스가 정지될 때, 예기치 못한 재생성 실패나 용량 부족으로 인해 다른 AZ 또는 리전으로 이전해야 하는 상황에 대비하여 AMI를 미리 생성해두려 한다.

## 아키텍처

이 시스템은 다음과 같은 구성요소들로 이루어져 있다:

- **EventBridge Rule**: EC2 인스턴스 상태 변경 이벤트 중 "stopped" 상태를 감지한다
- **Lambda Function**: 이벤트를 받아 AMI를 생성하고 SNS 알림을 발송한다
- **IAM Roles**: Lambda가 필요한 AWS 서비스에 접근할 수 있도록 권한을 부여한다
- **SNS Topic**: AMI 생성 완료 알림을 발송한다

## 디렉토리 구조

```
ec2-shutdown-ami/
├── lambda/
│   └── create_ami_on_ec2_shutdown.py    # Lambda 함수 소스코드
├── iam/
│   ├── lambda-execution-role.json       # Lambda 실행 역할 정책
│   └── eventbridge-role.json            # EventBridge 역할 정책
└── README.md
```

## 주요 기능

### AMI 자동 생성
- EC2 인스턴스가 중지되면 즉시 AMI를 생성한다
- AMI 이름은 `AutoBackup-{인스턴스ID}-{타임스탬프}` 형식으로 자동 생성된다
- `NoReboot=True` 옵션을 사용하여 인스턴스를 재부팅하지 않고 AMI를 생성한다

### 알림 시스템
- AMI 생성이 완료되면 SNS를 통해 알림을 발송한다
- 알림에는 인스턴스 ID, 중지 시각, 생성된 AMI ID 정보가 포함된다
- 시간은 KST(한국 표준시)로 표시된다

### 권한 관리
- Lambda 함수는 최소 권한 원칙에 따라 필요한 권한만 부여받는다
- EC2 AMI 생성, SNS 발송, CloudWatch 로그 작성 권한을 포함한다

## 설정 요구사항

### 환경변수
Lambda 함수에 다음 환경변수를 설정해야 한다:
- `SNS_TOPIC_ARN`: 알림을 발송할 SNS 토픽의 ARN

### EventBridge 규칙
다음 이벤트 패턴으로 EventBridge 규칙을 설정한다:
```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["stopped"]
  }
}
```

## 주의사항

- 이 시스템은 인스턴스 중지(stop) 이벤트만 처리한다
- 인스턴스 종료(terminate) 이벤트는 제외되어 있다
- AMI 생성 시 추가 비용이 발생할 수 있다
- 생성된 AMI는 별도로 관리 및 삭제해야 한다
