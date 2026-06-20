const $ = (id) => document.getElementById(id);

const state = {
  n: 0n,
  phi: 0n,
  e: 0n,
  d: 0n,
  logGen: '',
  logE: '',
  logD: '',
  encryptionTrace: []
};

function showMessage(title, body) {
  $('modalTitle').textContent = title;
  $('modalBody').textContent = body;
  $('modal').showModal();
}

function isPrime(num) {
  if (num < 2n) return false;
  if (num === 2n) return true;
  if (num % 2n === 0n) return false;
  for (let i = 3n; i * i <= num; i += 2n) {
    if (num % i === 0n) return false;
  }
  return true;
}

function gcd(a, b) {
  while (b !== 0n) {
    const temp = b;
    b = a % b;
    a = temp;
  }
  return a < 0n ? -a : a;
}

function extendedGcd(a, b) {
  if (a === 0n) return [b, 0n, 1n];
  const [g, x1, y1] = extendedGcd(b % a, a);
  const x = y1 - (b / a) * x1;
  const y = x1;
  return [g, x, y];
}

function modInverse(e, phi) {
  const [g, x] = extendedGcd(e, phi);
  if (g !== 1n) return null;
  return ((x % phi) + phi) % phi;
}

function modPow(base, exponent, modulus) {
  if (modulus === 1n) return 0n;
  let result = 1n;
  base = base % modulus;
  while (exponent > 0n) {
    if (exponent % 2n === 1n) result = (result * base) % modulus;
    exponent = exponent / 2n;
    base = (base * base) % modulus;
  }
  return result;
}

function updateConsole() {
  $('console').textContent = state.logGen + state.logE + state.logD || '> Esperando generación de claves...';
}

function randomPrime(min, max) {
  while (true) {
    const num = BigInt(Math.floor(Math.random() * (max - min + 1)) + min);
    if (isPrime(num)) return num;
  }
}

function generateRandomPrimes() {
  let p = randomPrime(50, 500);
  let q = randomPrime(50, 500);
  while (p === q) q = randomPrime(50, 500);
  $('p').value = p.toString();
  $('q').value = q.toString();
}

function generateKeys() {
  try {
    const pText = $('p').value.trim();
    const qText = $('q').value.trim();

    if (!pText || !qText) {
      showMessage('Atención', 'Ingresa ambos números primos.');
      return;
    }

    const p = BigInt(pText);
    const q = BigInt(qText);

    if (!isPrime(p) || !isPrime(q)) {
      showMessage('Error', 'Ambos números deben ser primos válidos.');
      return;
    }

    if (p === q) {
      showMessage('Error', 'p y q deben ser números primos diferentes.');
      return;
    }

    const n = p * q;
    const phi = (p - 1n) * (q - 1n);
    state.n = n;
    state.phi = phi;

    const possibleE = [];
    for (let i = 3n; i < phi; i += 2n) {
      if (gcd(i, phi) === 1n) possibleE.push(i);
      if (possibleE.length >= 20) break;
    }

    if (possibleE.length === 0) {
      showMessage('Error', "No se encontró un exponente 'e' válido.");
      return;
    }

    state.logGen =
      `> Iniciando generación de claves ...\n\n` +
      `> Cálculo de n:\n  ${p} * ${q} = ${n}\n\n` +
      `> Función totiente de Euler φ(n):\n  (${p}-1) * (${q}-1) = ${phi}\n\n` +
      `> Posibles valores de e determinados:\n${possibleE.join(', ')}...\n\n`;
    state.logE = '';
    state.logD = '';
    updateConsole();

    $('nLabel').textContent = `Módulo (n): ${n}`;
    $('phiLabel').textContent = `Euler φ(n): ${phi}`;

    if (n < 1000n) {
      $('securityLabel').textContent = 'Seguridad: Muy Débil 🔴';
      $('securityLabel').style.color = '#ef4444';
    } else if (n < 50000n) {
      $('securityLabel').textContent = 'Seguridad: Moderada 🟡';
      $('securityLabel').style.color = '#f59e0b';
    } else {
      $('securityLabel').textContent = 'Seguridad: Fuerte 🟢';
      $('securityLabel').style.color = '#10b981';
    }

    const selectE = $('selectE');
    selectE.innerHTML = '';
    possibleE.forEach((value) => {
      const option = document.createElement('option');
      option.value = value.toString();
      option.textContent = value.toString();
      selectE.appendChild(option);
    });
    selectE.disabled = false;
    onESelect();
  } catch {
    showMessage('Error', 'Por favor ingresa únicamente números enteros.');
  }
}

function onESelect() {
  if (!state.phi) return;
  const e = BigInt($('selectE').value);

  state.logE =
    `> Selección del exponente público e: ${e}\n\n` +
    `> Determinación de d mediante Algoritmo Extendido de Euclides...\n\n`;

  const d0 = modInverse(e, state.phi);
  if (d0 === null) return;

  const possibleD = [];
  for (let k = 0n; k < 5n; k++) possibleD.push(d0 + k * state.phi);

  state.logE += `> Posibles valores de d determinados:\n${possibleD.join(', ')}\n\n`;
  state.logD = '';
  updateConsole();

  const selectD = $('selectD');
  selectD.innerHTML = '';
  possibleD.forEach((value) => {
    const option = document.createElement('option');
    option.value = value.toString();
    option.textContent = value.toString();
    selectD.appendChild(option);
  });
  selectD.disabled = false;
  onDSelect();
}

function onDSelect() {
  const e = BigInt($('selectE').value);
  const d = BigInt($('selectD').value);
  state.e = e;
  state.d = d;

  state.logD = `> Selección de la clave privada d: ${d}\n\n`;
  updateConsole();

  $('eLabel').textContent = `Pública (e): ${e}`;
  $('dLabel').textContent = `Privada (d): ${d}`;
  $('nInput').value = state.n.toString();
  $('dInput').value = d.toString();
}

function generateSpyMessage() {
  const messages = [
    'El águila ha aterrizado en el nido.',
    'Nos vemos en el punto de extracción a las 0400.',
    'El paquete fue entregado sin contratiempos.',
    'Abortar misión. Repito, abortar misión.',
    'La llave está debajo de la maceta azul.',
    "Operación 'Sombra Nocturna' iniciada."
  ];
  $('plainText').value = messages[Math.floor(Math.random() * messages.length)];
}

function encryptMessage() {
  const text = $('plainText').value;

  if (!text) {
    showMessage('Atención', 'Ingresa un mensaje para cifrar.');
    return;
  }

  if (state.n === 0n) {
    showMessage('Atención', 'Primero debes generar el par de claves en el Paso 1.');
    return;
  }

  state.encryptionTrace = [];
  const cipherArray = [];

  for (const char of text) {
    const m = BigInt(char.codePointAt(0));
    if (m >= state.n) {
      showMessage(
        'Error Matemático de RSA',
        `El código del carácter '${char}' (${m}) es mayor o igual al módulo n (${state.n}).\nRSA requiere que el tamaño del bloque sea estrictamente menor que el módulo.\n¡Usa números primos más grandes!`
      );
      return;
    }

    const c = modPow(m, state.e, state.n);
    cipherArray.push(c.toString());
    state.encryptionTrace.push({ char, m, eq: `${m}^${state.e} mod ${state.n}`, c });
  }

  const cipherText = cipherArray.join(',');
  $('cipherOut').value = cipherText;
  $('cipherIn').value = cipherText;
}

function decryptMessage() {
  const cipherText = $('cipherIn').value.trim();

  if (!cipherText) {
    showMessage('Atención', 'No hay criptograma para descifrar.');
    return;
  }

  try {
    const d = BigInt($('dInput').value.trim());
    const n = BigInt($('nInput').value.trim());
    const codes = cipherText.split(',');
    let plain = '';

    for (const code of codes) {
      const cleanCode = code.trim();
      if (!cleanCode) continue;
      const c = BigInt(cleanCode);
      const m = modPow(c, d, n);
      plain += String.fromCodePoint(Number(m));
    }

    $('plainOut').value = plain;
  } catch (err) {
    showMessage('Error de Descifrado', `Ha ocurrido un error:\n${err.message}`);
  }
}

async function copyText(text) {
  if (!text.trim()) return;
  try {
    await navigator.clipboard.writeText(text);
    showMessage('Copiado', 'Texto copiado al portapapeles exitosamente.');
  } catch {
    showMessage('Atención', 'No se pudo copiar automáticamente. Selecciona el texto y cópialo manualmente.');
  }
}

function saveToFile() {
  const cipherText = $('cipherOut').value.trim();
  if (!cipherText) {
    showMessage('Atención', 'No hay ningún mensaje cifrado para guardar.');
    return;
  }

  const content =
    `--- MENSAJE CIFRADO (CRIPTOGRAMA) ---\n` +
    `${cipherText}\n\n` +
    `--- CLAVE PRIVADA PARA DESCIFRAR ---\n` +
    `Módulo (n): ${state.n}\n` +
    `Clave Privada (d): ${state.d}\n`;

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'criptograma_rsa.txt';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function loadFromFile(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = () => {
    const content = reader.result;
    const cipherMatch = content.match(/--- MENSAJE CIFRADO \(CRIPTOGRAMA\) ---\n([\s\S]*?)\n\n---/);
    const nMatch = content.match(/Módulo \(n\):\s*(\d+)/);
    const dMatch = content.match(/Clave Privada \(d\):\s*(\d+)/);

    if (cipherMatch) $('cipherIn').value = cipherMatch[1].trim();
    if (nMatch) $('nInput').value = nMatch[1];
    if (dMatch) $('dInput').value = dMatch[1];

    showMessage('Éxito', 'Archivo cargado correctamente.');
  };
  reader.onerror = () => showMessage('Error', 'No se pudo leer el archivo.');
  reader.readAsText(file, 'UTF-8');
}

function showCalculations() {
  if (!state.encryptionTrace.length) {
    showMessage('Atención', 'Primero cifra un mensaje para ver los cálculos.');
    return;
  }

  const lines = state.encryptionTrace.map((item) => {
    return `Carácter: ${item.char}\nASCII/Unicode: ${item.m}\nOperación: ${item.eq}\nResultado cifrado: ${item.c}`;
  });

  showMessage('Cálculos del cifrado', lines.join('\n\n--------------------\n\n'));
}

$('themeBtn').addEventListener('click', () => {
  document.body.classList.toggle('light');
  $('themeBtn').textContent = document.body.classList.contains('light') ? '☾' : '☼';
});

$('autoPrimes').addEventListener('click', generateRandomPrimes);
$('generateKeys').addEventListener('click', generateKeys);
$('selectE').addEventListener('change', onESelect);
$('selectD').addEventListener('change', onDSelect);
$('spyMessage').addEventListener('click', generateSpyMessage);
$('encrypt').addEventListener('click', encryptMessage);
$('decrypt').addEventListener('click', decryptMessage);
$('copyCipher').addEventListener('click', () => copyText($('cipherOut').value));
$('copyPlain').addEventListener('click', () => copyText($('plainOut').value));
$('saveFile').addEventListener('click', saveToFile);
$('loadFile').addEventListener('change', loadFromFile);
$('showCalc').addEventListener('click', showCalculations);
$('closeModal').addEventListener('click', () => $('modal').close());
