
<b>Простенький бот для проверки в сети ли пользователь ВКонтакте</b>

1. Установить библеотеки, открыть консоль в папке и прописать pip install -r requirements.txt 
2. Открыть config.py через любой редактор, прописать BotFather (токен бота), vk_api (токен вк), указать ID админов (https://t.me/FIND_MY_ID_BOT)
3. Запустить main.py, python main.py


Установка на хостинг

1. Покупаем вдс/впc хостинг, ставим ubuntu 20.04 - 22.04 - 18.04
2. Заходим на хост и прописываем все команды по порядку

- sudo apt update 
- sudo apt install sqlite3 
- sudo apt install nodejs (необязательно, для использования демонизатора)
- sudo apt install npm (необязательно, для использования демонизатора)
- npm install pm2 -g (необязательно, для использования демонизатора)
- sudo apt install python3 
- sudo apt-get install python3-pip 
- sudo pip3 install Aiogram 
- sudo pip3 install aiohttp 
- sudo pip3 install unzip

3) После установки создаем папку bot (mkdir bot), заливаем архив со скриптом и распаковываем (unzip имя_архива.zip)
4) Запускаем скрипт любой из команд:
pm2 start main.py --interpreter=python3 - запуск в демонизаторе pm2 (Чтобы скрипт не падал в случае ошибки, также можно смотреть логи - pm2 logs)
python3 main.py - обычный запуск
