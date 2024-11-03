# Агент обучения моделей

## Запуск
Процесс запуска агента ничем не отличаеться от стандартного: 
- собираем kb
- запускаем сервер
- запускаем ostis-web

Далее переходим в остис, находим start_train_fnn_agent и мы должны увидеть такой формат.

![start_train_fnn_agent](https://i.imgur.com/bLJDNe1.jpeg)

У вас не будет нод:
- action_train_fnn
- question
- question_initiated

Поэтому для запуска вам надо их добавить и синхронизировать с бз.

### После этого в консоли мы должны увидеть процесс обучения в консоли
![start_train_fnn_agent](https://i.imgur.com/NA36SGc.jpeg)