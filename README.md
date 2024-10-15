<h1>Чат бот для получения курса валют</h1>
<h2>Задание</h2>
<p>Напишите простой чат-бот в Телеграм, который при присоединении говорит "Добрый день. Как вас зовут?", 
  берет ответ как имя и сообщает, например: "Рад знакомству, Алексей!. Курс доллара сегодня 100р", беря котировку
из любого открытого источника. Используйте бесплатные решения, их достаточно. Опишите:</p>
<p>* Технологии, которые использовали.</p>
<p>* Встретившиеся проблемы и пути их решения.</p>
<p>* Ссылку в телеграм на вашего бота.</p>

<h2>Использованные технологии</h2>
<p>Для написания бота использовался фреймворк aiogram.</p>
<p>Для get запроса использовалась библиотека requests</p>
<p>Для взаимодействия с .env файлом использовалась библиотека dotenv</p>
<p>Также для работы с бд использовалась библиотека sqlite3</p>
<h2>Встретившиеся проблемы и пути их решения</h2>

<p>✅ Первым делом надо было выбрать ресурс, из которого получать данные о курсе валют. Был выбран сайт центробанка и проект cbr-xml-daily.ru, который позволяет простым get запросом получить курсы валют. Однако на этом ресурсе есть ограничение на частоту и количество запросов. Это решалось хранением данных о курсах валют в файле на своём сервере и обновлением его каждые 20 секунд, что не нарушает правил пользования сервисом.</p>
<p>✅ Во время работы столкнулся с проблемой параллельного запуска самого бота и процесса, отправляющего запрос на получение курсов валют. В итоге была выбрана простая реализация с бесконечным циклом с интервалами в 20 секунд, поскольку использовать планировщик нет особого смысла, сайт центробанка часто выкладывает ежедневный курс с большой погрешностью.</p>
<p>✅ Требовалось спросить пользователя о его имени, а потом ответить, обращаясь по нему. Для принятия имени и ответа с обращением по этому имени использовалась машина состояний.</p>
<p>✅ Также я решил добавить базу данных, которая хранила бы данные о пользователяь, и каждый раз для того, чтоб сообщить курс валют не приходилось спрашивать имя.</p>
<p>✅ Также, делая задатки для дальнейшего развития, если база данных даёт сбой, программа может выполнять определённые функции без доступа к ней. В дальнейшем это помогло бы не полностью останавливать работу программы, а разделить действия на те, что требуют авторизации и те, что не требуют.</p>
<p>✅ Если из-за какой-то ошибки пользователь по команде /start не был зарегистрирован, то при отсутствии ошибок работы бд бот после каждого сообщения будет предлагать зарегистрироваться.</p>
<p>✅ Также возникла мысль о том, что ограничить пользователю возможность менять имя. Точнее, чтоб он не мог делать это чащей, чем раз в 10 минут. Для этого в бд созраняется время последнего обновления имени, а при попытке изменить имя это значение сравнивается с настоящим временем.</p>

<h2>Ссылка на бота в телеграм</h2>
<p>https://t.me/Tosha84_bot</p>
