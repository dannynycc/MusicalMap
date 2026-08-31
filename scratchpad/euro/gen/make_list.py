# -*- coding: utf-8 -*-
"""建立歐陸原創 51 部的生成清單(身份釘死,不含劇情)+ kb_merge keymap。
劇名/人名保留原文變音符號 —— 冷門在地劇靠正確拼寫才搜得到。"""
import json, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PAIRS = [
 ["a christmas carol bit", "A Christmas Carol - Il Musical by Compagnia BIT (Italian original musical, original music and lyrics by Stefano Lori and Marco Caselle, book and direction by Melina Pellicano)"],
 ["alice nel paese delle meraviglie", "Alice nel Paese delle Meraviglie - Il Musical, the Italian-produced original musical touring Italian theatres (not the Disney film version)"],
 ["aggiungi un posto a tavola", "Aggiungi un posto a tavola, the Italian musical comedy by Garinei & Giovannini with music by Armando Trovajoli, premiered 1974"],
 ["belle e la bestia", "Belle e la Bestia - Il Musical by Compagnia dell'ORA, the Italian original musical with its own original score (not the Disney Beauty and the Beast)"],
 ["cera una volta scugnizzi", "C'era una volta... Scugnizzi, the Italian musical by Claudio Mattone (2001), staged at Teatro Sistina in Rome"],
 ["forza venite gente", "Forza Venite Gente, the 1981 Italian musical about Saint Francis of Assisi"],
 ["frida opera musical", "FRIDA Opera Musical by MIC International Company, written by Andrea Ortis and Gianmario Pagano, directed by Andrea Ortis"],
 ["gloria", "Gloria - Il Musical, the Italian jukebox musical comedy built on the songs of Umberto Tozzi"],
 ["il ragazzo dai pantaloni rosa", "Il ragazzo dai pantaloni rosa - Il Musical, the Italian jukebox musical written by Roberto Proia and directed by Massimo Romeo Piparo"],
 ["lupin", "LUPIN - Il Musical by Compagnia della Corona, original music by Paola Magnanini, book and direction by Salvatore Sito"],
 ["maradona el diego", "Maradona El Diego - Opera Musical, the Italian original musical with music by Marco Frisina and book by Gianmario Pagano"],
 ["michelangelo da caravaggio", "Michelangelo da Caravaggio - A Rebel Rock Musical, the Italian rock musical about the painter Caravaggio"],
 ["peter pan il musical bennato", "Peter Pan il Musical, the Italian musical with music by Edoardo Bennato, directed by Maurizio Colombi"],
 ["raffaella", "Raffaella il Musical, the Italian biographical musical about Raffaella Carrà, written and directed by Luciano Cannito, produced by Viola Produzioni"],
 ["win for life", "Win for life, the Italian musical comedy created by the group Oblivion and directed by Giorgio Gallione"],
 ["saturnin hybernia", "Saturnin, the new Czech original musical at Divadlo Hybernia with music by Roman Říčař, adapted and directed by Tomáš Dianiška, after Zdeněk Jirotka's novel"],
 ["vy nejste zena pane", "VY NEJSTE ŽENA, PANE!, the Czech original musical comedy written by Karel Janák, directed by Lukáš Burian at Divadlo Radka Brzobohatého"],
 ["zlatovlaska", "Zlatovláska, the Czech original fairy-tale musical with music by Angelo Michajlov at Hudební divadlo Karlín"],
 ["edudant a francimor", "Edudant a Francimor, the Czech family musical at Hudební divadlo Karlín after Karel Poláček's 1933 book"],
 ["carodejnice bordelina", "Čarodějnice Bordelína, the Czech children's musical after the book by Sandra Dražilová Zlámalová, directed by Milan Enčev at Divadlo Radka Brzobohatého"],
 ["rebelove karlin", "Rebelové, the Czech jukebox musical of 1960s Czech hits at Hudební divadlo Karlín, after Filip Renč's 2001 film"],
 ["andel pane karlin", "Anděl Páně, the Czech original musical comedy with music and lyrics by Ondřej G. Brzobohatý, directed by Martin Čičvák at Hudební divadlo Karlín"],
 ["mocal story", "Močál Story, the Czech musical comedy written and composed by Ivan Mládek, directed by Vilém Dubnička at Hudební divadlo Karlín"],
 ["kapka medu pro verunku", "Kapka medu pro Verunku, the Czech original family musical with libretto by Jan Pixa and Alena Pixová"],
 ["snowboardaci", "Snowboarďáci, the Czech original musical after Karel Janák's 2004 film, directed by Lukáš Burian at Divadlo Radka Brzobohatého"],
 ["a dzsungel konyve", "A dzsungel könyve, the Hungarian musical with music by Dés László, lyrics by Geszti Péter and book by Békés Pál, premiered 1996 at Pesti Színház"],
 ["a padlas", "A Padlás, the Hungarian musical with music by Presser Gábor, lyrics by Sztevanovity Dusán and book by Horváth Péter, premiered 1988 at Vígszínház"],
 ["macskafogo", "Macskafogó, the Hungarian musical at József Attila Színház after Béla Ternovszky's 1986 Hungarian animated film"],
 ["legy jo mindhalalig", "Légy jó mindhalálig, the Hungarian musical with music by Kocsák Tibor and book by Miklós Tibor, after Zsigmond Móricz's novel"],
 ["made in hungaria", "MADE IN HUNGÁRIA, the Hungarian rock jukebox musical built on Fenyő Miklós's songs"],
 ["a meseauto zenes vigjatek ket reszben", "A meseautó, the Hungarian musical comedy (zenés vígjáték) produced by Veres 1 Színház, after the 1934 Hungarian film Meseautó"],
 ["nikola tesla vegtelen energia", "Nikola Tesla - Végtelen energia, the Hungarian original musical with book by Egressy Zoltán, premiered 2020 in Pomáz"],
 ["a tron", "A TRÓN, the new Hungarian original musical about Hunyadi Mátyás, world premiere at Erkel Színház in Budapest"],
 ["mindig itt leszunk mohacs 500", "Mindig itt leszünk... Mohács 500, the Hungarian rock musical by Szomor György, world premiere 2026 in Mohács, produced by Budapesti Operettszínház"],
 ["hogyan tudnek elni nelkuled", "Hogyan tudnék élni nélküled?, the Hungarian jukebox musical built on Demjén Ferenc's songs, staged at Erkel Színház"],
 ["zrinyi 1566", "Zrínyi 1566, the Hungarian historical musical written by Moravetz Levente with music by Balásy Szabolcs, Horváth Krisztián and Papp Zoltán, premiered 2009 in Szigetvár"],
 ["elvalt nok klubja nyilvanos foproba", "Elvált nők klubja, the Hungarian musical comedy produced by Liliom Produkció, after Olivia Goldsmith's novel"],
 ["carmen", "Carmen, the Frank Wildhorn musical (music Frank Wildhorn, lyrics Jack Murphy, book Norman Allen), world premiere 2008 at the Karlín Musical Theatre in Prague"],
 ["metro", "Metro, the Polish musical with music by Janusz Stokłosa, book and lyrics by Agata and Maryna Miklaszewska, directed by Janusz Józefowicz at Teatr Studio Buffo"],
 ["polita", "POLITA, the Polish musical about Pola Negri by Janusz Józefowicz and Janusz Stokłosa at Teatr Studio Buffo in Warsaw"],
 ["musical 1989", "Musical 1989, the Polish rap musical with music by Andrzej Webber Mikosz and book and lyrics by Marcin Napiórkowski"],
 ["serce ze szka musical zen", "Serce ze szkła. Musical zen, the Polish experimental musical with libretto by Klaudia Hartung-Wójciak and Maria Peszek, directed by Cezary Tomaszewski at STUDIO teatrgaleria"],
 ["europavisjonar", "Europavisjonar, the Norwegian political satire musical by Simen Formo Hay, Johan Hveem Maurud and Oda Radoor, premiered 2025 at Det Norske Teatret"],
 ["anglagard", "Änglagård - The Musical, the Swedish musical after Colin Nutley's 1992 film, premiered at Oscarsteatern in Stockholm"],
 ["pippi pa sirkus", "Pippi på sirkus, the Swedish circus musical with music by Björn Ulvaeus, after Astrid Lindgren's Pippi Longstocking"],
 ["emil i lonneberga", "Emil i Lönneberga, the Swedish family musical after Astrid Lindgren's stories, staged at Intiman in Stockholm"],
 ["ronja rovardotter", "Ronja Rövardotter, the Swedish family musical with music by Björn Isfält, after Astrid Lindgren's novel"],
 ["sa som i himmelen", "Så som i himmelen, the Swedish musical created by Kay Pollak, Carin Pollak and Fredrik Kempe, after the 2004 Swedish film"],
 ["julekalender", "The Julekalender, the Danish Christmas musical by the comedy group De Nattergale, after their 1991 Danish TV series"],
 ["ternet ninja", "Ternet Ninja Live, the new Danish musical after Anders Matthesen's Ternet Ninja, adapted by Clemens Telling and directed by Sargun Oshana"],
 ["de spiekpietjes", "De Spiekpietjes, the Flemish (Belgian) children's musical about the Spiekpietjes, staged at Trixxo Theater in Hasselt"],
]

assert len(PAIRS) == 51, len(PAIRS)
here = os.path.dirname(os.path.abspath(__file__))
json.dump([p[1] for p in PAIRS], open(os.path.join(here, 'list.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([[g, t] for g, t in PAIRS], open(os.path.join(here, 'keymap.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('list.json / keymap.json ->', len(PAIRS), '部')
