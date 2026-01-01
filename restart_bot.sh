#!/bin/bash

echo "🛑 Останавливаем все запущенные боты..."
killall -9 Python 2>/dev/null
sleep 3

echo "🧹 Очищаем старые логи..."
rm -f bot.log

echo "🚀 Запускаем бота..."
nohup python3 -m bot.main > bot.log 2>&1 &
echo $! > bot.pid

sleep 3

echo "✅ Бот запущен! PID: $(cat bot.pid)"
echo ""
echo "📊 Статус:"
ps aux | grep "Python.*bot.main" | grep -v grep

echo ""
echo "📝 Последние логи:"
tail -10 bot.log

echo ""
echo "✅ Готово! Бот работает."
echo "📖 Смотреть логи: tail -f bot.log"
echo "🛑 Остановить: kill $(cat bot.pid)"
