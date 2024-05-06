LANGUAGES=$(find bot/locale -mindepth 1 -maxdepth 1 -type d -printf '%f\n')

for lang in $LANGUAGES
do
    echo "Compiling ${lang} translations..."
    msgfmt -o bot/locale/${lang}/LC_MESSAGES/bot.mo bot/locale/${lang}/LC_MESSAGES/bot.po
done

echo "Compilation finished."

#убедитесь, что у него есть права на выполнение chmod +x compile_translations.sh
#Запусьтите скрипт ./compile_translations.sh