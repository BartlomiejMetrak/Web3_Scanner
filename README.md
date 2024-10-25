# Web3Bots

- API Infura to api to wszystkich EVM compatible blockchainów czyli m.in. Ether, Base, Polgon, Arbitrum, Binance Smart Chain etc (ale bez Solany)
- API ehterscan to api to pobierania danych z blockchainu Ethereum - na początku można się na nim skupić, inny sensowny to w zasadzie Base i Solana
- Coingecko i Dexscreenr to dwa API do pobierania obecnych i historycznych cen, trzeba dopisać funkcje historyczne

Trzeba jeszcze zrobić klasę do łączenia się ze Coinmarket Cap - bo tam na DEX API można pobierać listę nowych tokenów zdaje się (ICO)

**Pomysły do zrobienia:**
- napisanie algorytmu który znajdowałby wspólne adresy wsród holderów różnych tokenów po określonych datach posiadania - to już zacząłem testować. Albo rozkminić jak inaczej możemy identyfikować adresy, które możą przynależeć do znanych kont na twitterze. Po identyfikacji takiego konta możemy śledzić nowe winestycje, które po publicznych postach na x.com zazwyczaj mocno zyskują. Do skanowania można rozminić jak dołączyć powiązane wallety (adresy). Niektórzy korzystają z kilku kont do zarządzania swoimi inwestycjami i regularnie przelewają kapitał z jednego na drugi.

- algorytm do skanowania adresów (ew. + powiązane adresy), które miały wysokie i regularne stopy zwrotu z inwestycji za ostatni okres i zapisanie ich do listy 'śledzonych walletów' - potem możemy sobie zrobić komunikator co edzie wysyłał sygnały o nowych inwestycjach. Mój pomysł jest taki, aby te adresy szukać po nowych ICO na DEXach i sprawdzać tylko te tokeny, które np mocno zyskały. Wtedy bierzemy holderów tych tokentów, którzy kupowali na samym początku po ICO i sprawdzamy czy ich pozstałe inwestycje były równie zyskowne. Jeśli tak to znaczy, że ten adres zaliczamy do grupy top picks i śledzimy jego kolejne inwestycje. 