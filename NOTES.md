# NOTES

> Uzupełnij krótko – wystarczą punkty. To dla nas punkt wyjścia do rozmowy.

## Jak uruchomić (jeśli coś zmieniłeś/aś)

-

## Przyczyna czerwonego testu

- Co było źle: cutoff był zapisany na sztywno jako `12:00 UTC`. To jest 14:00 w Warszawie
  tylko latem (UTC+2). Zimą (UTC+1) wychodziło 13:00, więc między 13:00 a 14:00 zamówienia
  były błędnie odrzucane.
- Dlaczego test to wyłapał: wszystkie pozostałe testy dotyczyły lipca, gdzie stała UTC akurat
  się zgadza. Tylko `test_winter_order_before_cutoff_is_accepted` (13:30 w styczniu) trafiał
  w to okno.
- Jak to naprawiłeś/aś: cutoff liczę jako `14:00` w strefie `Europe/Warsaw`
  (`datetime.combine(..., tzinfo=ZoneInfo("Europe/Warsaw"))`), a przesunięcie wylicza `zoneinfo`.
  Dopisałem testy brzegowe: granica zimą, ostatnia mikrosekunda, dni zmiany czasu (28.03 i
  31.10.2027), `now` podane w UTC oraz dostawa na dziś. Sprawdziłem też, że nowe testy padają
  na starej implementacji (4 czerwone), czyli faktycznie łapią ten błąd.

## Jak korzystałem/am z AI

- Narzędzia: Claude Code Opus 5.5
- Przykładowe prompty:
- „Przeczytaj README i kod szkieletu. Rozpisz plan całości: kolejność zadań, podział
  na commity i decyzje projektowe. Kodu jeszcze nie piszemy.”
- „Zmień model: sklep może złożyć kilka zamówień na ten sam dzień, bo może o czymś
  zapomnieć. Plan produkcji ma sumować wszystkie zamówienia z danego dnia.”
- „W planie produkcji pokazuj nieaktywne produkty tylko wtedy, gdy mają zamówienia
  na ten dzień, i dodaj sumę sztuk dla każdej kategorii.”
- „Frontend: lista produktów zostaje, plan produkcji i formularz zamówienia jako osobne
  podstrony (react-router). Formularz z cenami i sumą, po złożeniu zamówienia zostaje
  na stronie z linkiem do planu na ten dzień.”

## Co zweryfikowałem/am ręcznie

- Nowe testy cutoffu padają na starej implementacji czyli faktycznie łapią błąd.
- Tabele i ograniczenia w Postgresie (`\d orders`, `\d order_items`).
- `POST /orders` w Swaggerze: poprawne zamówienie, drugie na ten sam dzień, data dziś, nieaktywny produkt.
- Widok planu w przeglądarce: dzień z zamówieniami, dzień bez zamówień, ładowanie.
- Formularz zamówienia: pusty formularz, błąd z backendu, poprawne zamówienie i link do planu.

## Gdzie AI się pomyliło / co poprawiłem/am

- AI założyło jedno zamówienie na sklep na dzień zmieniłem, bo sklep może chcieć coś domówić.
- AI dopisało testy modelu, których README nie wymagało usunąłem, zostawiłem tylko potrzebne.
- AI dodawało w kodzie zbędne komentarze usunąłem je przed commitem.

## Co dalej przy większej ilości czasu

- Konta i role: sklep (składa zamówienia tylko dla siebie – `store_id` brany z konta,
  a nie z formularza), produkcja (widzi plan), admin (zarządza produktami i cenami).
- Edycja i anulowanie zamówienia do godziny cutoff.
- Testy na prawdziwym Postgresie zamiast SQLite.

