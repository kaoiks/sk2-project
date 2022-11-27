Jakub Witczak 148151
Jakub Żytliński 148140

Opis projektu
Wisielec


Po uruchomieniu klienta gracz podaje swój nick. Jeżeli nie trwa gra, to gracz trafia do lobby.
Aby wystartować grę, przynajmniej dwóch graczy w lobby musi zaznaczyć gotowość.

Jeżeli aktualnie trwa gra, gracz oczekuje w lobby na zakończenie trwającej rozgrywki.

Po starcie rozgrywki serwer losuje hasło z puli.

Gracze mają po 11 żyć. Przy każdej źle zgadniętej literce gracz traci jedno życie. Gracz widzi ile liter ma odgadywane hasło. Gracze widzą ilość żyć swoich przeciwników.

Gracze otrzymują punkty za każdą rozgrywkę w zależności od kolejności w jakiej odgadną hasło, im szybciej tym więcej punktów (pierwszy otrzymuje n-1, drugi n-2, itd., gdzie n to liczba graczy w rozgrywce). Ostatni gracz oraz gracze którzy nie odgadli hasła dostają po 0 punktów.

Każda gra składa się z 5 rund. Każda runda ma limit czasowy, który wynosi 100 sekund. Gracze, którzy stracili wszystkie życia widzą rozszyfrowane hasło, w momencie gdy wszyscy gracze zakończą rundę lub skończy się czas. Jeżeli w grze zostanie jeden gracz, wówczas dostaje on informację, że wygrał i rozgrywka zostaje zakończona. Gracze na bieżąco widzą ranking graczy z punktami, włączając w to też graczy którzy rozłączyli się z gry.
