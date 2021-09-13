# Автобусы на карте Москвы

Веб-приложение показывает передвижение автобусов на карте Москвы.

<img src="https://user-images.githubusercontent.com/14781165/133058947-22a6b51e-8ec5-4742-a8f2-2cea92ea0046.gif">

## Клиентская часть
### Как запустить

- Скачайте код
- Откройте в браузере файл index.html


### Настройки

Внизу справа на странице можно включить отладочный режим логгирования и указать нестандартный адрес веб-сокета.

<img src="https://user-images.githubusercontent.com/14781165/133058912-b4f740f3-ef91-4015-a457-f0a2532f7353.png">

Настройки сохраняются в Local Storage браузера и не пропадают после обновления страницы. Чтобы сбросить настройки удалите ключи из Local Storage с помощью Chrome Dev Tools —> Вкладка Application —> Local Storage.

Если что-то работает не так, как ожидалось, то начните с включения отладочного режима логгирования.

### Формат данных

Фронтенд ожидает получить от сервера JSON сообщение со списком автобусов:

```js
{
  "msgType": "Buses",
  "buses": [
    {"busId": "c790сс", "lat": 55.7500, "lng": 37.600, "route": "120"},
    {"busId": "a134aa", "lat": 55.7494, "lng": 37.621, "route": "670к"},
  ]
}
```

Те автобусы, что не попали в список `buses` последнего сообщения от сервера будут удалены с карты.

Фронтенд отслеживает перемещение пользователя по карте и отправляет на сервер новые координаты окна:

```js
{
  "msgType": "newBounds",
  "data": {
    "east_lng": 37.65563964843751,
    "north_lat": 55.77367652953477,
    "south_lat": 55.72628839374007,
    "west_lng": 37.54440307617188,
  },
}
```



### Используемые библиотеки

- [Leaflet](https://leafletjs.com/) — отрисовка карты
- [loglevel](https://www.npmjs.com/package/loglevel) для логгирования

## Серверная часть
## Как запустить

- Скачайте код
- Создайте виртуальное окружение ```python3 -m venv venv```
- Активируйте виртуальное окружение ```source venv/bin/activate```
- Установить зависимости ```pip install -r requirements.txt```
- Запустите сервер ```python server.py```
- Запустите генератор данных ```python fake_bus.py```
- Откройте в браузере файл `index.html`


## Настройки
  Описание параметров можно увидеть запустив `server.py --help` или `fake_bus.py --help` соответственно.
## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
