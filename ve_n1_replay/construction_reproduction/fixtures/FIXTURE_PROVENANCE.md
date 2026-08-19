# Provenance — fixtures de sub acest director

Copii exacte, byte-cu-byte, ale fișierelor deja publicate (NEsigilate) pe branch-ul
`statistician-foundation`. Niciun fișier de aici conține bare OHLC reale — doar structură deja
publicată (clasă/interval/nivel/adnotări de preț aproximative unde există). Verificat separat
(v. `CONSTRUCTION_REPRODUCTION_README.md`) că barele OHLC reale ale celor 48 de ferestre rămân
în escrow, în afara oricărui checkout Git, inaccesibile aici.

| fișier local | sursă (`statistician-foundation`) | commit sursă | SHA-256 (copia locală) |
|---|---|---|---|
| `LEVEL_MAPPING.md` | `statistician/BLIND_BATCH_02_LEVEL_MAPPING.md` | `5a9d5ec0cb27dbb778aa3eddfee063eea249f7fd` | `1e390ca858d162c72a0f3284b6007eaadb9d62d3b2786f0aefd3b50e869367fd` |
| `PART1_LOCKED_LABELS.json` | `statistician/RANGE_V3_BLIND_BATCH_02_PART1_LOCKED_LABELS.json` | `b29a14553230360beb940b049f2bdfea60a9b22a` | `fd3b4b49403a7585e1c740290349363304eaa8434381cc7869dfe5fdf5608ed5` |
| `PART2_LOCKED_LABELS.json` | `statistician/RANGE_V3_BLIND_BATCH_02_PART2_LOCKED_LABELS.json` | `b29a14553230360beb940b049f2bdfea60a9b22a` | `24708a30b4fe9cc5b3c22aad5c28b8323668f9c9d6898d9051f247eb7295f182` |
| `PART3_PROVISIONAL_LABELS.json` | `statistician/RANGE_V3_BLIND_BATCH_02_PART3_PROVISIONAL_LABELS.json` | `b29a14553230360beb940b049f2bdfea60a9b22a` | `e2a48eec99ff590e1236a03621f04e39f1c6ec7cc81f450950881eddc4c2641d` |
| `PART4_PROVISIONAL_LABELS.json` | `statistician/RANGE_V3_BLIND_BATCH_02_PART4_PROVISIONAL_LABELS.json` | `b29a14553230360beb940b049f2bdfea60a9b22a` | `e77abb89e93e942e15caea4b91c4097e18f4c2abf31d6d6e4cf5cab51e8e8b35` |
| `CORRECTION_ADDENDUM_046_048.md` | `statistician/RANGE_V3_BLIND_BATCH_02_CORRECTION_ADDENDUM_046_048.md` | `ba8b59ae072d0381d64eaed89ab5da36834eca74` | `2b2960f81485af5cf26bf175db36f23f5ff7839ff76b48604bb3588cf9c057a4` |

Re-verificabil oricând: `git show <commit sursă>:<cale statistician-foundation> \| sha256sum`.

Copiate aici EXACT pentru a elimina dependența de o citire cross-branch la momentul reproducerii
(§12 mandat: "Niciun rezultat declarat nu poate depinde de un script local necomis" — un `git show`
împotriva unei ramuri care ar putea, teoretic, fi ștearsă/rescrisă local e mai fragil decât un
fișier comis direct în arborele acestui commit).
