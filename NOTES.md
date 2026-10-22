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

- Narzędzia:
- Przykładowe prompty:

## Co zweryfikowałem/am ręcznie

-

## Gdzie AI się pomyliło / co poprawiłem/am

-

## Co dalej przy większej ilości czasu

-
