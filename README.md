## Проектная работа по курсу "Инфраструктурная платформа на основе Kubernetes"
# Инфраструктурная Managed k8s платформа для корпоративного сервера NextCloud с онлайн-редактированием офисных документов
## Авторы: Уласевич Игорь, Лукша Павел

### Основные ссылки:
## https://project.retail-consult.by/ -- сервер NextCloud
## https://office-project.retail-consult.by/ -- сервер для онлайн-редактирования офисных документов
## https://argocd-project.retail-consult.by/ -- интерфейс argocd
## https://grafana-project.retail-consult.by/ -- grafana для анализа логов и мониторинга
## Данные для входа даны при сдаче проекта в кабинете студента

### Описание:
Проект представляет собой сервер Nextcloud с сервером онлайн редактирования документов OnlyOffice с полносью автоматическим разворачиванием.
Содержит в себе:
- Сервер NextCloud
- Ceрвер OnlyOffice
- Реплицируемая БД PerconaXtraDBCluster
- Сервер Memcached для кэширования файлов
- Сервер Redis для кэширования сессий
- Promtail для сбора логов
- Loki для хранения логов
- Prometheus для сбора метрик
- Grafana с дэшбордами для отображения логов и метрик
- Nginx ingress controller
- Agrocd для деплоя и CD

### Предварительные требования:
- В YandexCloud должен быть создан сервисный аккаунт k8s с ролями vpc.publicAdmin, container-registry.images.puller, k8s.cluster-api.cluster-admin, k8s.admin, load-balancer.admin, k8s.clusters.agent
- Нужно сгенерировать ключ доступа и авторизованный IAM ключ
- В secret CLOUD должен быть внесен id клауда YandexCloud
- В secret FOLDER должен быть внесен id директории YC, в которой нужно развернуть кластер
- В secret SECRET должен быть внесен IAM-ключ от YC
- В secret TLS_CRT должен быть внесен сертификат для TLS
- В secret TLS_KEY должен быть внесен ключ от сертификата
- В secret DB_PASS должен быть внесен пароль, который будет установлен как пароль ня БД, на вход в NextCloud и как JWT-токен от OnlyOffice
- В secret S3_BUCKET_LOKI должен быть внесен баккет для чанков локи
- В secret S3_BUCKET_NC должен быть внесен баккет для файлов пользователей из NC
- В secret S3_KEY должен быть внесен id ключа для доступа к S3 YC
- В secret S3_SECRET должен быть внесен секрет от ключа
- В s3 должны быть созданы баккеты, внесенные в S3_BUCKET_LOKI, S3_BUCKET_NC

### Как это работает:
Работает всё как с self-hosted раннером, так и с пустым ubuntu
При push или закрытии merge-request срабатывает github action, который запускает python-скрипт, который:
- Устанавливает Yandex-cli, если не установлен в раннере
- Подключается к YC с помощью ключа из секретов
- Проверяет, есть ли нужная сеть и подсеть, если нет, создаёт
- Проверяет, есть ли k8s кластер с именем из cluster.json, если нет, создаёт, если есть и остановлен, запускает
- Проверяет, созданы ли хосты в количестве из cluster.json, если нет, создаёт
- После того, как кластер создан и запущен, генерирует данные доступа к API
- Устанавливает kubectl, если не установлен в раннере
- Устанавливает helm, если не установлен в раннере
Дале запускается action, который:
- Создаёт необходимые namespace при их отсутствии
- Из secret-ов добавляет сертификат для TLS в namespace ingress-nginx (в самом nginx он настроен как default-сертификат)
- Добвляет кастомный error-page доя 404 и 503 ошибок
- Темплейт secrets.yaml заполняет из github-secrets чувствительными данными и применяет его, добавляя необходимые секреты в кластер
Далее запусается скрипт argocd.py, который:
- Проверяет, установлен ли argocd в кластере, если нет, добавляет репозиторий в helm и устанавливает
- Добавляет/обновляет корневое приложение в argocd, которое уже добавит все необходимые приложения из директории argo-apps этого же репозитория. Helm-values располагаются в директории values

  Разворачивание в пустой YandexCloud занимает 12+ минут на github-actions + 10+ минут на применение всего необходимого argocd.
  Всё, что нужно после окончания, на DNS-сервере обновить ip, полученный ingress-nginx, и в настройках NextCloud указать адрес и JWT токен onlyoffice для онлайн редактирования документов
  
![1](https://github.com/user-attachments/assets/30594b61-e0a7-4232-8f8f-6c67aca0538b)

![2](https://github.com/user-attachments/assets/5edf46c9-2a75-4bc3-af1b-fb09d331e14d)

![3](https://github.com/user-attachments/assets/10c3d39b-3964-40f2-81fe-b7c55c3923b8)

![4](https://github.com/user-attachments/assets/ba647bab-09c1-4815-a6f1-c36ffc8ce4a9)

![5](https://github.com/user-attachments/assets/c5c649d5-d910-491c-86d2-2d0fd9e1cb38)

![6](https://github.com/user-attachments/assets/babf2b76-d309-4d40-a1a7-1e5d4dc8e26a)

![7](https://github.com/user-attachments/assets/ae50254b-3c2c-4b3c-89d3-0bb41f15ac9d)
