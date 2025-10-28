# GPT-5 Guida pratica

VINCENZO COSENZA
Guida pratica
a GPT-5
vincos.itScrivere prompt
per il nuovo
ChatGPT

Indice
Le novità di GPT-5
PromptingContext Window01
050302
0604Livelli di sforzo
FrameworkLimiti d’utilizzo 
07 Next

A circa 3 anni dal lancio di ChatGPT (modello GPT-3.5), OpenAI ha
rilasciato una nuova versione, che introduce sostanziali novità e richiede
un approccio diverso al prompting. In questa guida ho racchiuso alcuni
consigli frutto della mia esperienza e della documentazione esistente. Le novità di GPT-5
Un sistema unificato
Questo nuovo modello, per la prima volta, è in grado di comprendere la
nostra richiesta e decidere autonomamente se rispondere velocemente
oppure se “riflettere” più a lungo, valutando diverse alternative, per poi
risponderci. In pratica la nostra richiesta viene inviata ad un sistema di
smistamento (router) che decide se dev’essere gestita da un modello di
reasoning o meno. 
Finora i modelli di reasoning - o1, o3, o4-mini - erano selezionabili
all’occorrenza dall’utente per le questioni più complesse. Ora, questi
vecchi modelli sono scomparsi (ma gli utenti paganti possono riattivarli
scegliendo l’opzione apposita dalle Impostazioni). 
💡 È importante sapere che il router viene continuamente addestrato per
migliorare il suo comportamento sulla base del comportamento
dell’utente (in che occasione decidiamo di cambiare modello oppure in
base alle valutazioni che diamo alle risposte ottenute).
Un modello migliore
GPT‑5 ovviamente è migliore dei modelli precedenti e ciò emerge dai
benchmark condotti dall’azienda e da terze parti. 
Le sue risposte sono più rapide, ma soprattutto fa meno errori. Incorre
meno nelle cosiddette “allucinazioni”. 
Soprattutto, è in grado di seguire meglio le istruzioni dell’utente e le sue
risposte sono meno accondiscendenti (fenomeno detto sycophancy).
Questo si riflette in una capacità di scrittura più naturale e fluida, che
può essere molto utile per la creazione di testi di vario genere.
Anche per gli sviluppatori ci sono miglioramenti nello sviluppo di codice
front-end e nel debugging di ampi repository.

La nuova versione di ChatGPT ha una nuova interfaccia con un selettore
dei modelli meno affollato rispetto al passato. Aprendolo, dal menu in
alto a sinistra, troveremo meno modelli tra cui scegliere, ognuno dei
quali è caratterizzato da un diverso livello di “sforzo cognitivo”.Livelli di sforzo 
AUTO
L’opzione selezionata di default è “Auto”. In questo caso è il sistema
che sceglie autonomamente la quantità di sforzo da applicare all’attività
che gli abbiamo chiesto di svolgere. Se gli facciamo una domanda a cui
può rispondere attingendo alla sua base di conoscenza, ci risponderà
velocemente, usando un modello “non-reasoning”. Se, al contrario, gli
chiediamo di risolvere un problema complesso, il router sceglierà di
attivare un modello reasoning con un livello di sforzo adeguato a darci la
risposta corretta e quindi impiegherà più tempo. 
Mentre il sistema ci risponde potremo vedere cosa sta facendo (in
realtà, vedremo un riassunto del suo modo di “ragionare”) e decidere di
optare per una risposta più rapida (cliccando su “Salta”).
INSTANT
Scegliendo l’opzione “Instant” dal menu a tendina, diremo chiaramente
al sistema che abbiamo bisogno di una risposta più rapida possibile. 
Quindi va usata quando sappiamo che stiamo richiedendo una risposta
semplice che può essere recuperata dai dati di addestramento. Per
esempio, se chiediamo “parlami della rivoluzione francese”.
THINKING MINI
Se si seleziona l’opzione “Thinking Mini” il sistema attiverà il modello di
reasoning, ma con uno sforzo cognitivo basso. In questo modo bilancerà
la velocità d’inferenza con la profondità della risposta. 

Da un punto di vista tecnico, quello che succede nel back-end del
sistema è che verrà applicato un cosiddetto “Juice Number” basso (un
numero da 1 a 200 che corrisponde allo sforzo di ragionamento,
probabilmente 16). Queste informazioni tecniche non sono state
esplicitate, ma da alcuni test sembra plausibile ipotizzarlo.
Quindi questa selezione va usata quando pensiamo che la nostra
domanda richieda un po’ di riflessione in più. Ad esempio, “Stendi un
piano editoriale mensile che sia originale e che non ripeta i copy già
usati in quello che ti allego”.  
THINKING
Scegliendo l’opzione “Thinking” dal menu a tendina, esprimeremo la
volontà di accedere al modello di reasoning con un livello cognitivo
significativo. In questo caso, è probabile che il “Juice Number” applicato
sarà 64 o giù di lì.
Questa selezione va usata quando crediamo che la nostra richiesta
meriti un ragionamento approfondito. Ad esempio, quando chiediamo
attività complesse di scrittura di codice o che richiedono più passaggi
per essere portate a termine efficacemente. 
PRO
Gli abbonati alla versione Pro di ChatGPT possono accedere anche
all’opzione “Thinking Pro”. In questo caso, si attiverà GPT-5 con il più
alto sforzo cognitivo possibile, corrispondente ad un “Juice Number” di
200. 
Questa selezione è molto utile per attività di coding, di strategia,
compiti che hanno elementi di ambiguità e che richiedono più tempo di
ragionamento. Ad esempio “Fai una revisione tecnica di sicurezza del
mio codice, individuando minacce e possibili mitigazioni del rischio”
oppure “Confronta questi 10 studi e costruisci una posizione
argomentata, evidenziando limiti e incertezze”.

La "context window" (spesso tradotta come finestra di contesto) di un
Large Language Model (LLM) indica la quantità massima di testo (input e
output combinati) che il modello può "tenere a mente" e usare per
generare risposte in un’unica interazione.
L’ampiezza della finestra di contesto non è misurata in parole, ma in
token (unità linguistiche che possono corrispondere a parole intere,
parti di parola o simboli). Un token può corrispondere, a seconda della
lingua, a 0,7-0,8 parole.
Per calcolare il raggiungimento del limite viene usato sia il numero di
token sfruttato dall’utente per scrivere il prompt, sia quello che il
modello genera per la risposta.  
In pratica, più è ampia la context window che il sistema ci mette a
disposizione, più lungo e complesso può essere il testo che il modello è
in grado di elaborare (per esempio, analizzare interi documenti allegati,
mantenere coerenza in lunghe conversazioni, fare ragionamenti più
articolati).
💡 In ChatGPT la context window messa a disposizione da OpenAI varia:
Per i modelli Fast:
gli utenti Free hanno una finestra di 16.000 token (~12.000 parole)
gli utenti Plus e Team di 32.000 token (~24.000 parole)
gli utenti Pro ed Enterprise di 128.000 token (~96.000 parole)
Per i modelli Thinking
tutti gli utenti paganti hanno una finestra di contesto che arriva a
196.000 token (~147.000 parole).
Chi necessita “di più spazio” può optare per Google Gemini che riesce a
gestire 1 milione di token.Context Window

OpenAI ha deciso di applicare dei limiti all’utilizzo delle diverse opzioni
appena analizzate. Ovviamente per minimizzare il costo associato ai
differenti livelli di ragionamento perché più è elevato, maggiore sarà
l’utilizzo delle risorse computazionali dei loro  server. Ad agosto 2025 i
limiti sono quelli descritti di seguito.  Limiti d’utilizzo
UTENTI FREE
Gli utenti che non hanno sottoscritto un abbonamento a ChatGPT
possono usare GPT-5 ma soltanto nella sua versione “Auto”. Quindi sarà
il modello a decidere il tipo di sforzo cognitivo da applicare, in base al
prompt.
Il limite è di 10 prompt ogni 5 ore. Dopo 10 richieste il sistema userà un
modello mini (non è chiaro quali siano le sue caratteristiche).  
ABBONATI PLUS
Coloro che hanno sottoscritto un abbonamento Plus da €23 al mese,
avranno la possibilità di selezionare anche le varianti Instant, Thinking
Mini e Thinking. Con la sola esclusione della Pro.
Il limite d’uso di GPT-5 è di 160 messaggi ogni 3 ore. Dopo, la chat
userà un modello mini.  
C’è poi un limite di 3000 messaggi a settimana per l’uso del modello
“Thinking” (quando selezionato dall’utente). Se, invece, sarà il sistema
ad attivarlo automaticamente, non conterà per il raggiungimento del
limite settimanale.
ABBONATI TEAM (BUSINESS) E PRO
Gli utenti con un abbonamento a ChatGPT Team da €29 al mese e Pro da
€229 al mese possono usare GPT-5 senza limiti.

Il modello GPT-5 è molto diverso dai precedenti. Non è stato progettato
per essere esclusivamente conversazionale, ma per essere la base di
“agenti” ossia software che non si limitano a rispondere alle richieste,
ma che riescono a portare a termine attività complesse, usando non solo
la base di conoscenza su cui sono stati addestrati, ma anche strumenti
esterni. Questo perché lo stesso ChatGPT sta diventando sempre più un
agente, più o meno autonomo (si pensi alla “modalità Agente” che è solo
un assaggio di quello che vedremo nei prossimi anni).
E siccome i sistemi agentivi sono sviluppati per seguire catene di
istruzioni ben strutturate, GPT-5 è un modello pensato per essere
particolarmente sensibile ai prompt che scriviamo. Va da sé che la
scrittura del prompt può essere determinante per ottenere un risultato
ottimale.
 Prom pting
Errori da evitare
Prima di vedere quale dovrebbe essere la struttura ideale di un prompt,
passiamo in rassegna alcuni errori da evitare nella sua scrittura:
Prompt vaghi: evita domande molto aperte o istruzioni poco precise; 
Linguaggio ambiguo: non usare parole gergali o ambigue che
rischiano di non essere interpretate come si vorrebbe;
Prompt overload: non scrivere prompt che contengono troppe
informazioni non strutturare e pieni di dettagli non necessari.
Potrebbero confondere il sistema sui termini cui porre attenzione per
assolvere al compito assegnato.

RuoloSpulciando i documenti pubblicati OpenAI, destinati principalmente agli
sviluppatori che useranno GPT-5 attraverso le API per sviluppare i propri
software, ho estrapolato alcune linee guida per la struttura da dare ai
prompt per il nuovo ChatGPT.
Anche se ho effettivamente notato che un prompt ben strutturato è
molto più efficace di uno improvvisato, interiorizzare un framework è
importante soprattutto per valorizzare il nostro ruolo di guida della
macchina.
Ecco gli elementi che dovrebbe contenere un prompt ben strutturato:Framework
Ruolo: assegnare un ruolo specifico al
chatbot gli permette di individuare
meglio la parte di knowledge base a
cui attingere
Obiettivo: specificare apertamente
cosa vogliamo ottenere dal compito
assegnato
Istruzioni: dettagliare quali fasi
operative ci aspettiamo che compia il
sistema  
Contesto: indicare tutte le informazioni
necessarie all’espletamento
dell’attività (background, target,
esempi, tono/stile) 
Output: esplicitare il formato della
risposta (es. una tabella, un elenco,
xls, csv, json)
Obiettivo
Istruzioni
Contesto
Output

Questa struttura non è rigida, ma può essere adattata alle proprie
esigenze. Il consiglio è quello di fare dei test su casi concreti.
Ad esempio, il ruolo e l’output non sono sempre essenziali ai fini del
risultato. A volte il ruolo può essere agevolmente inferito dal contesto e
l’output può essere indifferente per l’utente. Decidi caso per caso.
Tra i vincoli si possono specificare diversi
elementi: 
Verbosità: è un parametro che usando
le API può essere impostato su livelli
specifici (low, medium, high). Nel
prompt per ChatGPT possiamo essere
più liberi nella spiegazione del livello di
prolissità del il sistema deve avere
Stile: serve ad imporre uno stile di
scrittura specifico al chatbot. Es:
linguaggio corporate, informale,
tecnico, forbito, ecc. 
Formato: definisce il formato
dell’output. Come visto, può essere
oggetto di una sezione specifica. INDICAZIONI AGGIUNTIVE
Inoltre GPT-5 è in grado di recepire anche informazioni sui vincoli, che si
possono usare all’occorrenza. I vincoli potrebbero essere compresi tra
le Istruzioni oppure inseriti separtamente per una maggiore chiarezza.
Verbosità
Stile
FormatoVincoliUn accorgimento molto importante per ottenere risposte coerenti è
quello di aggiungere esempi di output e materiali a supporto. Il modo
migliore per farlo è caricando degli allegati. 

Riflessione
Pianificazione
Validazione
RevisioneCompiti complessi
Se l’attività da far svolgere al sistema è complicata o richiede più fasi, si
dovrebbero aggiungere altre istruzioni:
Ragionamento pre-esecuzione: è un
modo per forzare il modello a
“riflettere” meglio sul compito affidato.
Es: "Prima di cominciare, spiegami cosa
hai capito del compito affidato e
l’approccio che seguirai” 
Pianificazione: così si induce il chatbot
a stilare un piano preciso delle sue
azioni. Es: "Crea un piano dettagliato del
tuo operato con i sotto-task identificati” 
Controlli di validazione: è utile per
spingere il modello a procedere
gradualmente effettuando dei controlli.
Es: "Dopo ogni fase principale, verifica
che i risultati siano in linea con le
specifiche date” 
Revisione post-esecuzione: è un modo
per far controllare la correttezza
dell’attività svolta e definire una
condizione di conclusione del processo.
Es: "Prima di concludere, accertati che
tutti gli obiettivi sono stati raggiunti” 

PROMPT SEMPLICEEsempio 1
Scrivi 3 social post per Instagram per promuovere un caffè monorigine etiope, esaltandone il suo
profilo floreale. 
PROMPT STRUTTURATO
#Ruolo
Sei un copywriter esperto. 
#Obiettivo
Devi aiutarmi a promuovere un caffè monorigine etiope, esaltandone il suo profilo floreale 
#Istruzioni
Il tuo compito è di produrre 3 social post per Instagram. Ognuno di essi deve:
Avere un titolo in grado di catturare l’attenzione 
Avere un corpo di testo di massimo 100 parole
Enfatizzare le note floreali del caffè etiope
Essere scritto in un linguaggio originale e sofisticato (no scelte stilistiche banali o stereotipate) 
#Contesto
Il prodotto da promuovere è un caffè monorigine etiope tostato dall’azienda Gardelli di Forlì, tra le
prime in Italia a proporre specialty coffee.
Il target è composto da appassionati di specialty coffee.
#Output
Usa una formattazione markdown

PROMPT SEMPLICEEsempio 2
Cerca tutte le informazioni più aggiornate sul mercato dei prodotti bio in Italia
PROMPT STRUTTURATO
# Obiettivo
Fornire tutte le informazioni più aggiornate riguardanti il mercato dei prodotti biologici in Italia.
# Istruzioni
Ricercare e presentare dati recenti, tendenze, normative, e principali attori del mercato bio italiano.
Priorità ad affidabilità e attualità delle fonti.
# Checklist
Inizia con una checklist concisa (3-7 punti) sui sottotask che svolgerai; mantieni la lista a livello
concettuale.
# Contesto
Focus sul settore dei prodotti biologici (alimentari e non).
Escludere mercati esteri e prodotti non certificati bio.
# Processo e Verifica
Prima di ogni ricerca o estrazione dati da fonti, esplicita in una riga la finalità e gli input essenziali della
ricerca.
Dopo ogni raccolta o sintesi di informazioni, valida in 1-2 frasi l'affidabilità e la rilevanza dei dati individuati
e procedi oppure autocorreggi in caso di mancata aggiornatezza o coerenza.
# Output
Struttura la risposta in paragrafi tematici; presenta dati e riferimenti rilevanti in elenchi puntati o tabelle
dove utile.
# Verbosità
Sintesi esaustiva, con linguaggio tecnico ma accessibile.
# Condizioni di Conclusione e Autonomia
Termina quando l'insieme delle informazioni richieste risulta completo e aggiornato.
Procedi autonomamente a meno che non manchino elementi essenziali; in caso di gap irrisolvibili,
chiedi chiarimenti prima di proseguire.

Next
SCOPRI  TUTTI  I  CORSIVuoi approfondire?
Se questa guida ti ha fatto sorgere il desiderio di approfondire, ho un
corso di formazione specifico su ChatGPT & C. pensato per marketer e
non.
Ne ho anche altri progettati per chi vuole imparare a generare immagini,
video e progettare agenti IA. Sono già stati seguiti da oltre 700 persone.  
Si tratta di corsi pratici che si svolgono online, in diretta web, per
garantire uno scambio di conoscenze immediato e utile. Quelli per
aziende possono essere svolti anche in sede.
Cercami
Il mio sito 
La mia newsletter 
I miei tutorial su YouTube 
Il mio profilo LinkedIn

VINCOS.ITImmagini e testi: Vincenzo Cosenza 
Pubblicazione: agosto 2025